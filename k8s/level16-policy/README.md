# Level 16 — Policy-as-Code (Kyverno)

Enforce security policies on the cluster — block unsafe deployments before they run.

## ✅ Status: COMPLETED (2026-05-18)

## Why

- Without policy: anyone can deploy privileged pods, skip resource limits, use `latest` tag
- With Kyverno: cluster rejects bad configs automatically

> Using **Kyverno** over OPA/Gatekeeper because it's K8s-native YAML (no Rego language to learn).

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

## Setup Commands (verified working)

```bash
# Install Kyverno
helm repo add kyverno https://kyverno.github.io/kyverno
helm install kyverno kyverno/kyverno -n kyverno --create-namespace

# Apply policy (deny-based — works correctly)
kubectl apply -f disallow-privileged.yaml

# Test — BLOCKED ✓
kubectl apply -f test-privileged-pod.yaml
# Error: "Privileged pods are not allowed."

# Test — ALLOWED ✓
kubectl run test-normal --image=nginx
# pod/test-normal created
```

## Incidents & Lessons Learned

### Incident 1: Pattern-based policy doesn't block pods without securityContext

- **Problem:** Policy v1 used `pattern` with `privileged: "!true"` but pod was still created
- **Cause:** When a pod has NO `securityContext` field at all, pattern matching `"!true"` doesn't trigger — it only checks if the field exists AND equals true
- **Fix:** Use `deny` with `conditions` instead of `pattern` — explicitly checks the value with fallback to `'false'`

### Incident 2: heredoc/herestring YAML issues in bash

- **Problem:** `kubectl apply -f - <<< 'yaml...'` with multi-line YAML fails or gets wrong indentation
- **Cause:** Terminal copy-paste adds inconsistent spaces; `<<<` is single-line only
- **Fix:** Always write to file first (`cat > /tmp/file.yaml <<'EOF'`) then `kubectl apply -f /tmp/file.yaml`

### Incident 3: `--overrides` flag split across lines

- **Problem:** `kubectl run --overrides='{...}'` didn't work — pod created without overrides
- **Cause:** Terminal wrapped the command into multiple lines, treating `--overrides` as a separate command
- **Fix:** Use YAML file instead of `--overrides` for complex pod specs

## Policy: disallow-privileged (working version)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-v2
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
      deny:
        conditions:
          any:
          - key: "{{ request.object.spec.containers[].securityContext.privileged || 'false' }}"
            operator: AnyIn
            value:
            - true
```

## Results

| Test | Expected | Actual |
|------|----------|--------|
| Pod with `privileged: true` | ❌ Blocked | ❌ Blocked ✓ |
| Pod without securityContext | ✅ Allowed | ✅ Allowed ✓ |
| Normal pod (nginx) | ✅ Allowed | ✅ Allowed ✓ |

## TODO

- [x] Install Kyverno on k3s
- [x] Apply disallow-privileged policy
- [x] Test: privileged pod → rejected
- [x] Test: normal pod → allowed
- [ ] Add require-resource-limits policy
- [ ] Add disallow-latest-tag policy (Audit mode)
- [ ] View policy reports: `kubectl get policyreport -A`
