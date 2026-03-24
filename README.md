# DevOps FastAPI Lab 🚀

A production-style DevOps lab using FastAPI, Docker, Kubernetes, and a full monitoring stack with automated CI/CD pipeline.

---

## Architecture
```
git push
    │
    ▼
GitHub Actions (CI/CD)
    ├── Build Docker image
    ├── Push → GitHub Container Registry (GHCR)
    └── Auto deploy → Self-hosted Runner (VM)
              │
              ▼
    ┌─────────────────────────┐
    │   Ubuntu VM (Home Lab)  │
    ├─────────────────────────┤
    │  Nginx Reverse Proxy    │
    │         │               │
    │  FastAPI (Docker)       │
    │         │               │
    │  Prometheus → Grafana   │
    │  Node Exporter          │
    │  cAdvisor               │
    │  Alertmanager           │
    └─────────────────────────┘
              │
    ┌─────────────────────────┐
    │   Kubernetes (k3s)      │
    ├─────────────────────────┤
    │  FastAPI Deployment     │
    │  Nginx (Helm)           │
    │  Traefik Ingress        │
    └─────────────────────────┘
```

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Application | FastAPI, Python |
| Containerization | Docker, Docker Compose |
| Container Registry | GitHub Container Registry (GHCR) |
| Orchestration | Kubernetes (k3s), Helm |
| Reverse Proxy | Nginx, Traefik |
| Monitoring | Prometheus, Grafana, Node Exporter, cAdvisor |
| Alerting | Alertmanager |
| CI/CD | GitHub Actions |
| Runner | Self-hosted (Ubuntu VM) |
| Version Control | Git, GitHub |

---

## Project Structure
```
.
├── app/                    # FastAPI application
│   ├── main.py
│   └── requirements.txt
├── docker/                 # Dockerfile
│   └── Dockerfile
├── compose/                # Docker Compose files
│   ├── app.yml
│   └── monitoring.yml
├── monitoring/             # Monitoring configs
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── provisioning/
│   └── alertmanager/
│       └── alertmanager.yml
├── k8s/                    # Kubernetes manifests
│   ├── fastapi-deploy.yml
│   ├── fastapi-service.yml
│   └── fastapi-ingress.yml
├── helm/                   # Helm chart
│   └── fastapi/
├── nginx/                  # Nginx config
│   └── my-api.conf
├── scripts/                # Automation scripts
│   ├── setup.sh
│   └── deploy.sh
└── .github/workflows/      # CI/CD pipeline
    └── docker.yml
```

---

## CI/CD Pipeline

Every push to `main` branch triggers:
```
1. Build Docker image
2. Push image to GHCR (ghcr.io/derbswag/devops-api:latest)
3. Self-hosted runner pulls new image
4. Container restarts automatically
```

Workflow file: `.github/workflows/docker.yml`

---

## Getting Started

### Clone repository
```bash
git clone https://github.com/DerbSwag/Devops-fastapi-lab.git
cd Devops-fastapi-lab
```

### Run Application
```bash
# Start FastAPI
docker compose -f compose/app.yml up -d

# Start monitoring stack
docker compose -f compose/monitoring.yml up -d
```

### Deploy to Kubernetes
```bash
kubectl apply -f k8s/fastapi-deploy.yml
kubectl apply -f k8s/fastapi-service.yml
kubectl apply -f k8s/fastapi-ingress.yml
```

---

## Service URLs

| Service | URL |
|---------|-----|
| FastAPI | http://localhost:8000 |
| Nginx | http://localhost |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Alertmanager | http://localhost:9093 |
| Node Exporter | http://localhost:9100 |
| Portainer | http://localhost:9000 |

### Grafana Login
```
Username: admin
Password: admin
```

---

## Monitoring Stack

| Tool | Purpose |
|------|---------|
| Prometheus | Metrics collection & storage |
| Grafana | Visualization dashboards |
| Node Exporter | Host metrics (CPU, RAM, Disk) |
| cAdvisor | Container metrics |
| Alertmanager | Alert routing & notifications |

---

## License

MIT License
