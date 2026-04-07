# Kubernetes Level 5

## Topics
- StatefulSet + PersistentVolume (PostgreSQL)
- ConfigMap & Secret management
- RBAC (namespace-scoped)
- Helm multi-environment (dev/prod)

## Architecture
```
[FastAPI] → ConfigMap (APP_ENV, LOG_LEVEL, DB_HOST)
          → Secret    (DB_USER, DB_PASSWORD, SECRET_KEY)
          → PostgreSQL StatefulSet → PVC (2Gi, local-path)
[RBAC]    → fastapi-sa scoped to level5 namespace only
```

## Quick Deploy

### 1. Create Secret (never commit real values)
```bash
kubectl create secret generic fastapi-secret \
  --from-literal=DB_USER=postgres \
  --from-literal=DB_PASSWORD=yourpassword \
  --from-literal=SECRET_KEY=yoursecretkey \
  -n level5
```

### 2. Apply manifests
```bash
kubectl apply -f k8s/level5/configmap.yaml
kubectl apply -f k8s/level5/rbac/
kubectl apply -f k8s/level5/postgres/
kubectl apply -f k8s/level5/fastapi/
```

### 3. Helm multi-env
```bash
# Dev (port 32010)
helm upgrade --install fastapi-dev ./helm/fastapi \
  -f helm/values/values-dev.yaml -n level5-dev

# Prod (port 32011)
helm upgrade --install fastapi-prod ./helm/fastapi \
  -f helm/values/values-prod.yaml -n level5-prod
```

## RBAC Test
```bash
kubectl auth can-i get configmaps \
  --as=system:serviceaccount:level5:fastapi-sa -n level5  # yes
kubectl auth can-i delete pods \
  --as=system:serviceaccount:level5:fastapi-sa -n level5  # no
```
