# 🚀 Deployment Guide

## Portfolio Monte Carlo Analysis Platform - Production Deployment

This guide covers deploying the Portfolio Analysis Platform to production using Docker, Kubernetes, or cloud services (AWS ECS, Azure App Service, Google Cloud Run).

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
   - [AWS ECS/Fargate](#aws-ecsfargate)
   - [Kubernetes](#kubernetes)
   - [Azure App Service](#azure-app-service)
   - [Google Cloud Run](#google-cloud-run)
5. [Configuration](#configuration)
6. [CI/CD](#cicd)
7. [Monitoring & Operations](#monitoring--operations)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** 2.30+
- **Python** 3.12+ (for local development)

### Optional (for cloud deployment)
- **AWS CLI** 2.0+ (for AWS ECS)
- **kubectl** 1.28+ (for Kubernetes)
- **Azure CLI** 2.50+ (for Azure)
- **gcloud CLI** 440.0+ (for Google Cloud)

### Cloud Accounts
- AWS Account (for ECS deployment)
- Azure Account (for App Service)
- Google Cloud Account (for Cloud Run)
- Docker Hub or GitHub Container Registry account

---

## Local Development

### 1. Clone Repository
```bash
git clone https://github.com/cooptaylor1-rgb/portfolio-monte-carlo-app.git
cd portfolio-monte-carlo-app
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_TTL=600
MAX_SCENARIOS=10000
```

### 3. Run with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 4. Access Application
- **Application:** http://localhost:8501
- **Health Check:** http://localhost:8501/health
- **Metrics:** http://localhost:8501/metrics

### 5. Run Without Docker (Python)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

---

## Docker Deployment

### Build Docker Image
```bash
# Development build
docker build -t portfolio-analyzer:dev .

# Production build with version tag
docker build -t portfolio-analyzer:1.0.0 \
             -t portfolio-analyzer:latest .

# Multi-platform build (ARM + x86)
docker buildx build --platform linux/amd64,linux/arm64 \
                    -t portfolio-analyzer:latest .
```

### Run Docker Container
```bash
# Basic run
docker run -p 8501:8501 portfolio-analyzer:latest

# With environment variables
docker run -p 8501:8501 \
           -e APP_ENV=production \
           -e LOG_LEVEL=INFO \
           -e CACHE_TTL=3600 \
           portfolio-analyzer:latest

# With volume mounts (for logs)
docker run -p 8501:8501 \
           -v $(pwd)/audit_logs:/app/audit_logs \
           portfolio-analyzer:latest

# Run in background (detached)
docker run -d --name portfolio-app \
           -p 8501:8501 \
           --restart unless-stopped \
           portfolio-analyzer:latest
```

### Docker Compose (Production)
```bash
# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable Redis cache
# Uncomment redis service in docker-compose.yml
docker-compose up -d redis app

# Enable PostgreSQL
# Uncomment postgres service in docker-compose.yml
docker-compose up -d postgres app

# View resource usage
docker-compose stats

# Scale application (multiple instances)
docker-compose up -d --scale app=3
```

---

## Cloud Deployment

### AWS ECS/Fargate

#### Prerequisites
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

#### 1. Push Image to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name portfolio-analyzer --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag portfolio-analyzer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-analyzer:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-analyzer:latest
```

#### 2. Create ECS Cluster
```bash
# Create cluster
aws ecs create-cluster --cluster-name portfolio-analyzer-prod --region us-east-1

# Create task definition
cat > task-definition.json <<EOF
{
  "family": "portfolio-analyzer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-analyzer:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "APP_ENV", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "python /app/healthcheck.py || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/portfolio-analyzer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 3. Create Service with Load Balancer
```bash
# Create Application Load Balancer (ALB)
aws elbv2 create-load-balancer \
  --name portfolio-analyzer-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing \
  --type application

# Create target group
aws elbv2 create-target-group \
  --name portfolio-analyzer-tg \
  --protocol HTTP \
  --port 8501 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30

# Create ECS service
aws ecs create-service \
  --cluster portfolio-analyzer-prod \
  --service-name portfolio-analyzer \
  --task-definition portfolio-analyzer:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=app,containerPort=8501"
```

#### 4. Configure Auto Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/portfolio-analyzer-prod/portfolio-analyzer \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 3 \
  --max-capacity 10

# Create scaling policy (CPU-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/portfolio-analyzer-prod/portfolio-analyzer \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

**Cost Estimate:** $200-500/month (3-10 tasks)

---

### Kubernetes

#### 1. Create Kubernetes Manifests

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portfolio-analyzer
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: portfolio-analyzer
  template:
    metadata:
      labels:
        app: portfolio-analyzer
    spec:
      containers:
      - name: app
        image: ghcr.io/cooptaylor1-rgb/portfolio-monte-carlo-app:latest
        ports:
        - containerPort: 8501
        env:
        - name: APP_ENV
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 10
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: portfolio-analyzer
  namespace: production
spec:
  selector:
    app: portfolio-analyzer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portfolio-analyzer
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - portfolio-analyzer.example.com
    secretName: portfolio-analyzer-tls
  rules:
  - host: portfolio-analyzer.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: portfolio-analyzer
            port:
              number: 80
```

#### 2. Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace production

# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check deployment
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production

# View logs
kubectl logs -f -l app=portfolio-analyzer -n production

# Scale deployment
kubectl scale deployment portfolio-analyzer --replicas=5 -n production
```

**Cost Estimate:** $300-700/month (depending on cloud provider)

---

### Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name portfolio-analyzer-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name portfolio-analyzer-plan \
  --resource-group portfolio-analyzer-rg \
  --sku P1v2 \
  --is-linux

# Create web app
az webapp create \
  --resource-group portfolio-analyzer-rg \
  --plan portfolio-analyzer-plan \
  --name portfolio-analyzer-app \
  --deployment-container-image-name ghcr.io/cooptaylor1-rgb/portfolio-monte-carlo-app:latest

# Configure app settings
az webapp config appsettings set \
  --resource-group portfolio-analyzer-rg \
  --name portfolio-analyzer-app \
  --settings APP_ENV=production LOG_LEVEL=INFO

# Configure auto-scaling
az monitor autoscale create \
  --resource-group portfolio-analyzer-rg \
  --resource portfolio-analyzer-app \
  --resource-type Microsoft.Web/serverFarms \
  --name autoscale-settings \
  --min-count 3 \
  --max-count 10 \
  --count 3

# View logs
az webapp log tail --name portfolio-analyzer-app --resource-group portfolio-analyzer-rg
```

**Cost Estimate:** $150-400/month

---

### Google Cloud Run

```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project your-project-id

# Build and push image to GCR
gcloud builds submit --tag gcr.io/your-project-id/portfolio-analyzer

# Deploy to Cloud Run
gcloud run deploy portfolio-analyzer \
  --image gcr.io/your-project-id/portfolio-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars APP_ENV=production,LOG_LEVEL=INFO

# View service details
gcloud run services describe portfolio-analyzer --region us-central1

# View logs
gcloud run services logs read portfolio-analyzer --region us-central1
```

**Cost Estimate:** $100-300/month (pay-per-request)

---

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

**Critical Production Settings:**
```bash
# Security
SECRET_KEY=<generate-random-32-char-string>
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Performance
CACHE_TTL=3600
MAX_SCENARIOS=10000

# Observability
SENTRY_DSN=https://xxx@sentry.io/xxx
ENABLE_METRICS=true

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

### Secrets Management

**AWS Secrets Manager:**
```bash
# Store secret
aws secretsmanager create-secret \
  --name portfolio-analyzer/prod/secret-key \
  --secret-string "your-secret-key"

# Retrieve in ECS task definition
{
  "secrets": [
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:portfolio-analyzer/prod/secret-key"
    }
  ]
}
```

**Kubernetes Secrets:**
```bash
# Create secret
kubectl create secret generic app-secrets \
  --from-literal=secret-key=your-secret-key \
  --namespace production

# Use in deployment
env:
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: secret-key
```

---

## CI/CD

### GitHub Actions

The repository includes two workflows:

1. **`.github/workflows/ci.yml`** - Test & Lint (runs on every PR)
2. **`.github/workflows/cd.yml`** - Build & Deploy (runs on push to main)

#### Required Secrets

Configure in GitHub Settings > Secrets and variables > Actions:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID_PROD
AWS_SECRET_ACCESS_KEY_PROD
SLACK_WEBHOOK (optional)
```

#### Manual Deployment

```bash
# Deploy to staging
gh workflow run cd.yml -f environment=staging

# Deploy to production (requires approval)
gh workflow run cd.yml -f environment=production

# Rollback
gh workflow run cd.yml -f environment=production -f action=rollback
```

---

## Monitoring & Operations

### Health Checks

- **Liveness:** `GET /health` - Is app alive?
- **Readiness:** `GET /ready` - Ready for traffic?
- **Startup:** `GET /startup` - Finished starting?

### Metrics

Access metrics at `/metrics` endpoint (Prometheus format):

```
# Request metrics
request_count
request_duration_avg
error_count

# Simulation metrics
simulation_count
simulation_scenarios_total
simulation_duration_avg

# Cache metrics
cache_hits
cache_misses
cache_hit_rate

# System metrics
process_cpu_percent
process_memory_mb
process_threads
```

### Logging

Structured JSON logs:
```json
{
  "timestamp": "2025-12-02T10:15:30.123Z",
  "level": "INFO",
  "correlation_id": "req-abc123",
  "operation": "monte_carlo_simulation",
  "duration_ms": 51.4,
  "scenarios": 1000
}
```

### Error Tracking

Integrate with Sentry:
```bash
export SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker logs portfolio-app

# Check health endpoint
curl http://localhost:8501/health

# Verify environment variables
docker exec portfolio-app env | grep APP_
```

### High Memory Usage

```bash
# Check memory limits
docker stats portfolio-app

# Reduce cache size
export CACHE_MAX_SIZE_MB=250

# Limit scenarios
export MAX_SCENARIOS=5000
```

### Slow Performance

```bash
# Enable Redis caching
export REDIS_ENABLED=true
export REDIS_HOST=redis

# Check metrics
curl http://localhost:8501/metrics

# Review performance tests
python test_performance.py
```

### Database Connection Issues

```bash
# Check PostgreSQL connectivity
docker exec -it portfolio-app psql -h postgres -U portfolio_user -d portfolio_db

# Verify credentials
echo $DB_PASSWORD

# Check network
docker network ls
docker network inspect portfolio-net
```

---

## Support

- **Documentation:** [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md)
- **Performance:** [PERFORMANCE_OPTIMIZATION_GUIDE.md](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- **Issues:** https://github.com/cooptaylor1-rgb/portfolio-monte-carlo-app/issues

---

## License

Copyright © 2025 Salem Investment Counselors. All rights reserved.
