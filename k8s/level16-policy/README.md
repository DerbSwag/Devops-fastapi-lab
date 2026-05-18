# Level 16 — Policy-as-Code (Kyverno)

Enforce security policies on the cluster — block unsafe deployments before they run.

## Why

- Without policy: anyone can deploy privileged pods, skip resource limits, use `latest` tag
- With Kyverno: cluster rejects bad configs automatically

> Using **Kyverno** over OPA/Gatekeeper because it's K8s-native YAML (no Rego language to learn).

## Policies

| Policy | What it blocks | Severity |
|--------|---------------|----------|
| **Disallow privileged** | Pods with `privileged: true` | 🔴 Block |
| **Require resource limits** | Pods without CPU/RAM limits | 🔴 Block |
| **Disallow latest tag** | Images using `:latest` | 🟡 Warn |
| **Require labels** | Pods without `app` and `team` labels | 🟡 Warn |
| **Disallow host network** | Pods using `hostNetwork: true` | 🔴 Block |

## Architecture

```
kubectl apply (new pod)
       │
       ▼
Kyverno Admission Controller
       │
       ├── Policy check PASS → Pod created ✓
       │
       └── Policy check FAIL → Pod rejected ✗
                                (error message returned)
```

## Setup

```bash
helm repo add kyverno https://kyverno.github.io/kyverno
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

## Example: Disallow Privileged Pods

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged
spec:
  validationFailureAction: Enforce
  rules:
  - name: deny-privileged
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Privileged pods are not allowed."
      pattern:
        spec:
          containers:
          - securityContext:
              privileged: "!true"
```

## Example: Require Resource Limits

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-limits
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-limits
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "CPU and memory limits are required."
      pattern:
        spec:
          containers:
          - resources:
              limits:
                memory: "?*"
                cpu: "?*"
```

## TODO

- [ ] Install Kyverno on k3s
- [ ] Apply disallow-privileged policy
- [ ] Test: try deploying privileged pod → should be rejected
- [ ] Apply require-limits policy
- [ ] Apply disallow-latest-tag policy (Audit mode first)
- [ ] View policy reports: `kubectl get policyreport -A`
