# Level 11 — Service Mesh (Linkerd)

Lightweight service mesh on k3s — mTLS, traffic observability, and reliability features.

> Using **Linkerd** over Istio because it's lighter (~200MB RAM vs ~2GB) and better suited for k3s.

## Architecture

```
┌─── k3s Cluster with Linkerd ────────────────────────────┐
│                                                           │
│  ┌──────────────────────────────────────────────┐        │
│  │ Linkerd Control Plane                         │        │
│  │  ├── destination (service discovery)          │        │
│  │  ├── identity (mTLS certificate authority)    │        │
│  │  └── proxy-injector (sidecar injection)       │        │
│  └──────────────────────────────────────────────┘        │
│                                                           │
│  ┌─────────┐  mTLS   ┌─────────┐  mTLS   ┌─────────┐  │
│  │ FastAPI │◄───────►│ Postgres│◄───────►│ Redis   │  │
│  │ + proxy │         │ + proxy │         │ + proxy │  │
│  └─────────┘         └─────────┘         └─────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────┐        │
│  │ Linkerd Viz (Dashboard)                       │        │
│  │  - Live traffic topology                      │        │
│  │  - Per-route success rate & latency           │        │
│  │  - TCP connections & bytes                    │        │
│  └──────────────────────────────────────────────┘        │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## What Service Mesh Gives You

| Feature | Without Mesh | With Linkerd |
|---------|-------------|--------------|
| Encryption | Plain HTTP between pods | **mTLS everywhere** (auto) |
| Observability | Need custom metrics | **Golden metrics** (latency, success rate, RPS) |
| Retries | App must implement | **Automatic retries** on failure |
| Traffic split | Manual deployment | **Canary deploys** (90/10 traffic split) |
| Auth | NetworkPolicy only | **Service-to-service identity** |

## Setup

```bash
# 1. Install Linkerd CLI
curl -sL https://run.linkerd.io/install | sh
export PATH=$HOME/.linkerd2/bin:$PATH

# 2. Pre-check
linkerd check --pre

# 3. Install control plane
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -

# 4. Verify
linkerd check

# 5. Install Viz dashboard
linkerd viz install | kubectl apply -f -

# 6. Inject sidecar to FastAPI namespace
kubectl get deploy -n default -o yaml | linkerd inject - | kubectl apply -f -

# 7. Access dashboard
linkerd viz dashboard
```

## Mesh FastAPI deployment

```yaml
# Add annotation to enable sidecar injection
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi
  annotations:
    linkerd.io/inject: enabled
spec:
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
```

## Traffic Split (Canary Deploy)

```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: fastapi-canary
spec:
  service: fastapi
  backends:
  - service: fastapi-stable
    weight: 900m    # 90%
  - service: fastapi-canary
    weight: 100m    # 10%
```

## Resource Requirements

| Component | RAM |
|-----------|-----|
| Control plane | ~200MB |
| Per-pod proxy sidecar | ~20MB |
| Viz dashboard | ~100MB |
| **Total** | **~350MB** |

## Files

| File | Purpose |
|------|---------|
| `linkerd-inject-annotation.yaml` | Annotation patch for existing deployments |
| `traffic-split.yaml` | Canary deploy example |
| `README.md` | This file |
