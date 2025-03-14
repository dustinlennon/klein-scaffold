
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
