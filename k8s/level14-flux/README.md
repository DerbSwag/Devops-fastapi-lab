# Level 14 — GitOps with Flux

Alternative GitOps tool — compare Flux vs ArgoCD side-by-side.

## Why Both?

- ArgoCD = UI-first, pull-based, great dashboard
- Flux = CLI-first, push-based, native Helm/Kustomize support
- Knowing both = shows depth, not just one-tool knowledge

## Comparison

| Feature | ArgoCD (Level 3) | Flux (this level) |
|---------|-------------------|-------------------|
| UI | Rich web dashboard | CLI + Grafana |
| Sync | Pull (polls repo) | Pull (reconciliation loop) |
| Helm | App of Apps | HelmRelease CRD |
| Kustomize | Supported | Native |
| Multi-tenancy | Projects | Namespaced controllers |
| Notifications | Built-in | Notification Controller |
| Weight | ~500MB RAM | ~200MB RAM |

## Architecture

```
GitHub Repo (helm/fastapi/)
       │
       ▼ (Flux watches)
┌─── k3s ─────────────────────────┐
│                                   │
│  Source Controller                │
│  (fetches from Git/Helm repos)   │
│       │                           │
│       ▼                           │
│  Kustomize/Helm Controller        │
│  (applies manifests)              │
│       │                           │
│       ▼                           │
│  FastAPI Deployment (synced)      │
│                                   │
└───────────────────────────────────┘
```

## Setup

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap (connects to your GitHub repo)
flux bootstrap github \
  --owner=DerbSwag \
  --repository=Devops-fastapi-lab \
  --path=k8s/level14-flux/clusters/home-lab \
  --personal

# Check status
flux get all
```

## Key CRDs

```yaml
# GitRepository — source
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: devops-lab
spec:
  url: https://github.com/DerbSwag/Devops-fastapi-lab
  ref:
    branch: main
  interval: 1m
---
# HelmRelease — deploy
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: fastapi
spec:
  interval: 5m
  chart:
    spec:
      chart: ./helm/fastapi
      sourceRef:
        kind: GitRepository
        name: devops-lab
  values:
    replicaCount: 2
```

## TODO

- [ ] Install Flux on k3s (separate namespace from ArgoCD)
- [ ] Bootstrap with GitHub repo
- [ ] Create GitRepository + HelmRelease for FastAPI
- [ ] Verify auto-sync on git push
- [ ] Compare sync speed: ArgoCD vs Flux
- [ ] Set up Flux notifications → Discord
