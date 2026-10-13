# Self-Healing Microservices on Kubernetes

A containerised microservices application demonstrating **Kubernetes self-healing, health monitoring, CPU-based autoscaling, load testing, and observability with Prometheus and Grafana**.

## Overview

This project explores how Kubernetes can maintain the availability of a microservices application when Pods fail and how it can scale application replicas in response to increased CPU utilisation.

The application consists of three Python Flask services deployed to a local Kubernetes cluster using Minikube. Prometheus collects infrastructure metrics, Grafana visualises system behaviour, and k6 generates HTTP traffic to test the application under load.

## Architecture

```text
                 Client
                   |
                   v
             API Gateway
              Port 5000
              /       \
             v         v
       User Service  Order Service
        Port 5001     Port 5002

       Kubernetes Cluster
       ├── Deployments and Services
       ├── Liveness and Readiness Probes
       ├── Horizontal Pod Autoscaler
       └── Self-Healing and Recovery

       Monitoring
       ├── Prometheus
       └── Grafana

       Load Testing
       └── k6
```

## Features

- **Microservices architecture:** Separate gateway, user and order services built with Python and Flask.
- **Containerisation:** Docker images package each service and its dependencies.
- **Kubernetes deployment:** Deployments and Services manage application workloads and internal communication.
- **Self-healing:** Kubernetes replaces deleted Pods to maintain the configured number of replicas.
- **Health monitoring:** Liveness probes detect containers that need restarting, while readiness probes determine whether Pods are ready to receive traffic.
- **Horizontal Pod Autoscaling:** The gateway scales between 1 and 4 replicas based on CPU utilisation, targeting 50% of requested CPU.
- **Load testing:** k6 generates concurrent requests to evaluate application behaviour under load.
- **Observability:** Prometheus collects Kubernetes metrics, and Grafana presents CPU usage, CPU utilisation, replica counts and Pod counts.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python and Flask | Microservices and REST APIs |
| Docker | Containerisation |
| Kubernetes | Workload management and self-healing |
| Minikube | Local Kubernetes cluster |
| kubectl | Kubernetes management |
| Helm | Monitoring stack installation |
| Prometheus | Metrics collection |
| Grafana | Monitoring dashboards |
| k6 | HTTP load testing |
| Bash | Chaos experiment scripting |

## Project Structure

```text
self-healing-microservices/
├── services/
│   ├── gateway/
│   ├── user-service/
│   └── order-service/
├── k8s/
│   ├── gateway.yaml
│   ├── user-service.yaml
│   ├── order-service.yaml
│   └── k6-loadtest.yaml
├── chaos/
│   └── chaos.sh
├── monitoring/
│   └── grafana-dashboard.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Prerequisites

- Docker Desktop with WSL2 integration
- Ubuntu on WSL2
- kubectl
- Minikube
- Helm
- Git

The application and monitoring stack require sufficient CPU, memory and disk space.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/self-healing-microservices.git
cd self-healing-microservices
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Start Minikube

Ensure Docker Desktop is running, then execute:

```bash
minikube start
minikube status
kubectl get nodes
```

The node should report `Ready` before deploying the application.

### 3. Build the application images

Build each service image:

```bash
docker build -t gateway:v2 services/gateway
docker build -t user-service:v2 services/user-service
docker build -t order-service:v2 services/order-service
```

Load the images into Minikube:

```bash
minikube image load gateway:v2
minikube image load user-service:v2
minikube image load order-service:v2
```

Ensure that the image tags in the Kubernetes manifests match the tags built above. The manifests use `imagePullPolicy: Never` for locally loaded images.

### 4. Deploy the services

```bash
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/order-service.yaml
kubectl apply -f k8s/gateway.yaml
```

Verify the deployment:

```bash
kubectl get deployments
kubectl get services
kubectl get pods
```

Wait until the application Pods are ready.

### 5. Enable CPU-based autoscaling

Enable the Metrics Server addon:

```bash
minikube addons enable metrics-server
```

Create the gateway Horizontal Pod Autoscaler:

```bash
kubectl autoscale deployment gateway \
  --cpu=50% \
  --min=1 \
  --max=4
```

Inspect scaling status:

```bash
kubectl get hpa
kubectl top pods
```

The HPA adjusts the replica count according to CPU utilisation and the configured scaling limits.

### 6. Install Prometheus and Grafana

Add the Prometheus community chart repository:

```bash
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts

helm repo update
```

Install the monitoring stack:

```bash
helm install monitoring \
  prometheus-community/kube-prometheus-stack
