# NixOS module for the Wurwolves game server.
#
# It describes the service only and knows nothing about Proxmox or LXC, so it
# can equally be imported into a VM or a bare-metal host. Everything the service
# writes lives under `stateDir`, which under the cattle deployment model is a
# mountpoint rather than part of the rootfs.
{ config, lib, pkgs, ... }:

let
  cfg = config.services.wurwolves;

  # SessionMiddleware signs the cookie that carries a player's identity, so
  # anyone holding the key can forge any player's session — and in this game a
  # session *is* your secret role. It used to be a constant in main.py, which
  # meant everyone had it.
  preflight = pkgs.writeShellScript "wurwolves-preflight" ''
    set -u
    if [ -z "''${SECRET_KEY:-}" ]; then
      echo "wurwolves: SECRET_KEY is not set. It must be defined in ${cfg.environmentFile}." >&2
      exit 1
    fi
    if [ "$SECRET_KEY" = "not-so-secret" ]; then
      echo "wurwolves: SECRET_KEY is still the placeholder from .env.dev, which is public." >&2
      exit 1
    fi
  '';
in
{
  options.services.wurwolves = {
    enable = lib.mkEnableOption "the Wurwolves game server";

    backend = lib.mkOption {
      type = lib.types.package;
      description = "Python environment carrying the backend's runtime dependencies. Must provide `bin/python`.";
    };

    frontend = lib.mkOption {
      type = lib.types.package;
      description = "Built React frontend, served as static files by Caddy.";
    };

    source = lib.mkOption {
      type = lib.types.path;
      description = ''
        Repository root, placed on PYTHONPATH so `backend` is importable. The
        backend is not packaged as a distribution; this mirrors how the flake's
        `backend` app runs it.
      '';
    };

    stateDir = lib.mkOption {
      type = lib.types.path;
      default = "/data";
      description = ''
        Directory holding everything that must survive container replacement.
        Expected to be a mountpoint declared outside this flake; the cattle
        module refuses to finish booting if it is not one.
      '';
    };

    port = lib.mkOption {
      type = lib.types.port;
      default = 80;
      description = "Port Caddy listens on. TLS is terminated upstream, so this is plain HTTP.";
    };

    backendPort = lib.mkOption {
      type = lib.types.port;
      default = 8000;
      description = "Loopback port the FastAPI backend listens on.";
    };

    logLevel = lib.mkOption {
      type = lib.types.str;
      default = "INFO";
      description = "Level for the Python logging module. Note capitals.";
    };

    environmentFile = lib.mkOption {
      type = lib.types.path;
      default = "${cfg.stateDir}/secrets/wurwolves.env";
      defaultText = lib.literalExpression ''"''${config.services.wurwolves.stateDir}/secrets/wurwolves.env"'';
      description = ''
        systemd EnvironmentFile supplying SECRET_KEY. It lives on the persistent
        mountpoint rather than in the rootfs, so it survives replacement. The
        unit refuses to start without it.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    users.users.wurwolves = {
      isSystemUser = true;
      group = "wurwolves";
      home = cfg.stateDir;
      description = "Wurwolves game server";
    };
    users.groups.wurwolves = { };

    # The mountpoint itself is created by Proxmox; these are the directories
    # inside it that the service expects.
    systemd.tmpfiles.rules = [
      "d ${cfg.stateDir}         0750 wurwolves wurwolves -"
      "d ${cfg.stateDir}/db      0750 wurwolves wurwolves -"
      "d ${cfg.stateDir}/secrets 0700 wurwolves wurwolves -"
    ];

    systemd.services.wurwolves-backend = {
      description = "Wurwolves backend (FastAPI)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        # Four slashes total: sqlite:/// plus an absolute path.
        DATABASE_URL = "sqlite:///${cfg.stateDir}/db/wurwolves.db";
        PYTHONPATH = "${cfg.source}";
        LOG_LEVEL = cfg.logLevel;
        PYTHONUNBUFFERED = "1";
      };

      serviceConfig = {
        User = "wurwolves";
        Group = "wurwolves";
        WorkingDirectory = cfg.stateDir;
        # Leading "-" so a missing file is not a systemd-level load failure: the
        # unit still refuses to start, but the preflight below is what reports
        # it, and it can say which variable is wanted and where.
        EnvironmentFile = "-${cfg.environmentFile}";
        # reset_db drops and recreates the schema when it no longer matches the
        # models, which is how this app has always migrated. Games are transient
        # by nature, so losing them on a schema change is expected.
        ExecStartPre = [
          preflight
          "${cfg.backend}/bin/python -m backend.reset_db"
        ];
        ExecStart = "${cfg.backend}/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port ${toString cfg.backendPort}";
        Restart = "always";
        RestartSec = 5;

        # The security boundary for this estate is the border router, not the
        # service container, so this is modest hardening rather than a sandbox.
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [ cfg.stateDir ];
      };
    };

    services.caddy = {
      enable = true;
      # Mirrors the repo's Caddyfile, minus the TLS handling: the border router
      # terminates TLS, so Caddy's data and config directories carry nothing
      # worth persisting and stay in the disposable rootfs.
      virtualHosts.":${toString cfg.port}".extraConfig = ''
        handle /api/* {
          reverse_proxy 127.0.0.1:${toString cfg.backendPort}
        }

        handle /docs* {
          reverse_proxy 127.0.0.1:${toString cfg.backendPort}
        }

        handle /openapi.json {
          reverse_proxy 127.0.0.1:${toString cfg.backendPort}
        }

        handle {
          root * ${cfg.frontend}

          encode gzip zstd

          try_files {path} /index.html
          file_server
        }
      '';
    };

    networking.firewall.allowedTCPPorts = [ cfg.port ];
  };
}
