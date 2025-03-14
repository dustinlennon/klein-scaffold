
Quickstart
====


```bash
# clone the repo
git clone git@github.com:dustinlennon/klein-scaffold.git

# update files: dotenv, docker-compose.yaml, systemd/site-example.service

# add a symbolic link
sudo ln -s $(pwd) /opt/site-example

# build the image
SCAFFOLD_PATH=$(pwd) docker-compose -f docker-compose.yaml build

# open the port to LAN
sudo ufw allow proto tcp from 192.168.1.0/24 to any port 8082 comment "site-example"

# enable and start the service
sudo systemctl enable ./site-example.service
sudo systemct start ./site-example.service 

# test
curl localhost:8082/welcome

```



Run Scenarios
====

```bash
# local
pipenv run python3 app/scaffold/builder.py --config app/config.yaml
pipenv run python3 app/scaffold/builder.py --config app/config.yaml --production
pipenv run python3 -m app.scaffold.builder --production --config app/config.yaml

# local dynamic reload
app/serve.sh

# twistd
pipenv run twistd -ny app/server.tac

# docker
SCAFFOLD_PATH=$(pwd) docker-compose -f docker-compose.yaml build
SCAFFOLD_PATH=$(pwd) docker-compose -f docker-compose.yaml up --force-recreate -V

```