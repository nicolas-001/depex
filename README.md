# Depex Project

<p>
  <a href="https://github.com/GermanMT/depex/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/GermanMT/depex?color=green&logo=github" alt="release">
  </a>

  <a href="https://github.com/GermanMT/depex/blob/main/LICENSE.md" target="_blank">
    <img src="https://img.shields.io/github/license/GermanMT/depex?logo=gnu" alt="license">
  </a>

  <a href="https://doi.org/10.5281/zenodo.12793934">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.12793934.svg" alt="DOI">
  </a>
</p>

## Video tutorial

https://github.com/user-attachments/assets/0dbb63f4-7bc5-4e4d-81d0-94444a61e386

## Deployment requirements

1. [Docker](https://www.docker.com/) to deploy the tool.

2. [Git Large Files Storage](https://git-lfs.com/) (git-lfs) for cloning correctly the seeds of the repository.

## Deployment with docker

### Step 1
Create a .env from *template.env* file.

#### Get API Keys

- How to get a *GitHub* [API key](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

- Modify the **Json Web Token (JWT)** secret key with your own. You can generate your own with the command **node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"**.

### Step 2
Run command 'docker compose up --build'. The vulnerability database will be loaded with the data automatically extracted from the NVD up to the date of the release being downloaded. And it will automatically update to the present time before deploying the *backend*. If you want to avoid the update and the time it takes, you can comment out the *lifespan* function in the */backend/app/main.py* file.

#### Seeders

- You can create your graphs from scratch or load existing ones used in the experimentation of other articles or simply built and that can help in the creation of new graphs (this task can be time consuming). To do this use the script **seeds/graphdb_seeder.sh** if you are on Linux or **graphdb_seeder.bat** if you are on Windows.

### Step 3 
Enter [here](http://0.0.0.0:3000) for the frontend Web API.

#### Other tools
1. It is recommended to use a GUI such as [MongoDB Compass](https://www.mongodb.com/en/products/compass) to see what information is being indexed in vulnerability database.
   
2. You can see the created graph built for [pip](http://0.0.0.0:7474/browser/), [npm](http://localhost:7473/browser/) and [mvn](http://localhost:7472/browser/) clicking in this names. Using the Neo4J browser interfaces.

## Proxy Enviroment

### Create an *.env* file por proxy settings

Define these variables in an *.env* file that can be referenced by *docker-compose.yml*. Example *.env* file:

```
HTTP_PROXY=http://proxy.example.com:port
HTTPS_PROXY=https://proxy.example.com:port
NO_PROXY=localhost,127.0.0.1
```

### Add an *.env* to the *docker-compose.yml*

Add the proxy configuration defined in the *.env* file, for example to the following *docker-compose.yml* file:

```
services:
  app:
    image: your-app-image
    build: .
    env_file:
      - .env
    ports:
      - "8080:80"
```