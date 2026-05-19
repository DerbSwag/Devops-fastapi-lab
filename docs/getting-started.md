# Getting Started

Full setup guide for running the DevOps FastAPI Lab locally with Docker and Kubernetes.

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| Docker + Docker Compose | Container runtime |
| kubectl | Kubernetes CLI |
| k3s | Lightweight Kubernetes (single-node) |
| Helm 3 | Kubernetes package manager |
| ArgoCD CLI | GitOps management (optional) |

---

## 1. Clone & Configure

```bash
git clone https://github.com/DerbSwag/Devops-fastapi-lab.git
cd Devops-fastapi-lab
cp .env.example .env
```

Edit `.env` and set:
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
```

> ⚠️ Never commit real values. `.env` is excluded via `.gitignore`.

---

## 2. Run with Docker Compose

```bash
# Application
docker compose -f compose/app.yml up -d

# Monitoring stack (Prometheus + Grafana + Alertmanager)
docker compose -f compose/monitoring.yml up -d
```

Verify:
- FastAPI → http://localhost:8000
- Prometheus → http://localhost:9090
- Grafana → http://localhost:3000 (admin/admin)
- Alertmanager → http://localhost:9093

---

## 3. Deploy to Kubernetes (Helm)

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Install FastAPI via Helm
helm install fastapi helm/fastapi/
```

---

## 4. Setup ArgoCD (GitOps)

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8888:443 --address 0.0.0.0
# https://<VM_IP>:8888

# Check sync status
kubectl get application -n argocd
```

ArgoCD monitors `helm/fastapi/` on the `main` branch and auto-syncs changes to the cluster.

---

## 5. Ingress + NetworkPolicy + HPA (Level 4)

```bash
# Install Nginx Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443

# Apply HPA
kubectl apply -f k8s/level4-ingress-hpa/hpa.yaml
```

Test ingress (add `<VM_IP> fastapi.local` to `/etc/hosts`):
```bash
curl -H "Host: fastapi.local" http://<VM_IP>:30080/
```

Monitor HPA:
```bash
watch "kubectl get hpa && kubectl top pods"
```

---

## 6. StatefulSet + RBAC (Level 5)

```bash
# Create namespace
kubectl create namespace level5

# Create secrets (never commit real values)
kubectl create secret generic fastapi-secret \
  --from-literal=DB_USER=postgres \
  --from-literal=DB_PASSWORD=yourpassword \
  --from-literal=SECRET_KEY=yoursecretkey \
  -n level5

# Deploy
kubectl apply -f k8s/level5-statefulset/configmap.yaml
kubectl apply -f k8s/level5-statefulset/rbac/
kubectl apply -f k8s/level5-statefulset/postgres/
kubectl apply -f k8s/level5-statefulset/fastapi/
```

---

## 7. Multi-environment Helm Deploy

```bash
# Dev (NodePort 32010)
helm upgrade --install fastapi-dev ./helm/fastapi \
  -f helm/values/values-dev.yaml -n level5-dev --create-namespace

# Prod (NodePort 32011)
helm upgrade --install fastapi-prod ./helm/fastapi \
  -f helm/values/values-prod.yaml -n level5-prod --create-namespace
```

---

## 8. TLS with cert-manager (Level 6)

```bash
# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true

# Apply TLS configs
kubectl apply -f k8s/level4-ingress-hpa/cluster-issuer.yaml
kubectl apply -f k8s/level4-ingress-hpa/fastapi-ingress-tls.yaml
kubectl apply -f k8s/level4-ingress-hpa/monitoring-ingress.yaml
```

Domains (add to `/etc/hosts`):

| Domain | Service |
|--------|---------|
| fastapi.lab | FastAPI App (HTTPS) |
| grafana.lab | Grafana Dashboard |
| prometheus.lab | Prometheus |
| alertmanager.lab | Alertmanager |

---

## 9. Loki Logging Stack (Level 8)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install loki-stack grafana/loki-stack \
  -n monitoring --create-namespace \
  -f k8s/level8-loki/loki-values.yaml
```

Verify in Grafana → Data Sources → Loki → Explore.

---

## CI/CD Pipeline

Every push to `main` triggers:

1. GitHub Actions builds Docker image
2. Pushes to `ghcr.io/derbswag/devops-api:latest` + `:<git-sha>`
3. Self-hosted runner deploys via Docker Compose
4. ArgoCD detects Helm drift → auto-sync to Kubernetes

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ArgoCD sync failed | `kubectl get application -n argocd -o yaml` — check `.status.conditions` |
| HPA not scaling | Ensure metrics-server is running: `kubectl top pods` |
| cert-manager pending | Check ClusterIssuer: `kubectl describe clusterissuer` |
| Pods CrashLoopBackOff | Check logs: `kubectl logs <pod> -n <namespace>` |
| Grafana no data | Verify Prometheus target is up at http://localhost:9090/targets |
