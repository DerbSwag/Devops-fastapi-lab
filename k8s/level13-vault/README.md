# Level 13 — HashiCorp Vault (Secret Management)

Secure secret injection into pods — replace K8s Secrets (base64) with Vault.

## ✅ Status: COMPLETED (2026-05-18)

## Why

- K8s Secrets = base64 encoded (NOT encrypted)
- Vault = encrypted at rest, audit log, auto-rotation, dynamic secrets

## Architecture

```
┌─── k3s ──────────────────────────────────────┐
│                                                │
│  Vault Server (dev mode)                       │
│       │                                        │
│       ▼                                        │
│  Vault Agent Injector (sidecar)                │
│       │                                        │
│       ▼                                        │
│  FastAPI Pod                                   │
│  ├── /vault/secrets/db-creds  (auto-injected) │
│  └── App reads file, no env vars exposed       │
│                                                │
└────────────────────────────────────────────────┘
```

## Setup Commands (verified working)

```bash
# Install Vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault \
  -n vault --create-namespace \
  --set "server.dev.enabled=true" \
  --set "injector.enabled=true"

# Store secret (exec into vault pod)
kubectl -n vault exec -it vault-0 -- vault kv put secret/fastapi/db \
  username="fastapi_user" password="SuperSecret123"

# Enable K8s auth
kubectl -n vault exec -it vault-0 -- vault auth enable kubernetes
kubectl -n vault exec -it vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

# Create policy
kubectl -n vault exec -it vault-0 -- vault policy write fastapi-policy - \
  <<< 'path "secret/data/fastapi/*" { capabilities = ["read"] }'

# Create role
kubectl -n vault exec -it vault-0 -- vault write auth/kubernetes/role/fastapi \
  bound_service_account_names=fastapi-sa \
  bound_service_account_namespaces=default \
  policies=fastapi-policy ttl=1h

# Create ServiceAccount
kubectl create serviceaccount fastapi-sa -n default

# Deploy with Vault injection
kubectl apply -f fastapi-vault.yaml

# Verify
kubectl exec deploy/fastapi-vault -c app -- cat /vault/secrets/db-creds
# Output: data: map[password:SuperSecret123 username:fastapi_user]
```

## Incidents & Lessons Learned

### Incident 1: `vault` command not found on k8s-master
- **Problem:** Ran `vault` commands on k8s-master node instead of inside vault pod
- **Cause:** `vault` CLI is only available inside the vault-0 pod
- **Fix:** Use `kubectl -n vault exec -it vault-0 -- vault <command>` or exec into pod first

### Incident 2: heredoc `<<EOF` fails inside vault pod (ash shell)
- **Problem:** `vault policy write fastapi-policy - <<EOF` produced parse error
- **Cause:** Vault pod uses `ash` (Alpine) which handles heredoc differently
- **Fix:** Use `<<<` (herestring) from k8s-master: `kubectl -n vault exec ... -- vault policy write fastapi-policy - <<< 'policy content'`

### Incident 3: YAML heredoc EOF not closing
- **Problem:** `cat > file << 'EOF'` never closed, stuck at `>` prompt
- **Cause:** `EOF` had leading spaces (must be at column 0)
- **Fix:** Ensure `EOF` is flush-left with no indentation

## Results

| Metric | Value |
|--------|-------|
| Secret injection | ✅ Working via sidecar |
| Auth method | Kubernetes (ServiceAccount) |
| Policy | Read-only on `secret/data/fastapi/*` |
| No K8s Secrets used | ✅ Zero base64 secrets |
| Setup time | ~15 minutes |

## TODO

- [x] Install Vault on k3s (dev mode)
- [x] Enable KV v2 engine
- [x] Store DB credentials
- [x] Configure Kubernetes auth method
- [x] Inject secrets into FastAPI pod via annotation
- [x] Verify: pod reads secret from /vault/secrets/
- [ ] (Advanced) Dynamic PostgreSQL credentials
- [ ] (Advanced) Secret rotation with TTL
