# DevOps FastAPI Lab 🚀

This project demonstrates a **modern DevOps stack** using a FastAPI application deployed with Docker and monitored using Prometheus and Grafana.

The goal of this lab is to simulate a **real DevOps environment** including containerization, reverse proxy, monitoring, and CI/CD automation.

---

# Architecture

```
Client
  │
  ▼
Nginx Reverse Proxy
  │
  ▼
FastAPI Application (Docker)
  │
  ▼
Prometheus ──► Grafana Dashboard
  │
  ├── Node Exporter (Host Metrics)
  └── cAdvisor (Container Metrics)
```

---

# Tech Stack

### Application

* FastAPI
* Python

### Containerization

* Docker
* Docker Compose

### Reverse Proxy

* Nginx

### Monitoring & Metrics

* Prometheus
* Grafana
* Node Exporter
* cAdvisor
* Alertmanager

### DevOps Tools

* Git
* GitHub Actions (CI Pipeline)

---

# Project Structure

```
.
├── app
│   ├── main.py
│   └── requirements.txt
│
├── docker
│   └── Dockerfile
│
├── compose
│   ├── app.yml
│   └── monitoring.yml
│
├── monitoring
│   ├── alertmanager
│   │   └── alertmanager.yml
│   │
│   ├── grafana
│   │   ├── dashboards
│   │   └── provisioning
│   │
│   └── prometheus
│       ├── prometheus.yml
│       └── alerts.yml
│
├── nginx
│   └── my-api.conf
│
├── scripts
│   ├── deploy.sh
│   └── setup.sh
│
└── README.md
```

---

# Getting Started

## Clone repository

```
git clone https://github.com/DerbSwag/devops-fastapi-lab.git
cd devops-fastapi-lab
```

---

## Run Application

Start FastAPI application

```
docker compose -f compose/app.yml up -d
```

Start monitoring stack

```
docker compose -f compose/monitoring.yml up -d
```

---

# Service URLs

| Service       | URL                   |
| ------------- | --------------------- |
| FastAPI       | http://localhost:8000 |
| Nginx         | http://localhost      |
| Prometheus    | http://localhost:9090 |
| Grafana       | http://localhost:3000 |
| Alertmanager  | http://localhost:9093 |
| Node Exporter | http://localhost:9100 |

---

# Grafana Login

```
Username: admin
Password: admin
```

---

# CI Pipeline

GitHub Actions automatically runs when code is pushed to the **main branch**.

Pipeline steps:

```
1. Checkout repository
2. Build Docker image
3. Verify Docker build
```

Workflow file:

```
.github/workflows/docker.yml
```

---

# Monitoring Stack

Metrics are collected from:

* **Node Exporter** → Host metrics (CPU / RAM / Disk)
* **cAdvisor** → Container metrics
* **Prometheus** → Time-series metrics storage
* **Grafana** → Visualization dashboards

---

# Example Dashboards

Grafana dashboards visualize:

* CPU usage
* Memory usage
* Disk usage
* Container metrics
* System uptime

---

# Alerting

Alertmanager is used to handle alerts from Prometheus.

Example alerts:

* High CPU usage
* High memory usage
* Instance down

Configuration:

```
monitoring/prometheus/alerts.yml
monitoring/alertmanager/alertmanager.yml
```

---

# DevOps Features Demonstrated

* Containerized microservice
* Reverse proxy architecture
* Infrastructure monitoring
* Metrics visualization
* Alert management
* CI pipeline automation

---

# Future Improvements

Possible enhancements for this lab:

* CD deployment pipeline
* Docker image push to registry
* Loki logging stack
* OpenTelemetry tracing
* Kubernetes deployment
* Terraform infrastructure provisioning

---

# License

MIT License
