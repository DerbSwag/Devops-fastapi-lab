# DevOps FastAPI Lab

This project demonstrates a DevOps stack using FastAPI and Docker.

## Stack

- FastAPI
- Docker
- Docker Compose
- Nginx Reverse Proxy
- Prometheus Monitoring
- Grafana Dashboard
- Node Exporter
- cAdvisor

## Architecture

Client
  ↓
Nginx (HTTPS)
  ↓
FastAPI (Docker)
  ↓
Prometheus → Grafana
