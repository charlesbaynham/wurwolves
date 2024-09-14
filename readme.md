Wurwolves
=========

A simple web app to play Werewolves (AKA Mafia) online. Live now at [wurwolves.com](https://www.wurwolves.com).

Deployment
----------

This repository can be used to build docker containers for the frontend and backend, using nix, or can be run using nix directly.

1. Configure `.env`

then either:

2. Run `nix run .#frontend` in one window
3. ...and `nix run .#backend` in another

or:

2. `nix run` to build docker images and store them in the local registry
3. `docker compose up`

Traefik
-------

The default instructions above will launch a local service for testing. To
deploy properly, use the ".env.traefik" template to wire these containers into
traefik for SSL certificates. You will need to also have a traefik instance
running and connected to the docker network called "traefik". HTTPS negotiation
is out of scope for this repository - set it up in traefik.

Local development
-----------------

For local development, install nix and direnv then use::

1. `direnv allow`
2. `npm i`
3. `npm run dev`

Outline
-------

The backend runs a FastAPI REST interface in python. The frontend is React.js served by its built-in server.
