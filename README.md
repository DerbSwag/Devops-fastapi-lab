Readme · MDCopyDevOps FastAPI Lab 🚀
A production-style DevOps lab using FastAPI, Docker, Kubernetes, and a full monitoring stack with automated CI/CD pipeline and GitOps.

Architecture
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

Tech Stack
CategoryToolsApplicationFastAPI, PythonContainerizationDocker, Docker ComposeContainer RegistryGitHub Container Registry (GHCR)OrchestrationKubernetes (k3s), HelmGitOpsArgoCDIngressNginx Ingress ControllerReverse ProxyNginx, TraefikMonitoringPrometheus, Grafana, Node Exporter, cAdvisorAlertingAlertmanager → DiscordCI/CDGitHub Actions + Self-hosted RunnerVersion ControlGit, GitHub

Project Structure
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
│   ├── cert-manager/
│   ├── hpa/
│   ├── ingress/
│   ├── level5/             ← Level 5
│   └── rbac/
├── helm/
│   └── fastapi/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values/
│       └── templates/
├── level4-ingress-hpa/
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

Prerequisites
Before getting started, ensure the following are installed:

Docker + Docker Compose
kubectl
k3s (single-node Kubernetes)
Helm 3
ArgoCD CLI (optional)


Learning Roadmap
✅ Level 1 — Docker & CI/CD

FastAPI containerized with Docker
Docker Compose for multi-service stack
GitHub Actions CI/CD pipeline
Auto-deploy via self-hosted runner
Image pushed to GHCR

✅ Level 2 — Kubernetes & Helm

k3s single-node cluster setup
FastAPI deployed via Helm chart
ConfigMap & Secrets management
Service types: ClusterIP / NodePort

✅ Level 3 — GitOps & Monitoring

ArgoCD installed on k3s
Auto-sync from helm/fastapi/ on main branch
Self-heal enabled
Prometheus + Grafana + Alertmanager stack
5 alert rules → Discord notifications

✅ Level 4 — Advanced Kubernetes

Nginx Ingress Controller — expose services via domain instead of NodePort
NetworkPolicy — pod-level firewall, restrict traffic to ingress-nginx namespace only
HPA — auto-scale FastAPI pods 1→5 replicas based on CPU utilization (50%)

✅ Level 5 — StatefulSet, RBAC & Multi-env Helm

PostgreSQL via StatefulSet + PersistentVolume (2Gi)
ConfigMap & Secret management for DB credentials
RBAC — namespace-scoped Role + RoleBinding for FastAPI service account
Helm multi-environment deploy (dev / prod) with separate values files

✅ Level 6 — Ingress + TLS

Nginx Ingress Controller + cert-manager for domain-based routing
Self-signed ClusterIssuer for HTTPS termination
Multi-service ingress (FastAPI, Grafana, Prometheus, Alertmanager)

DomainServicefastapi.labFastAPI App (HTTPS)grafana.labGrafana Dashboardprometheus.labPrometheusalertmanager.labAlertmanager
✅ Level 7 — HPA Stress Test

Auto-scaling FastAPI pods based on CPU load
Stress test result: 199% CPU spike → scaled from 1 → 6 pods automatically

SettingValueMin Replicas1Max Replicas10Target CPU50%

CI/CD Pipeline
Every push to main triggers:
1. Build Docker image
2. Push image → ghcr.io/derbswag/devops-api:latest + :<git-sha>
3. Self-hosted runner deploys via Docker Compose
4. ArgoCD detects Helm changes → sync to Kubernetes

GitOps with ArgoCD
ArgoCD monitors helm/fastapi/ and auto-syncs to Kubernetes:
bash# Check sync status
kubectl get application -n argocd

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8888:443 --address 0.0.0.0
# https://<VM_IP>:8888

Getting Started
1. Clone repository
bashgit clone https://github.com/DerbSwag/Devops-fastapi-lab.git
cd Devops-fastapi-lab
2. Configure secrets
bash# Copy example env file and fill in your values
cp .env.example .env
# Set DISCORD_WEBHOOK_URL in .env — never commit real values
3. Run Application (Docker)
bashdocker compose -f compose/app.yml up -d
docker compose -f compose/monitoring.yml up -d
4. Deploy to Kubernetes (Helm)
bashexport KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install fastapi helm/fastapi/
5. Apply Level 4 configs
bashkubectl apply -f level4-ingress-hpa/
6. Deploy Level 5 (StatefulSet + RBAC)
bash# Create secrets first (never commit real values)
kubectl create secret generic fastapi-secret \
  --from-literal=DB_USER=postgres \
  --from-literal=DB_PASSWORD=yourpassword \
  --from-literal=SECRET_KEY=yoursecretkey \
  -n level5

kubectl apply -f k8s/level5/configmap.yaml
kubectl apply -f k8s/level5/rbac/
kubectl apply -f k8s/level5/postgres/
kubectl apply -f k8s/level5/fastapi/
7. Helm multi-environment deploy
bash# Dev (NodePort 32010)
helm upgrade --install fastapi-dev ./helm/fastapi \
  -f helm/values/values-dev.yaml -n level5-dev --create-namespace

# Prod (NodePort 32011)
helm upgrade --install fastapi-prod ./helm/fastapi \
  -f helm/values/values-prod.yaml -n level5-prod --create-namespace
8. Install Ingress + TLS (Level 6)
bashhelm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true

kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
kubectl apply -f k8s/ingress/

Level 4 — Ingress, NetworkPolicy, HPA
Ingress Controller
bash# Access via domain (add to /etc/hosts: <VM_IP> fastapi.local)
curl -H "Host: fastapi.local" http://<VM_IP>:30080/
NetworkPolicy
bashkubectl apply -f level4-ingress-hpa/fastapi-netpol.yaml

# Verify
curl -H "Host: fastapi.local" http://<VM_IP>:30080/  # ✅ allowed
curl --max-time 5 http://<POD_IP>:8000/               # ❌ blocked
HPA
bashkubectl apply -f level4-ingress-hpa/fastapi-hpa.yaml

# Monitor scaling
watch "kubectl get hpa && kubectl top pods"

Service URLs
ServiceURLFastAPI (Docker)http://localhost:8000FastAPI (K8s - Ingress)http://fastapi.local:30080FastAPI (K8s - NodePort)http://<VM_IP>:32010Prometheushttp://localhost:9090Grafanahttp://localhost:3000Alertmanagerhttp://localhost:9093Node Exporterhttp://localhost:9100Portainerhttp://localhost:9000ArgoCDhttps://<VM_IP>:8888

Note: All URLs above are for local lab use only. Do not expose these ports to the internet without proper authentication.


Monitoring & Alerting
Alert Rules
AlertConditionSeverityHighCPUUsageCPU > 80% for 1mwarningHighMemoryUsageRAM > 85% for 1mwarningDiskSpaceLowDisk > 80% for 1mcriticalInstanceDownService down for 1mcriticalContainerHighCPUContainer CPU > 80%warning
Alerts are sent to Discord via Alertmanager webhook (configured via DISCORD_WEBHOOK_URL environment variable — see .env.example).
Grafana
URL:      http://localhost:3000
Username: admin
Password: admin  ← change this for any non-local environment

Security Notes

Discord webhook URL is loaded from environment variable, never hardcoded
Kubernetes secrets are created via kubectl create secret — template files use placeholder values only
Real secret files (*secret-real.yaml, *.env) are excluded via .gitignore


License
MIT License
