{
  description = "Simple npm+python environment";

  # nixpkgs, flake-utils and poetry2nix stay indirect (resolved from the
  # registry, pinned by flake.lock) - the app's toolchain is validated against
  # those revisions, npmDepsHash included, and is deliberately not disturbed.
  #
  # The container's OS comes from a current nixpkgs instead, because the LXC
  # image plumbing the cattle module needs is newer than that pin. Mixing is
  # fine: the app packages are self-contained closures wherever they are built.
  inputs.nixpkgs-lxc.url = "github:NixOS/nixpkgs/nixos-26.05";
  inputs.cattle.url = "git+https://github.com/charlesbaynham/nix-proxmox-cattle?ref=v1";

  outputs = { self, nixpkgs, flake-utils, poetry2nix, nixpkgs-lxc, cattle }:
    let
      lxcSystem = "x86_64-linux";
      wurwolvesModule = import ./nix/wurwolves.nix;

      perSystem = flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv;

        pythonEnv = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
        };

        # What the deployed container needs, and deliberately free of pytest,
        # selenium and ipython.
        runtimeEnv = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
          groups = [ ];
        };

        reqs = with pkgs; [
          pkgs.nodejs
          pkgs.poetry
          pythonEnv
          pkgs.pre-commit
          pkgs.black
          pkgs.caddy
          pkgs.ruby # For pre-commit FIX-ME hook
        ];

        frontendBuild = pkgs.buildNpmPackage rec {
          pname = "wurwolves";
          version = "0.0.0";
          src = ./react-ui;
          npmDepsHash = "sha256-Tvnkw0TOx4bdstfXzRO5LGjJXAetFAzZjkPIh8FbSJk=";
          installPhase = ''
            mkdir $out
            cp -a build/. $out
          '';
        };

        frontendBuildWithCaddy = pkgs.stdenv.mkDerivation {
          name = "wurwolves-with-caddy";
          src = frontendBuild;
          installPhase = ''
            mkdir $out
            mkdir $out/result
            cp "${./Caddyfile}" $out/Caddyfile
            cp -a $src/. $out/result
          '';
        };

        frontendApp =
          let
            inputs = [
              pkgs.caddy
            ];
          in
          (
            flake-utils.lib.mkApp
              {
                drv = (pkgs.writeShellScriptBin "script" ''
                  export PATH=${pkgs.lib.makeBinPath inputs}:$PATH
                  cd ${frontendBuildWithCaddy}

                  exec caddy run
                '');
              }
          );

        backendApp =
          flake-utils.lib.mkApp
            {
              drv = (pkgs.writeShellScriptBin "script" ''
                export PATH=${pkgs.lib.makeBinPath [ pythonEnv ]}:$PATH

                # Add this flake to python path, but let the local directory take priority
                export PYTHONPATH=${self}:$PYTHONPATH

                python -m backend.reset_db && true
                exec python -m uvicorn backend.main:app --host 0.0.0.0
              '');
            };

        loadDocker = flake-utils.lib.mkApp
          {
            drv = (pkgs.writeShellScriptBin "script" ''
              nix build .#dockerFrontend
              export IMG_ID=$(docker load -i result | sed -nr 's/^Loaded image: (.*)$/\1/p' | xargs -I{} docker image ls "{}" --format="{{.ID}}")
              docker tag $IMG_ID wurwolves-frontend:latest

              nix build .#dockerBackend
              export IMG_ID=$(docker load -i result | sed -nr 's/^Loaded image: (.*)$/\1/p' | xargs -I{} docker image ls "{}" --format="{{.ID}}")
              docker tag $IMG_ID wurwolves-backend:latest
            '');
          };


      in
      {
        devShell =
          pkgs.mkShell {
            name = "devShell";
            buildInputs = reqs;
          };

        apps = {
          inherit loadDocker;
          default = loadDocker;
          frontend = frontendApp;
          backend = backendApp;
        };

        packages = {
          inherit frontendBuild frontendBuildWithCaddy runtimeEnv;
          default = frontendBuild;
          dockerFrontend = pkgs.dockerTools.buildLayeredImage {
            name = "wurwolves-frontend";
            created = "now";
            config = {
              Cmd = [ frontendApp.program ];
              ExposedPorts = {
                "80/tcp" = { };
                "443/tcp" = { };
              };
              Env = [ "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt" ];
            };
          };
          dockerBackend = pkgs.dockerTools.buildLayeredImage {
            name = "wurwolves-backend";
            created = "now";
            config = {
              Cmd = [ backendApp.program ];
              WorkingDir = "/data";
              Volumes = { "/data" = { }; };
            };
          };
        };
      }
    );

      # `.#proxmoxLxcTemplate` is the rootfs tarball Proxmox takes as a CT
      # template. Everything generic about being a cattle container comes from
      # nix-proxmox-cattle; only the app wiring is here.
      lxcTemplate = cattle.lib.mkTemplate {
        nixpkgs = nixpkgs-lxc;
        name = "wurwolves";
        system = lxcSystem;
        stateDir = "/data";
        modules = [
          wurwolvesModule
          {
            services.wurwolves = {
              enable = true;
              backend = perSystem.packages.${lxcSystem}.runtimeEnv;
              frontend = perSystem.packages.${lxcSystem}.frontendBuild;
              source = self;
            };
          }
        ];
      };
    in
    nixpkgs.lib.recursiveUpdate perSystem
      (lxcTemplate // { nixosModules.wurwolves = wurwolvesModule; });
}
