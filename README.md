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
          ├── Nginx Ingress Controller  ← Level 4
          ├── NetworkPolicy             ← Level 4
          ├── HPA (Auto-scaling)        ← Level 4
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
| Ingress | Nginx Ingress Controller |
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
├── docker/
│   └── Dockerfile
├── compose/
│   ├── app.yml
│   └── monitoring.yml
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   └── alertmanager/
│       └── alertmanager.yml
├── k8s/
│   ├── fastapi-deploy.yml
│   ├── fastapi-service.yml
│   └── fastapi-ingress.yml
├── helm/
│   └── fastapi/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── level4-ingress-hpa/     ← Level 4
│   ├── fastapi-ingress.yaml
│   ├── fastapi-netpol.yaml
│   └── fastapi-hpa.yaml
├── nginx/
│   └── my-api.conf
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
└── .github/workflows/
    └── docker.yml
```

---

## Learning Roadmap

### ✅ Level 1 — Docker & CI/CD
- FastAPI containerized with Docker
- Docker Compose for multi-service stack
- GitHub Actions CI/CD pipeline
- Auto-deploy via self-hosted runner
- Image pushed to GHCR

### ✅ Level 2 — Kubernetes & Helm
- k3s single-node cluster setup
- FastAPI deployed via Helm chart
- ConfigMap & Secrets management
- Service types: ClusterIP / NodePort

### ✅ Level 3 — GitOps & Monitoring
- ArgoCD installed on k3s
- Auto-sync from `helm/fastapi/` on main branch
- Self-heal enabled
- Prometheus + Grafana + Alertmanager stack
- 5 alert rules → Discord notifications

### ✅ Level 4 — Advanced Kubernetes
- **Nginx Ingress Controller** — expose services via domain instead of NodePort
- **NetworkPolicy** — pod-level firewall, restrict traffic to ingress-nginx namespace only
- **HPA** — auto-scale FastAPI pods 1→5 replicas based on CPU utilization (50%)

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

ArgoCD monitors `helm/fastapi/` and auto-syncs to Kubernetes:
```bash
# Check sync status
kubectl get application -n argocd

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8888:443 --address 0.0.0.0
# https://<VM_IP>:8888
```

---

## Level 4 — Ingress, NetworkPolicy, HPA

### Ingress Controller
```bash
# Install Nginx Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443

# Access via domain
curl -H "Host: fastapi.local" http://192.168.141.129:30080/
```

### NetworkPolicy
```bash
# Apply network policy
kubectl apply -f level4-ingress-hpa/fastapi-netpol.yaml

# Verify: ingress traffic allowed, direct pod access blocked
curl -H "Host: fastapi.local" http://192.168.141.129:30080/  # ✅ allowed
curl --max-time 5 http://<POD_IP>:8000/                       # ❌ blocked
```

### HPA
```bash
# Apply HPA
kubectl apply -f level4-ingress-hpa/fastapi-hpa.yaml

# Monitor scaling
watch "kubectl get hpa && kubectl top pods"
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
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install fastapi helm/fastapi/
```

### Apply Level 4 configs
```bash
kubectl apply -f level4-ingress-hpa/
```

---

## Service URLs

| Service | URL |
|---------|-----|
| FastAPI (Docker) | http://localhost:8000 |
| FastAPI (K8s - Ingress) | http://fastapi.local:30080 |
| FastAPI (K8s - NodePort) | http://192.168.141.129:30008 |
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

---

## Level 6 — Ingress + TLS

Nginx Ingress Controller + cert-manager สำหรับ domain-based routing และ HTTPS

| Domain | Service |
|---|---|
| fastapi.lab | FastAPI App (HTTPS) |
| grafana.lab | Grafana Dashboard |
| prometheus.lab | Prometheus |
| alertmanager.lab | Alertmanager |
```bash
# Install Nginx Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true
```

## Level 7 — HPA (Horizontal Pod Autoscaler)

Auto-scaling FastAPI pods ตาม CPU load

| Setting | Value |
|---|---|
| Min Pods | 1 |
| Max Pods | 10 |
| CPU Threshold | 50% |

Result: CPU spike 199% → scale จาก 1 → 6 pods อัตโนมัติ

---

## Level 6 — Ingress + TLS

Nginx Ingress Controller + cert-manager สำหรับ domain-based routing และ HTTPS

| Domain | Service |
|---|---|
| fastapi.lab | FastAPI App (HTTPS) |
| grafana.lab | Grafana Dashboard |
| prometheus.lab | Prometheus |
| alertmanager.lab | Alertmanager |
```bash
# Install Nginx Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true
```

## Level 7 — HPA (Horizontal Pod Autoscaler)

Auto-scaling FastAPI pods ตาม CPU load

| Setting | Value |
|---|---|
| Min Pods | 1 |
| Max Pods | 10 |
| CPU Threshold | 50% |

Result: CPU spike 199% → scale จาก 1 → 6 pods อัตโนมัติ
