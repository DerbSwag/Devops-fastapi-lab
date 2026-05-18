# Level 12 — Multi-Cluster (Linkerd Multi-Cluster)

Connect Home Lab k3s ↔ Company Lab k3s through WireGuard tunnel with Linkerd multi-cluster service mirroring.

> **Prerequisite:** Level 9 (WireGuard VPN) must be working — clusters need network connectivity.

## Architecture

```
┌─── Home Lab (k3s) ──────────────┐         ┌─── Company Lab (k3s) ──────────┐
│                                   │         │                                 │
│  ┌─────────┐   ┌──────────────┐ │  WG VPN │ ┌──────────────┐  ┌─────────┐ │
│  │ FastAPI │   │ Linkerd      │ │◄───────►│ │ Linkerd      │  │ Postgres│ │
│  │ (local) │   │ Gateway      │ │  10.0.0 │ │ Gateway      │  │ (local) │ │
│  └─────────┘   └──────┬───────┘ │  .0/24  │ └──────┬───────┘  └─────────┘ │
│                        │         │         │        │                       │
│  Service Mirror:       │         │         │        │  Service Mirror:      │
│  postgres-company ─────┘         │         │        └── fastapi-home        │
│  (mirrored from company)         │         │           (mirrored from home) │
│                                   │         │                                 │
└───────────────────────────────────┘         └─────────────────────────────────┘
```

## What Multi-Cluster Gives You

| Capability | Description |
|-----------|-------------|
| **Service mirroring** | Access company services from home cluster (and vice versa) |
| **Failover** | If home FastAPI dies, traffic routes to company automatically |
| **Data locality** | DB stays in company, app can run anywhere |
| **Disaster recovery** | Either cluster can serve traffic independently |

## How It Works

1. **WireGuard** provides network connectivity (Level 9)
2. **Linkerd Gateway** exposes services to other clusters
3. **Service Mirror** controller watches remote cluster and creates local mirror services
4. Apps call `service-name-remote` to reach the other cluster — transparently

## Setup

### 1. Link clusters (run on Home Lab)

```bash
# Generate link credentials from Company cluster
linkerd --context=company multicluster link --cluster-name company | \
  kubectl --context=home apply -f -

# Verify
linkerd --context=home multicluster check
```

### 2. Export services (on Company Lab)

```bash
# Mark postgres as exportable
kubectl --context=company label svc postgres mirror.linkerd.io/exported=true
```

### 3. Verify from Home Lab

```bash
# Should see mirrored service
kubectl --context=home get svc
# postgres-company   ClusterIP   ...

# Test connectivity
kubectl --context=home run test --rm -it --image=busybox -- wget -qO- postgres-company:5432
```

## Traffic Flow

```
Home Lab FastAPI
    │
    ▼ (calls postgres-company)
Linkerd Proxy (Home)
    │
    ▼ (mTLS over WireGuard tunnel)
Linkerd Gateway (Company)
    │
    ▼
PostgreSQL (Company Lab)
```

## Files

| File | Purpose |
|------|---------|
| `link-clusters.sh` | Script to link two clusters |
| `export-services.yaml` | Labels for service export |
| `README.md` | This file |

## Resource Requirements

| Component | Per Cluster |
|-----------|-------------|
| Linkerd Gateway | ~100MB RAM |
| Service Mirror controller | ~50MB RAM |
| **Additional over Level 11** | **~150MB** |

## Prerequisites Checklist

- [ ] Level 9: WireGuard tunnel working (ping 10.0.0.1 ↔ 10.0.0.2)
- [ ] Level 11: Linkerd installed on both clusters
- [ ] Both clusters can reach each other's API server (port 6443)
- [ ] `kubectl` contexts configured for both clusters
