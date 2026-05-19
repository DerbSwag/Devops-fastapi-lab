# Incident: First Run — Terraform & Ansible Setup Issues

**Date:** 2026-05-19
**Severity:** Low (lab setup, no production impact)
**Resolved:** 2026-05-19

## Summary

First time running Terraform and Ansible on actual infrastructure. Multiple issues encountered and resolved.

## Terraform Issues

### Issue 1: `terraform plan` hangs waiting for input
- **Problem:** Plan prompts for `var.key_name` interactively
- **Cause:** No `terraform.tfvars` file with required variables
- **Fix:** Create `terraform.tfvars` with `key_name` and `allowed_ssh_cidr`

### Issue 2: State lock from cancelled plan
- **Problem:** `terraform plan` fails with "state lock" error
- **Cause:** Previous `terraform plan` was cancelled mid-execution
- **Fix:** `terraform force-unlock` + remove `.terraform.tfstate.lock.info`

### Issue 3: AMI not found
- **Problem:** `data.aws_ami.ubuntu` returns no results
- **Cause:** Ubuntu 24.04 uses `hvm-ssd-gp3` not `hvm-ssd` in AMI name
- **Fix:** Change filter from `ubuntu/images/hvm-ssd/ubuntu-*-24.04` to `ubuntu/images/hvm-ssd-gp3/ubuntu-*-24.04`

### Issue 4: No SSH key pair on AWS
- **Problem:** EC2 instance needs key pair that doesn't exist
- **Fix:** `aws ec2 create-key-pair --key-name devops-lab-key`

## Ansible Issues

### Issue 1: SSH key not distributed
- **Problem:** `ansible all -m ping` fails — "Permission denied (publickey)"
- **Cause:** No SSH key existed on k8s-master, and key not copied to other nodes
- **Fix:** Generate ed25519 key + `sshpass` + `ssh-copy-id` to all nodes

### Issue 2: deploy-fastapi.yml — GHCR image denied
- **Problem:** Docker pull fails — "denied: permission denied"
- **Cause:** GHCR image is private, no docker login on target
- **Impact:** Non-critical — playbook logic works, just needs registry auth

### Issue 3: Node Exporter port conflict
- **Problem:** setup-monitoring.yml fails on node-exporter container
- **Cause:** Port 9100 already in use (existing node-exporter from kube-prometheus-stack)
- **Impact:** Non-critical — monitoring already running via K8s

### Issue 4: SSH service name mismatch
- **Problem:** harden-server.yml fails to restart SSH
- **Cause:** Playbook uses `sshd` but Ubuntu 24.04 service is named `ssh`
- **Impact:** Non-critical — hardening rules applied, just restart skipped

## Terraform Apply & Destroy

### Issue 5: GHCR image pull denied on EC2
- **Problem:** user_data deploys `ghcr.io/derbswag/devops-fastapi-lab:latest` but image is private
- **Fix:** Replaced with public image (`kennethreitz/httpbin`) for demo
- **Lesson:** Either make GHCR package public or add docker login to user_data

### Issue 6: `tiangolo/uvicorn-gunicorn-fastapi` returns 502
- **Problem:** Container starts but no app code inside — returns empty response
- **Cause:** Base image needs app code mounted/copied in
- **Fix:** Used `kennethreitz/httpbin` which works standalone

### Successful Deploy
```
terraform apply → 7 resources created in <1 min
- VPC + Subnet + IGW + Route Table
- Security Group (SSH + HTTP + 8000)
- EC2 t3.micro (Docker + app via user_data)
- App accessible at http://<public-ip>:8000 ✅
```

### Destroy
```
terraform destroy → 7 resources destroyed in <30s
- No leftover resources, no ongoing cost
```

## Results

| Component | Status |
|-----------|--------|
| Terraform plan | ✅ 7 resources planned |
| Terraform apply | ✅ 7 resources created, app accessible |
| Terraform destroy | ✅ 7 resources destroyed, no cost |
| Ansible ping (6 nodes) | ✅ All reachable |
| setup-docker.yml | ✅ Success (3 nodes) |
| deploy-fastapi.yml | ⚠️ Partial (registry auth needed) |
| setup-monitoring.yml | ⚠️ Partial (port conflict) |
| harden-server.yml | ⚠️ Partial (service name) |

## Lessons Learned

1. **Always create `terraform.tfvars`** before first plan — don't rely on interactive prompts
2. **AMI naming changes between Ubuntu versions** — verify filter matches current naming convention
3. **SSH key distribution is prerequisite** for Ansible — automate with `ssh-copy-id` or cloud-init
4. **Port conflicts expected** when running Ansible on nodes that already have K8s monitoring
5. **Service names differ between distros** — Ubuntu uses `ssh`, RHEL uses `sshd`
