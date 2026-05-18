# Level 13 — HashiCorp Vault (Secret Management)

Secure secret injection into pods — replace K8s Secrets (base64) with Vault.

## Why

- K8s Secrets = base64 encoded (NOT encrypted)
- Vault = encrypted at rest, audit log, auto-rotation, dynamic secrets

## Architecture

```
┌─── k3s ──────────────────────────────────────┐
│                                                │
│  Vault Server (dev mode or HA)                 │
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

## Setup

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault -n vault --create-namespace \
  --set "server.dev.enabled=true" \
  --set "injector.enabled=true"
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **KV Engine** | Key-value store for static secrets |
| **Dynamic Secrets** | Auto-generated DB credentials (TTL-based) |
| **Agent Injector** | Sidecar that writes secrets to pod filesystem |
| **Auth Method** | Kubernetes auth — pods authenticate via ServiceAccount |
| **Policy** | Fine-grained access control per namespace/app |

## TODO

- [ ] Install Vault on k3s (dev mode)
- [ ] Enable KV v2 engine
- [ ] Store DB credentials
- [ ] Configure Kubernetes auth method
- [ ] Inject secrets into FastAPI pod via annotation
- [ ] Verify: pod reads secret from /vault/secrets/
- [ ] (Advanced) Dynamic PostgreSQL credentials
