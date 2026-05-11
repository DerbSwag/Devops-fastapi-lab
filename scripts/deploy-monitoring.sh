#!/bin/bash
set -e
cd "$(dirname "$0")/.."

# Load env vars
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Generate alertmanager config from template
envsubst < monitoring/alertmanager/alertmanager.yml.template > monitoring/alertmanager/alertmanager.yml

# Start monitoring stack
docker compose -f compose/monitoring.yml up -d

echo "Monitoring stack deployed."
