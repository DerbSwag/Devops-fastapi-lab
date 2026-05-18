# Level 15 — Chaos Engineering

Test system resilience by injecting failures — prove your setup survives real-world problems.

## ✅ Status: COMPLETED (2026-05-18)

## Why

- "It works" ≠ "It's resilient"
- Chaos testing proves: HPA works, self-heal works, alerts fire correctly
- Netflix invented this (Chaos Monkey) — now standard in SRE

## Results

| Test | Method | Result |
|------|--------|--------|
| **Pod Delete** | `kubectl delete pod -l app=fastapi` | ✅ New pod Running in **8 seconds** |
| **CPU Stress / HPA** | Verified in Level 7 | ✅ 199% CPU → scaled 1→**6 pods** |
| **Self-heal** | K8s ReplicaSet controller | ✅ Automatic, no intervention |

## Chaos Tests Performed

### Test 1: Pod Delete (Self-Heal)

```bash
# Kill the fastapi pod
kubectl delete pod -l app=fastapi

# Watch recovery
kubectl get pods -w
```

**Output:**
```
fastapi-7c9f5b8c5-2dfgx   0/1   ContainerCreating   0   6s
fastapi-7c9f5b8c5-2dfgx   1/1   Running             0   8s
```

Recovery time: **8 seconds** ✅

### Test 2: CPU Stress (HPA Auto-Scale)

From Level 7 (verified with stress test):
```
CPU spike: 199%
Pods scaled: 1 → 6 (automatic)
Scale-down after load: 6 → 1 (after cooldown)
```

## Incidents & Lessons Learned

### Incident 1: Litmus ChaosCenter MongoDB CrashLoopBackOff

- **Problem:** `helm install litmus` succeeded but MongoDB pods kept crashing
- **Cause:** Litmus ChaosCenter requires MongoDB which needs more RAM than available on k3s node
- **Fix:** Skip ChaosCenter UI — use manual chaos tests instead. Same validation, zero overhead.
- **Lesson:** Heavy tooling isn't always needed. `kubectl delete pod` is a valid chaos test.

### Incident 2: Kyverno blocked Litmus installation

- **Problem:** Litmus pods use `privileged: true` in securityContext — Kyverno policy blocked them
- **Cause:** Level 16 policy (disallow-privileged) was active and applied cluster-wide
- **Fix:** Added namespace exclusion (`litmus`, `kube-system`, `vault`) to Kyverno policy
- **Lesson:** Policy-as-Code can block legitimate tools. Always exclude system namespaces.

### Incident 3: stress tool not available in FastAPI container

- **Problem:** `apt install stress` failed — permission denied (non-root container)
- **Cause:** FastAPI image runs as non-root user, no package manager access
- **Fix:** Use `polinux/stress` as separate pod, or Python CPU burn script
- **Lesson:** Production containers should be minimal — chaos tools run as separate pods

### Incident 4: HPA shows `<unknown>` for stress pod

- **Problem:** Ran stress in separate pod but HPA didn't react
- **Cause:** HPA monitors `deploy/fastapi` CPU only — separate pod doesn't count
- **Fix:** Must stress the target deployment directly, or reference Level 7 results
- **Lesson:** HPA is scoped to specific deployment, not node-wide CPU

## Approach: Manual Chaos vs Litmus

| | Litmus ChaosCenter | Manual Chaos |
|---|---|---|
| Setup | Heavy (MongoDB + 5 pods) | Zero setup |
| RAM needed | ~2GB+ | 0 |
| Validation | Same | Same |
| Portfolio value | Looks fancy | Shows understanding |
| Recommended for | Large clusters | k3s / resource-limited |

## TODO

- [x] Attempt Litmus install (documented failure + reason)
- [x] Pod delete chaos test — verify self-heal
- [x] CPU stress — verify HPA (from Level 7)
- [x] Document incidents and lessons
- [ ] (Future) Network delay test with `tc` command
- [ ] (Future) Node drain test (multi-node cluster)
