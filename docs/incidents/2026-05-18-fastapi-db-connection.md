# Incident Report: FastAPI DB Connection Failure

**Date:** 2026-05-18  
**Duration:** ~1.5 hours (20:15 - 21:50)  
**Severity:** Medium (app degraded, not fully down — healthz OK, readyz failed)  
**Affected:** FastAPI pods in `default` namespace (readiness probe failing)

---

## Summary

FastAPI pods ใน default namespace ไม่สามารถเชื่อมต่อ PostgreSQL (level5 namespace) ได้ ทำให้ readiness probe fail → pods แสดง 1/2 Ready → ArgoCD report Degraded

---

## Root Causes (3 ปัญหาซ้อนกัน)

### 1. Password มี special character ไม่ได้ URL-encode

- `DB_PASSWORD=p@ssw0rd` ถูกใส่ใน connection string ตรงๆ
- ตัว `@` ทำให้ asyncpg parse URL ผิด → ตีความ host เป็น `ssw0rd@postgres-0.postgres-service...`
- ผลลัพธ์: `gaierror: Name or service not known`

### 2. Password ใน default namespace ไม่ตรงกับ PostgreSQL จริง

- Secret ใน `default` namespace: `DB_PASSWORD=p@ssw0rd`
- Secret ใน `level5` namespace (ที่ postgres ใช้): `DB_PASSWORD=devpassword123`
- ผลลัพธ์: `InvalidPasswordError: password authentication failed`

### 3. asyncpg SSL + Linkerd proxy interference

- Code เดิมใช้ `?ssl=disable` ใน URL → asyncpg ไม่รู้จัก param นี้
- asyncpg default behavior คือ `prefer` SSL → พยายาม SSL connection ก่อน
- Linkerd sidecar intercept outbound TCP → DNS resolution ผ่าน proxy ล้มเหลวสำหรับ headless service ข้าม namespace

---

## Additional Issue: ArgoCD repo-server

- `argocd-repo-server` pod ค้างใน status `Unknown` หลัง node reboot
- init container `copyutil` เข้า CrashLoopBackOff
- ทำให้ ArgoCD sync status เป็น `Unknown` / health `Degraded`

---

## Resolution

### ArgoCD
```bash
kubectl delete pod argocd-repo-server-75f8589995-lrbfd -n argocd --force --grace-period=0
```
→ Pod recreate สำเร็จ, ArgoCD กลับมา Synced

### FastAPI DB Connection

**1. Fix URL-encoding (code change → pushed to GitHub)**
```python
# Before
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# After
from urllib.parse import quote_plus
DATABASE_URL = f"postgresql+asyncpg://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

**2. Fix SSL handling (code change)**
```python
import ssl as _ssl
_connect_args = {"ssl": False} if DB_SSLMODE == "disable" else {}
engine = create_async_engine(DATABASE_URL, pool_size=5, max_overflow=5, connect_args=_connect_args)
```

**3. Fix password mismatch (secret update)**
```bash
kubectl create secret generic fastapi-secret -n default \
  --from-literal=DB_PASSWORD=devpassword123 \
  --from-literal=API_KEY=my-super-secret-key-123 \
  --dry-run=client -o yaml | kubectl apply -f -
```

**4. Fix DB_HOST (configmap — use IP to bypass Linkerd DNS issue)**
```bash
kubectl create configmap fastapi-config -n default \
  --from-literal=DB_HOST=10.42.0.163 \
  --from-literal=DB_SSLMODE=disable \
  ... --dry-run=client -o yaml | kubectl apply -f -
```

---

## Commits

| Commit | Description |
|--------|-------------|
| `4fc23ce` | fix: use sslmode instead of ssl param for asyncpg |
| `1be1b21` | fix: use connect_args for asyncpg SSL |
| `7a9b0ef` | fix: explicitly pass ssl=False to asyncpg |
| `3e7ad9c` | fix: use ssl=false URL param |
| `ac6e6ca` | fix: pass ssl=False via connect_args (no URL params) |
| `39c563f` | fix: URL-encode DB credentials to handle special chars |

---

## Lessons Learned

1. **Always URL-encode credentials** — special chars (`@`, `#`, `%`) break connection string parsing
2. **Secrets ต้อง sync ข้าม namespace** — ถ้า app ใน namespace A ต่อ DB ใน namespace B ต้องมั่นใจว่า credentials ตรงกัน
3. **asyncpg + SQLAlchemy SSL** — ไม่สามารถใช้ URL query param สำหรับ SSL ได้ ต้องใช้ `connect_args={"ssl": False}`
4. **Linkerd + headless service** — Linkerd proxy intercept DNS/TCP สำหรับ headless service ข้าม namespace ได้ไม่ดี ใช้ `skip-outbound-ports` หรือ IP ตรง
5. **ArgoCD repo-server** — ถ้าค้างหลัง reboot ให้ force delete pod

---

## Final Fix (2026-05-19)

หลังจาก hotfix เมื่อวาน ได้ทำ permanent fix โดยย้าย configmap/secret เข้า Helm chart:

**1. สร้าง Helm templates สำหรับ configmap + secret**
- `helm/fastapi/templates/configmap.yaml`
- `helm/fastapi/templates/secret.yaml`

**2. อัปเดต `helm/fastapi/values.yaml`**
```yaml
podAnnotations:
  linkerd.io/inject: enabled
  config.linkerd.io/skip-outbound-ports: "5432"   # ← เพิ่มใหม่

config:
  DB_HOST: postgres-0.postgres-service.level5.svc.cluster.local  # ← DNS แทน IP
  DB_SSLMODE: disable

secret:
  DB_PASSWORD: devpassword123  # ← password ที่ถูกต้อง
```

**3. ลบ configmap/secret เก่าที่สร้างมือ → ArgoCD recreate จาก Helm**

**ผลลัพธ์:** Pod 2/2 Ready, readyz 200 OK, ArgoCD Synced+Healthy, DB_HOST เป็น DNS (ไม่ต้องแก้ถ้า postgres restart ได้ IP ใหม่)

**Commit:** `48d5b0c` — feat(helm): add configmap/secret templates, fix Linkerd skip-outbound-ports, DNS-based DB_HOST

---

## Prevention

- [x] ~~เพิ่ม CI test ที่ validate DB connection string format~~ → แก้ด้วย `quote_plus()` ใน code
- [x] ~~ใช้ Sealed Secrets หรือ External Secrets Operator~~ → ย้าย secret เข้า Helm chart (managed by ArgoCD)
- [ ] พิจารณาย้าย PostgreSQL มาอยู่ใน default namespace หรือใช้ ClusterIP service แทน headless
- [ ] เพิ่ม alerting rule สำหรับ pod readiness failure > 5 minutes
