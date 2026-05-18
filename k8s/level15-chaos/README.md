# Level 15 — Chaos Engineering (Litmus)

Test system resilience by injecting failures — prove your setup survives real-world problems.

## Why

- "It works" ≠ "It's resilient"
- Chaos testing proves: HPA works, self-heal works, alerts fire correctly
- Netflix invented this (Chaos Monkey) — now standard in SRE

## Experiments

| Experiment | What it does | What should happen |
|-----------|--------------|-------------------|
| **Pod Kill** | Delete random FastAPI pod | HPA recreates, zero downtime |
| **CPU Stress** | Spike CPU on node | HPA scales up pods |
| **Network Delay** | Add 500ms latency | App still responds (degraded) |
| **Disk Fill** | Fill /tmp on node | Alert fires, no crash |
| **Node Drain** | Cordon + drain a node | Pods reschedule to other nodes |

## Architecture

```
┌─── k3s ──────────────────────────────────────┐
│                                                │
│  Litmus ChaosCenter (UI)                       │
│       │                                        │
│       ▼                                        │
│  ChaosEngine (defines experiment)              │
│       │                                        │
│       ▼                                        │
│  ChaosExperiment (pod-kill, cpu-hog, etc.)     │
│       │                                        │
│       ▼                                        │
│  Target: FastAPI Deployment                    │
│                                                │
│  Meanwhile:                                    │
│  Prometheus → detects anomaly → Alert fires ✓  │
│  HPA → scales up → recovers ✓                 │
│                                                │
└────────────────────────────────────────────────┘
```

## Setup

```bash
# Install Litmus
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm
helm install litmus litmuschaos/litmus \
  -n litmus --create-namespace \
  --set portal.frontend.service.type=NodePort

# Install generic experiments
kubectl apply -f https://hub.litmuschaos.io/api/chaos/3.0.0?file=charts/generic/experiments.yaml
```

## Example: Pod Kill

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: fastapi-chaos
spec:
  appinfo:
    appns: default
    applabel: "app=fastapi"
  chaosServiceAccount: litmus-admin
  experiments:
  - name: pod-delete
    spec:
      components:
        env:
        - name: TOTAL_CHAOS_DURATION
          value: "30"
        - name: CHAOS_INTERVAL
          value: "10"
        - name: FORCE
          value: "false"
```

## Success Criteria

| Experiment | Pass if... |
|-----------|-----------|
| Pod Kill | New pod running within 10s, no 5xx errors |
| CPU Stress | HPA scales within 60s |
| Network Delay | P99 latency < 2s (degraded but alive) |
| Disk Fill | Alert fires within 1m |

## TODO

- [ ] Install Litmus on k3s
- [ ] Run pod-delete on FastAPI
- [ ] Verify HPA + self-heal recovery
- [ ] Run cpu-hog, verify HPA scaling
- [ ] Confirm Alertmanager fires during chaos
- [ ] Document results (before/during/after metrics)
