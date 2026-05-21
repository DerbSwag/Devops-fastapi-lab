# Level 11 — Service Mesh (Linkerd)

## ⚠️ Status: ATTEMPTED — Not Compatible with Current Setup (2026-05-21)

## Incident: Linkerd Proxy Bootstrap Failure on k3s

### Problem
Linkerd control plane pods (destination, proxy-injector) fail to start because the proxy sidecar cannot obtain identity certificates during bootstrap.

### Root Cause
Circular dependency:
1. Proxy sidecar needs identity certificate from `linkerd-identity` service
2. To reach `linkerd-identity`, proxy needs DNS resolution
3. Linkerd's init container redirects ALL traffic (including DNS) through the proxy
4. Proxy can't start without identity → DNS fails → identity unreachable → deadlock

### Attempted Fixes
| Fix | Result |
|-----|--------|
| `--set proxyInit.ignoreOutboundPorts=53` | identity + proxy-injector came up, destination still failed |
| `--set proxy.nativeSidecar=false` | Same result |
| Linkerd edge (26.5.2) | Failed |
| Linkerd stable (2.14.10) | Same failure |

### Environment
- k3s v1.31 (single control plane, 3 nodes)
- CoreDNS as cluster DNS
- NetworkPolicy active (but linkerd namespace has no policies)

### Conclusion
Linkerd's proxy-in-control-plane architecture has a bootstrap problem on k3s where DNS resolution timing is critical. This is a known issue in resource-constrained environments.

### Alternative Options (Future)
1. **Istio ambient mode** — no sidecar, uses ztunnel (node-level proxy)
2. **Cilium service mesh** — eBPF-based, no sidecar needed
3. **Linkerd with HA mode** on larger cluster (more RAM/nodes)

### Lessons Learned
1. Service mesh adds complexity — not always worth it for small clusters
2. Proxy sidecar in control plane creates circular dependency
3. Always check compatibility matrix before installing
4. Document failures — they show real debugging experience

---

## Original Plan (for reference)

### Architecture
```
┌─── k3s Cluster with Linkerd ────────────────────────────┐
│  Linkerd Control Plane                                    │
│  ├── destination (service discovery)                      │
│  ├── identity (mTLS certificate authority)                │
│  └── proxy-injector (sidecar injection)                   │
│                                                           │
│  ┌─────────┐  mTLS   ┌─────────┐                        │
│  │ FastAPI │◄───────►│ Postgres│                        │
│  │ + proxy │         │ + proxy │                        │
│  └─────────┘         └─────────┘                        │
└───────────────────────────────────────────────────────────┘
```

### What Service Mesh Would Give
- mTLS between all pods (automatic)
- Golden metrics (latency, success rate, RPS)
- Traffic splitting for canary deploys
- Service-to-service identity
