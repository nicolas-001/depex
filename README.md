# Depex Proyect

## Deployment with docker

I recommend to run command 'export DOCKER_BUILDKIT=1' before start working with docker.

1. Create a .env file from template.env

2. Deploy
- First time --> Run command 'docker-compose -f docker-compose-init.yml up --build' (Init dockerfile will seed MongoDB database with vulnerabilities and modeled package managers)
- After first Time --> Run command 'docker-compose up --build'

3. Enter [here](http://0.0.0.0:8000/docs)

(It is recommended to use a GUI such as [MongoDB Compass](https://www.mongodb.com/en/products/compass) to see what information is being indexed)

## Extra information

1. Here they are the [GitHub releases](https://github.com/GermanMT/depex/releases)

2. Here they are the [DockerHub releases](https://hub.docker.com/r/germanmt/depex/tags)