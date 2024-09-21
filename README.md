# Microservice of Social Sweat App

### Setup guide:

Run these commands in bash:
```
python3.12 -m venv .venv
source .venv/bin/activate
python --version
pip install --upgrade pip
pip install pip-tools
/bin/sh -e scripts/install_requirements_dev.sh
```

For running, needs a running mongodb. Create one in a docker with (you can replace x- variables):
```
sudo docker run -d --name x-docker_mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=x-name -e MONGO_INITDB_ROOT_PASSWORD=x-pass -v mongo_db:/data/db mongo:latest
```
and have these envs for it
```
## - MongoDB Config - ##
MONGO_VARIABLES_HOST=0.0.0.0
MONGO_VARIABLES_PORT=27017
MONGO_VARIABLES_USERNAME=x-name
MONGO_VARIABLES_PASSWORD=x-pass
```

### Running guide:

See `.env.example` file for all the envs you need

Start the mongo you created with `sudo docker start x-docker_mongodb`

Run the microservice locally with `python3.12 bin/run.py` or in a docker with `sudo docker-compose up` or `sudo docker compose up`
