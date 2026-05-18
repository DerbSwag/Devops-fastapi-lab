# Level 17 — Backup & Disaster Recovery (Velero)

Backup entire k8s cluster state + persistent volumes → restore anywhere.

## Why

- Node dies → all StatefulSet data gone (without backup)
- Accidental `kubectl delete ns` → everything lost
- Velero = snapshot cluster state + PVs → restore in minutes

## Architecture

```
┌─── k3s ──────────────────────┐         ┌─── Backup Storage ───┐
│                               │         │                       │
│  Velero Server                │────────►│  MinIO (S3-compatible)│
│  (runs as deployment)         │  backup │  or AWS S3            │
│                               │         │                       │
│  Resources backed up:         │         │  Stored:              │
│  - Deployments, Services      │         │  - cluster-state.tar  │
│  - ConfigMaps, Secrets        │         │  - pv-snapshots/      │
│  - PersistentVolumes          │         │                       │
│  - Helm releases              │         └───────────────────────┘
│                               │
└───────────────────────────────┘

Restore: velero restore create --from-backup <name>
→ All resources recreated (even on a fresh cluster)
```

## Setup (with MinIO as local S3)

```bash
# 1. Install MinIO (local S3-compatible storage)
kubectl apply -f minio.yaml

# 2. Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.0 \
  --bucket velero-backups \
  --secret-file ./minio-credentials \
  --backup-location-config region=minio,s3ForcePathStyle=true,s3Url=http://minio.velero:9000 \
  --use-node-agent

# 3. Verify
velero get backup-locations
```

## Usage

```bash
# Backup entire cluster
velero backup create full-backup --include-namespaces default,monitoring

# Backup on schedule (daily at 2am)
velero schedule create daily --schedule="0 2 * * *" --include-namespaces default,monitoring

# List backups
velero get backups

# Restore (disaster recovery)
velero restore create --from-backup full-backup

# Restore single namespace
velero restore create --from-backup full-backup --include-namespaces default
```

## Disaster Recovery Test

| Step | Action | Expected |
|------|--------|----------|
| 1 | `velero backup create test-backup` | Backup completes |
| 2 | `kubectl delete ns default` | Everything gone |
| 3 | `velero restore create --from-backup test-backup` | All resources restored |
| 4 | Verify pods running, PV data intact | ✅ |

## TODO

- [ ] Deploy MinIO on k3s (or use existing S3)
- [ ] Install Velero
- [ ] Create manual backup
- [ ] Test restore (delete namespace → restore)
- [ ] Set up daily schedule
- [ ] Verify PV snapshot/restore (PostgreSQL data)
- [ ] Document RTO/RPO (Recovery Time/Point Objective)
