{
  description = "Simple npm+python environment";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv;

        pythonEnv = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
        };

        reqs = with pkgs; [
          pkgs.nodejs
          pythonEnv
          pkgs.pre-commit
          pkgs.black
          pkgs.caddy
          pkgs.ruby  # For pre-commit FIX-ME hook
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

        # backendApp =
        #   let
        #     python = pkgs.python3.withPackages (ps: pythonReqs ++ [ backendPackage ]);
        #   in
        #   flake-utils.lib.mkApp
        #     {
        #       drv = (pkgs.writeShellScriptBin "script" ''
        #         export PATH=${pkgs.lib.makeBinPath [ python ]}:$PATH

        #         python -m backend.reset_db && true
        #         exec python -m uvicorn backend.main:app --host 0.0.0.0
        #       '');
        #     };

        # loadDocker = flake-utils.lib.mkApp
        #   {
        #     drv = (pkgs.writeShellScriptBin "script" ''
        #       nix build .#dockerFrontend
        #       export IMG_ID=$(docker load -i result | sed -nr 's/^Loaded image: (.*)$/\1/p' | xargs -I{} docker image ls "{}" --format="{{.ID}}")
        #       docker tag $IMG_ID streetfight-frontend:latest

        #       nix build .#dockerBackend
        #       export IMG_ID=$(docker load -i result | sed -nr 's/^Loaded image: (.*)$/\1/p' | xargs -I{} docker image ls "{}" --format="{{.ID}}")
        #       docker tag $IMG_ID streetfight-backend:latest
        #     '');
        #   };


      in
      {
        devShell =
          pkgs.mkShell {
            name = "devShell";
            buildInputs = reqs;
          };

        # apps = {
        #   inherit loadDocker;
        #   default = loadDocker;
        #   frontend = frontendApp;
        #   backend = backendApp;
        # };

        packages = {
          inherit frontendBuild frontendBuildWithCaddy;
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
          # dockerBackend = pkgs.dockerTools.buildLayeredImage {
          #   name = "wurwolves-backend";
          #   created = "now";
          #   config = {
          #     Cmd = [ backendApp.program ];
          #     WorkingDir = "/data";
          #     Volumes = { "/data" = { }; };
          #   };
          # };
        };
      }
    );
}
