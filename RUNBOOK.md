# RUNBOOK — Devops-fastapi-lab

> Procedures for the DevOps lab (k3s, ArgoCD, Prometheus, Grafana, Loki, Helm)
> Updated: 2026-06-15

## Quick Reference

| Item | Value |
|------|-------|
| Cluster | k3s (local/lab) |
| GitOps | ArgoCD |
| Monitoring | Prometheus + Grafana + Loki |
| CI/CD | GitHub Actions |
| App | FastAPI (Python) |

---

## Procedures

### 1. Deploy App via ArgoCD

```bash
git push origin main  # ArgoCD auto-syncs
# Manual sync:
argocd app sync fastapi-app
```

### 2. Access Grafana

```bash
kubectl port-forward svc/grafana 3000:80 -n monitoring
# Default: admin / prom-operator (from Helm values)
```

### 3. Check Pod Health

```bash
kubectl get pods -A
kubectl logs <pod> -n <ns>
```

### 4. Cert-Manager Certificate Issues

```bash
kubectl get certificates -A
kubectl describe certificate <name> -n <ns>
# If stuck: delete certificate resource, ArgoCD will recreate
```

### 5. Troubleshooting

| Symptom | Fix |
|---------|-----|
| ArgoCD OutOfSync | `argocd app sync <app> --force` |
| ImagePullBackOff | Check image tag in deployment YAML, verify registry access |
| Loki no logs | Check promtail DaemonSet pods running |

---

## Secrets & Security

- Helm values with secrets: sealed-secrets or SOPS
- ArgoCD admin: initial-admin-secret in argocd namespace
- ห้าม commit: kubeconfig, .env with real values

---

## Related Docs

- `README.md` — full architecture and setup guide
