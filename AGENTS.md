# AGENTS.md

## Project Overview

Production-style DevOps lab — FastAPI app deployed on Kubernetes (k3s) with ArgoCD GitOps, full monitoring stack (Prometheus + Grafana + Loki), GitHub Actions CI/CD, Helm charts, and cert-manager TLS.

## Tech Stack

- Python / FastAPI — application
- Docker — containerization
- Kubernetes (k3s) — orchestration
- Helm — package management
- ArgoCD — GitOps continuous delivery
- GitHub Actions — CI pipeline
- GHCR — container registry
- Prometheus + Grafana + Loki — monitoring & observability
- Alertmanager → Discord/Lark — alerting
- Nginx — reverse proxy / ingress
- cert-manager — TLS certificates

## Architecture

```
app/                → FastAPI application (main.py, requirements.txt)
docker/             → Dockerfile
compose/            → Docker Compose files (app.yml, monitoring.yml)
k8s/                → Kubernetes manifests (multi-level progression)
helm/               → Helm chart for FastAPI deployment
monitoring/         → Prometheus, Grafana, Alertmanager configs
nginx/              → Nginx reverse proxy config
scripts/            → Helper scripts
.github/workflows/  → CI pipeline (build → push to GHCR)
```

## Conventions

- Docker images tagged with git SHA and `latest`
- Helm values override per environment
- K8s manifests organized by level (level1-basic → level4-ingress-hpa)
- Monitoring configs use standard Prometheus relabeling
- Environment variables via `.env` files (gitignored)

## Commands

- Run locally: `docker compose -f compose/app.yml up -d`
- Run monitoring: `docker compose -f compose/monitoring.yml up -d`
- Build image: `docker build -f docker/Dockerfile -t fastapi-app .`
- Deploy to K8s: `helm upgrade --install fastapi helm/`
- CI: Triggered on push (build + push to GHCR)

## Important Notes

- Two environments: Home Lab (1-node k3s) and Company Lab (3-node k3s/Proxmox)
- ArgoCD auto-syncs from this repo's `helm/` directory
- Alertmanager sends to Discord webhook (Home) or Lark webhook (Company)
- No secrets in repo — use `.env.example` as reference
