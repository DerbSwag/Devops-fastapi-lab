#!/bin/bash

sudo apt update
sudo apt install docker.io docker-compose nginx -y

sudo systemctl enable docker
sudo systemctl start docker

docker compose up -d
