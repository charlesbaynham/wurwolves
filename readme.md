Wurwolves
=========

A simple web app to play Werewolves (AKA Mafia) online. Live now at [wurwolves.com](https://www.wurwolves.com).

This repository is ready to be deployed to a Heroku dyno. You'll need to manually add both the python and nodejs buildpacks like so:

```
heroku buildpacks:clear
heroku buildpacks:set heroku/nodejs
heroku buildpacks:add --index 1 heroku/python
```

And also the PostgreSQL addon:

```
heroku addons:create heroku-postgresql:hobby-dev
```

Alternatively, provision on your container platform of choice. The database is accessed and configured through the environmental variable `DATABASE_URL`.

Local use
---------

For local use, create and activate a python virtual environment then install and run:

```
virtualenv venv
source venv/bin/activate
npm install
npm dev
```

Outline
-------

The backend runs a FastAPI REST interface in python. The frontend is React.js served by its built-in server.