```

Check monitoring Pods:

```bash
kubectl get pods
```

Wait for the Prometheus, Grafana and related monitoring components to become ready.

### 7. Access Grafana

Forward the Grafana service to localhost:

```bash
kubectl port-forward svc/monitoring-grafana 3000:80
```

Open http://localhost:3000.

Retrieve the initial admin password:

```bash
kubectl get secret monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d
echo
```

The default username is `admin`.

Import `monitoring/grafana-dashboard.json` if restoring the exported dashboard, and ensure the Prometheus data source is configured.

## Load Testing

The project includes a k6 test manifest at `k8s/k6-loadtest.yaml`. The current test is configured for 50 virtual users over 60 seconds and sends requests to the gateway's `/summary` endpoint.

Run the test:

```bash
kubectl apply -f k8s/k6-loadtest.yaml
kubectl logs -f k6
```

If a previous k6 Pod already exists, inspect its status and remove a completed Pod before rerunning the test.

Observe autoscaling in another terminal:

```bash
kubectl get hpa -w
```

Observe gateway Pod changes:

```bash
kubectl get pods -l app=gateway -w
```

## Observed Load-Test Results

During a successful 50-virtual-user test, the following results were recorded:

| Metric | Observed result |
|---|---:|
| Virtual users | 50 |
| Test duration | 60 seconds |
| HTTP requests | 8,475 |
| Approximate throughput | 140.27 requests/second |
| Failed checks | 0% |
| Average HTTP duration | 153.78 ms |
| Median HTTP duration | 94.07 ms |
| 90th percentile HTTP duration | 384.36 ms |
| 95th percentile HTTP duration | 434 ms |
| Maximum HTTP duration | 1.87 seconds |

These are results from a particular local test run, not a guarantee of production capacity. Results depend on hardware, cluster configuration and workload.

## Self-Healing Experiment

Kubernetes Deployments maintain the desired number of Pod replicas.

List gateway Pods:

```bash
kubectl get pods -l app=gateway
```

Delete a gateway Pod using its actual name:

```bash
kubectl delete pod <gateway-pod-name>
```

Watch the replacement:

```bash
kubectl get pods -l app=gateway -w
```

Kubernetes should create a replacement Pod to maintain the Deployment's desired replica count. Readiness probes help ensure that traffic is sent only to ready Pods.

The repository also contains `chaos/chaos.sh`, a Bash script for repeatedly deleting service Pods. Use it only in the development cluster, after checking its target labels and behaviour.

## Grafana Dashboard

The exported dashboard is stored at `monitoring/grafana-dashboard.json`.

The dashboard includes panels for:

- Gateway CPU usage
- Gateway replica count
- Gateway Pod count
- Gateway CPU utilisation relative to CPU requests
- Gateway container restarts

The dashboard helps visualise CPU spikes and autoscaling behaviour during load testing. Pod replacement and container restart counts are different events, so Pod recovery should also be verified using Kubernetes Pod status and events.

## Useful Troubleshooting Commands

```bash
# List all Pods
kubectl get pods -A

# Inspect a Pod
kubectl describe pod <pod-name>

# View application logs
kubectl logs <pod-name>

# Inspect deployment status
kubectl get deployments

# Inspect autoscaling
kubectl get hpa

# Inspect resource usage
kubectl top pods

# Inspect Kubernetes events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Current Scope and Future Improvements

This project establishes the baseline for a more comprehensive resilience-testing platform.

Potential improvements include:

- A web interface for configuring and starting load tests.
- Controlled chaos experiments launched through a backend API.
- Application-level Prometheus metrics for request rate, latency and HTTP errors.
- Experiment history and recovery-time measurements.
- Persistent service data and database integration.
- Retry policies, timeouts, circuit breakers and graceful degradation.
- Automated recovery verification and richer dashboards.
- Public deployment with a reproducible demonstration environment.

These are future enhancements and are not claimed as completed features of the current baseline.

## Learning Outcomes

This project provided hands-on experience with containerisation, Kubernetes deployments, health probes, self-healing behaviour, horizontal autoscaling, resource monitoring, load testing and infrastructure observability.

It also demonstrates how to investigate scaling behaviour and validate recovery through controlled experiments.

## Author

**YOUR NAME**

GitHub: [YOUR-GITHUB-PROFILE](https://github.com/YOUR-USERNAME)

---

*Built as a hands-on project to explore resilient microservices and Kubernetes operations.*
