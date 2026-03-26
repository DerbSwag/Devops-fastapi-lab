# DevOps FastAPI Lab 🚀

A production-style DevOps lab using FastAPI, Docker, Kubernetes, and a full monitoring stack with automated CI/CD pipeline and GitOps.

---

## Architecture
```
git push
    │
    ▼
GitHub Actions (CI)
    ├── Build Docker image
    └── Push → GitHub Container Registry (GHCR)
                    │
                    ▼
             ArgoCD (GitOps CD)
                    ├── Detect Helm chart changes
                    ├── Sync → Kubernetes (k3s)
                    └── Pod update อัตโนมัติ

[ Ubuntu VM - Home Lab ]
    ├── Docker Stack
    │     ├── FastAPI (compose-api-1)
    │     ├── Nginx Reverse Proxy
    │     ├── Prometheus
    │     ├── Grafana
    │     ├── Alertmanager ──► Discord 🔔
    │     ├── Node Exporter
    │     ├── cAdvisor
    │     └── Portainer
    │
    └── Kubernetes (k3s)
          ├── FastAPI (Helm chart)
          ├── Traefik Ingress
          └── ArgoCD
```

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Application | FastAPI, Python |
| Containerization | Docker, Docker Compose |
| Container Registry | GitHub Container Registry (GHCR) |
| Orchestration | Kubernetes (k3s), Helm |
| GitOps | ArgoCD |
| Reverse Proxy | Nginx, Traefik |
| Monitoring | Prometheus, Grafana, Node Exporter, cAdvisor |
| Alerting | Alertmanager → Discord |
| CI/CD | GitHub Actions + Self-hosted Runner |
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
│   │   └── alerts.yml      # 5 alert rules
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── provisioning/
│   └── alertmanager/
│       └── alertmanager.yml  # Discord webhook
├── k8s/                    # Kubernetes manifests
│   ├── fastapi-deploy.yml
│   ├── fastapi-service.yml
│   └── fastapi-ingress.yml
├── helm/                   # Helm chart
│   └── fastapi/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
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

Every push to `main` triggers:
```
1. Build Docker image
2. Push image → ghcr.io/derbswag/devops-api:latest
3. Self-hosted runner deploys via Docker Compose
4. ArgoCD detects Helm changes → sync to Kubernetes
```

---

## GitOps with ArgoCD

ArgoCD monitors `helm/fastapi/` in this repo and auto-syncs to Kubernetes:
```bash
# Check sync status
kubectl get application -n argocd

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8888:443 --address 0.0.0.0
# https://<VM_IP>:8888
```

---

## Getting Started

### Clone repository
```bash
git clone https://github.com/DerbSwag/Devops-fastapi-lab.git
cd Devops-fastapi-lab
```

### Run Application (Docker)
```bash
docker compose -f compose/app.yml up -d
docker compose -f compose/monitoring.yml up -d
```

### Deploy to Kubernetes (Helm)
```bash
helm install fastapi helm/fastapi/
```

### Deploy via ArgoCD
```bash
kubectl apply -f - << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: fastapi
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/DerbSwag/Devops-fastapi-lab
    targetRevision: main
    path: helm/fastapi
    helm:
      releaseName: fastapi
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF
```

---

## Service URLs

| Service | URL |
|---------|-----|
| FastAPI (Docker) | http://localhost:8000 |
| FastAPI (K8s) | http://fastapi.local |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Alertmanager | http://localhost:9093 |
| Node Exporter | http://localhost:9100 |
| Portainer | http://localhost:9000 |
| ArgoCD | https://localhost:8888 |

---

## Monitoring & Alerting

### Alert Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighCPUUsage | CPU > 80% for 1m | warning |
| HighMemoryUsage | RAM > 85% for 1m | warning |
| DiskSpaceLow | Disk > 80% for 1m | critical |
| InstanceDown | Service down for 1m | critical |
| ContainerHighCPU | Container CPU > 80% | warning |

Alerts are sent to **Discord** via Alertmanager webhook.

### Grafana Login
```
Username: admin
Password: admin
```

---

## License

MIT License
