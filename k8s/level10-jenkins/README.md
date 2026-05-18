# Level 10 — Jenkins (Self-Hosted CI)

Self-hosted Jenkins on k3s — compare with GitHub Actions for CI/CD pipeline.

## Architecture

```
┌─── k3s Cluster ─────────────────────────────────────┐
│                                                       │
│  ┌─────────────┐    ┌─────────────┐                 │
│  │ Jenkins     │───►│ Jenkins     │                 │
│  │ Controller  │    │ Agent (pod) │                 │
│  │ (StatefulSet)│    └─────────────┘                 │
│  └──────┬──────┘                                     │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐    ┌─────────────┐                 │
│  │ Build image │───►│ Push to     │───► Deploy      │
│  │ (Kaniko)    │    │ GHCR        │    (ArgoCD)     │
│  └─────────────┘    └─────────────┘                 │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## Comparison: Jenkins vs GitHub Actions

| Feature | GitHub Actions | Jenkins |
|---------|---------------|---------|
| Hosting | GitHub-managed | Self-hosted (k3s) |
| Cost | Free (2000 min/mo) | Free (your infra) |
| Config | YAML in repo | Jenkinsfile in repo |
| Plugins | Marketplace | 1800+ plugins |
| Scaling | GitHub runners | Dynamic k8s agents |
| Secrets | GitHub Secrets | Credentials store |
| Learning | Easy | Steeper curve |

## Files

| File | Purpose |
|------|---------|
| `jenkins-values.yaml` | Helm values for Jenkins on k3s |
| `Jenkinsfile.example` | Pipeline: build → push → deploy |
| `README.md` | This file |

## Setup

```bash
# Install Jenkins via Helm
helm repo add jenkins https://charts.jenkins.io
helm repo update

helm install jenkins jenkins/jenkins \
  -n jenkins --create-namespace \
  -f jenkins-values.yaml

# Get admin password
kubectl exec -n jenkins svc/jenkins -c jenkins -- cat /run/secrets/chart-admin-password

# Access UI
kubectl port-forward -n jenkins svc/jenkins 8080:8080
# http://localhost:8080
```

## Pipeline (Jenkinsfile)

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
            spec:
              containers:
              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command: ['sleep', 'infinity']
            '''
        }
    }
    stages {
        stage('Build & Push') {
            steps {
                container('kaniko') {
                    sh '/kaniko/executor --context . --destination ghcr.io/derbswag/devops-api:${BUILD_NUMBER}'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl set image deployment/fastapi fastapi=ghcr.io/derbswag/devops-api:${BUILD_NUMBER}'
            }
        }
    }
}
```

## Resource Requirements

| Component | CPU | RAM |
|-----------|-----|-----|
| Jenkins Controller | 500m | 1Gi |
| Jenkins Agent (per build) | 500m | 512Mi |
| **Total minimum** | **1 core** | **2Gi** |
