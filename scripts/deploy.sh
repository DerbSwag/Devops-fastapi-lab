#!/bin/bash

echo "Pull latest code"
git pull

echo "Build container"
docker compose build

echo "Restart stack"
docker compose up -d

echo "Deployment complete"
