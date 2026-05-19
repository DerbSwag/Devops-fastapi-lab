# Learning Roadmap

Detailed level-by-level walkthrough of the DevOps FastAPI Lab. Each level builds on the previous one.

---

## Level 1 — Docker & CI/CD

**Goal:** Containerize the application and automate builds.

### What was done:
- FastAPI app containerized with multi-stage Dockerfile
- Docker Compose for running app + monitoring stack
- GitHub Actions CI/CD pipeline (`.github/workflows/docker.yml`)
- Self-hosted runner for auto-deploy
- Images pushed to GitHub Container Registry (GHCR)

### Key files:
```
docker/Dockerfile
compose/app.yml
compose/monitoring.yml
.github/workflows/docker.yml
```

### Pipeline flow:
```
git push → GitHub Actions → Build image → Push to ghcr.io/derbswag/devops-api
                                                    │
                                          Self-hosted runner
                                                    │
                                          docker compose up -d
```

---

## Level 2 — Kubernetes & Helm

**Goal:** Deploy to Kubernetes using Helm charts.

### What was done:
- k3s single-node cluster setup
- FastAPI deployed via custom Helm chart
- ConfigMap for app configuration
- Secrets for sensitive data
- Service types: ClusterIP (internal) and NodePort (external access)

### Key files:
```
helm/fastapi/Chart.yaml
helm/fastapi/values.yaml
helm/fastapi/templates/
```

### Commands:
```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install fastapi helm/fastapi/
kubectl get pods
```

---

## Level 3 — GitOps & Monitoring

**Goal:** Implement GitOps with ArgoCD and full monitoring stack.

### What was done:
- ArgoCD installed on k3s, monitoring `helm/fastapi/` on `main` branch
- Auto-sync enabled — any Helm change auto-deploys
- Self-heal enabled — manual drift is auto-corrected
- Prometheus + Grafana + Alertmanager deployed
- 5 alert rules configured → Discord notifications

### Alert rules:
| Alert | Condition | Severity |
|-------|-----------|----------|
| HighCPUUsage | CPU > 80% for 1m | warning |
| HighMemoryUsage | RAM > 85% for 1m | warning |
| DiskSpaceLow | Disk > 80% for 1m | critical |
| InstanceDown | Service down for 1m | critical |
| ContainerHighCPU | Container CPU > 80% | warning |

### Key files:
```
monitoring/prometheus/prometheus.yml
monitoring/prometheus/alerts.yml
monitoring/alertmanager/alertmanager.yml
```

---

## Level 4 — Advanced Kubernetes

**Goal:** Production-grade networking and auto-scaling.

### What was done:
- **Nginx Ingress Controller** — expose services via domain instead of NodePort
- **NetworkPolicy** — pod-level firewall, restrict traffic to ingress-nginx namespace only
- **HPA** — auto-scale FastAPI pods 1→5 replicas based on CPU utilization (50% target)

### Key files:
```
k8s/level4-ingress-hpa/hpa.yaml
k8s/level4-ingress-hpa/fastapi-ingress-tls.yaml
k8s/level4-ingress-hpa/monitoring-ingress.yaml
```

### HPA config:
| Setting | Value |
|---------|-------|
| Min Replicas | 1 |
| Max Replicas | 5 |
| Target CPU | 50% |

---

## Level 5 — StatefulSet, RBAC & Multi-env Helm

**Goal:** Stateful workloads, access control, and environment separation.

### What was done:
- **PostgreSQL** via StatefulSet + PersistentVolume (2Gi)
- **ConfigMap & Secret** management for DB credentials
- **RBAC** — namespace-scoped Role + RoleBinding for FastAPI service account
- **Helm multi-env** — separate `values-dev.yaml` / `values-prod.yaml`

### Key files:
```
k8s/level5-statefulset/configmap.yaml
k8s/level5-statefulset/secret.yaml
k8s/level5-statefulset/postgres/
k8s/level5-statefulset/fastapi/
k8s/level5-statefulset/rbac/
helm/values/values-dev.yaml
helm/values/values-prod.yaml
```

### Multi-env deployment:
```bash
# Dev — NodePort 32010
helm upgrade --install fastapi-dev ./helm/fastapi \
  -f helm/values/values-dev.yaml -n level5-dev --create-namespace

# Prod — NodePort 32011
helm upgrade --install fastapi-prod ./helm/fastapi \
  -f helm/values/values-prod.yaml -n level5-prod --create-namespace
```

---

## Level 6 — Ingress + TLS

**Goal:** HTTPS termination with cert-manager.

### What was done:
- Nginx Ingress Controller + cert-manager for domain-based routing
- Self-signed ClusterIssuer for HTTPS termination
- Multi-service ingress configuration

### Domains:
| Domain | Service |
|--------|---------|
| fastapi.lab | FastAPI App (HTTPS) |
| grafana.lab | Grafana Dashboard |
| prometheus.lab | Prometheus |
| alertmanager.lab | Alertmanager |

### Key files:
```
k8s/level4-ingress-hpa/cluster-issuer.yaml
k8s/level4-ingress-hpa/fastapi-ingress-tls.yaml
k8s/level4-ingress-hpa/monitoring-ingress.yaml
```

### Setup:
```bash
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true

kubectl apply -f k8s/level4-ingress-hpa/cluster-issuer.yaml
kubectl apply -f k8s/level4-ingress-hpa/fastapi-ingress-tls.yaml
kubectl apply -f k8s/level4-ingress-hpa/monitoring-ingress.yaml
```

---

## Level 7 — HPA Stress Test

**Goal:** Validate auto-scaling under load.

### What was done:
- Increased HPA max replicas to 10
- Ran CPU stress test against FastAPI pods
- Verified scaling behavior: 1 → 6 pods at 199% CPU spike

### HPA config (updated):
| Setting | Value |
|---------|-------|
| Min Replicas | 1 |
| Max Replicas | 10 |
| Target CPU | 50% |

### Result:
```
CPU spike: 199%
Pods scaled: 1 → 6
Scale-up time: ~30s after threshold breach
Scale-down: gradual after load removed
```

### Monitor:
```bash
watch "kubectl get hpa && kubectl top pods"
```

---

## Level 8 — Loki Logging Stack

**Goal:** Centralized log aggregation.

### What was done:
- Loki-stack (single binary mode) deployed in `monitoring` namespace
- Promtail collects logs from all pods automatically
- Grafana datasource integration for log search

### Key files:
```
k8s/level8-loki/loki-values.yaml
```

### Setup:
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install loki-stack grafana/loki-stack \
  -n monitoring --create-namespace \
  -f k8s/level8-loki/loki-values.yaml
```

### Verify:
1. Open Grafana → Data Sources → Loki
2. Go to Explore → Select Loki datasource
3. Query: `{namespace="default"}` to see pod logs

---

## Summary

```
Level 1: Docker + CI/CD          → Containerization & automation
Level 2: Kubernetes + Helm       → Orchestration & packaging
Level 3: ArgoCD + Monitoring     → GitOps & observability
Level 4: Ingress + HPA           → Production networking & scaling
Level 5: StatefulSet + RBAC      → Stateful workloads & security
Level 6: TLS                     → HTTPS termination
Level 7: Stress Test             → Scaling validation
Level 8: Loki                    → Centralized logging
```
