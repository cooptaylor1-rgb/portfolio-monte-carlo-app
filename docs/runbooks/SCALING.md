# Scaling Guide

## Scaling Overview

This guide covers horizontal and vertical scaling strategies for the Portfolio Monte Carlo application.

---

## Current Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────┐
│  Load Balancer  │
└──────┬──────────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌─▼───┐ ┌─▼───┐ ┌─▼───┐
│App 1│ │App 2│ │App 3│ │App N│  ← Stateless application instances
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───┬───┴───────┴───┬───┘
       │               │
   ┌───▼────┐     ┌───▼────┐
   │ Redis  │     │   DB   │         ← Shared services
   │ Cache  │     │  Pool  │
   └────────┘     └────────┘
```

---

## Vertical Scaling

### Docker Compose (Single Server)

**Increase Resources:**

```yaml
# docker-compose.yml
services:
  app:
    mem_limit: 4g          # Up from 2g
    mem_reservation: 2g    # Up from 1g
    cpus: 2                # Up from 1
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

**Apply changes:**
```bash
docker-compose down
docker-compose up -d
```

**Monitor impact:**
```bash
docker stats portfolio-app
```

### Kubernetes

**Increase Pod Resources:**

```yaml
# k8s/deployment.yaml
spec:
  containers:
  - name: portfolio-app
    resources:
      requests:
        memory: "2Gi"     # Up from 1Gi
        cpu: "1000m"      # Up from 500m
      limits:
        memory: "4Gi"     # Up from 2Gi
        cpu: "2000m"      # Up from 1000m
```

**Apply:**
```bash
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/portfolio-app
```

### AWS ECS

**Update Task Definition:**

```json
{
  "containerDefinitions": [{
    "memory": 4096,      // Up from 2048
    "cpu": 2048          // Up from 1024
  }]
}
```

**Apply:**
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs update-service --cluster portfolio-cluster --service portfolio-app --task-definition portfolio-app:NEW_VERSION
```

---

## Horizontal Scaling

### Docker Compose with Nginx

**1. Update docker-compose.yml:**

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

  app:
    image: portfolio-app:latest
    deploy:
      replicas: 3        # Run 3 instances
    environment:
      - ENV=production
    depends_on:
      - db
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  db:
    image: postgres:15-alpine
    # ... existing config

volumes:
  redis_data:
```

**2. Create nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        least_conn;
        server app:8501;
    }

    server {
        listen 80;
        
        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

**3. Deploy:**
```bash
docker-compose up -d --scale app=3
```

### Kubernetes Horizontal Pod Autoscaler (HPA)

**1. Create HPA:**

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: portfolio-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: portfolio-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
```

**2. Apply:**
```bash
kubectl apply -f k8s/hpa.yaml
```

**3. Monitor:**
```bash
kubectl get hpa portfolio-app-hpa --watch
```

### AWS ECS Auto Scaling

**1. Create Scaling Policy:**

```bash
# Target tracking - CPU
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/portfolio-cluster/portfolio-app \
    --min-capacity 2 \
    --max-capacity 10

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/portfolio-cluster/portfolio-app \
    --policy-name cpu-target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
      },
      "ScaleOutCooldown": 60,
      "ScaleInCooldown": 300
    }'
```

**2. Monitor:**
```bash
aws application-autoscaling describe-scaling-activities \
    --service-namespace ecs \
    --resource-id service/portfolio-cluster/portfolio-app
```

---

## Database Scaling

### Connection Pooling

**Update config.py:**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class Config:
    # ... existing config
    
    @property
    def database_engine(self):
        return create_engine(
            self.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,          # Base connections
            max_overflow=20,       # Additional connections
            pool_timeout=30,       # Wait time for connection
            pool_recycle=3600,     # Recycle connections after 1 hour
            pool_pre_ping=True     # Test connections before use
        )
```

### Read Replicas

**1. Setup read replica (AWS RDS example):**
```bash
aws rds create-db-instance-read-replica \
    --db-instance-identifier portfolio-db-replica-1 \
    --source-db-instance-identifier portfolio-db \
    --publicly-accessible
```

**2. Update application config:**

```python
class Config:
    DATABASE_WRITE_URL = os.getenv('DATABASE_URL')
    DATABASE_READ_URL = os.getenv('DATABASE_READ_URL', DATABASE_WRITE_URL)
    
    def get_db_connection(self, read_only=False):
        url = self.DATABASE_READ_URL if read_only else self.DATABASE_WRITE_URL
        return create_engine(url)
```

**3. Use in application:**

```python
# For writes
with config.get_db_connection(read_only=False).connect() as conn:
    conn.execute("INSERT INTO audit_logs ...")

# For reads
with config.get_db_connection(read_only=True).connect() as conn:
    results = conn.execute("SELECT * FROM audit_logs ...")
```

### Database Partitioning

**Partition by date:**

```sql
-- Create partitioned table
CREATE TABLE audit_logs (
    id SERIAL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50),
    data JSONB
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE audit_logs_2025_12 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Create index on each partition
CREATE INDEX ON audit_logs_2025_12 (timestamp);
CREATE INDEX ON audit_logs_2026_01 (timestamp);
```

---

## Cache Scaling

### Redis Cluster

**docker-compose.yml:**

```yaml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_master_data:/data

  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master

  redis-replica-2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master

  redis-sentinel-1:
    image: redis:7-alpine
    command: >
      redis-sentinel /etc/redis/sentinel.conf
      --sentinel monitor mymaster redis-master 6379 2
      --sentinel down-after-milliseconds mymaster 5000
      --sentinel failover-timeout mymaster 10000
    depends_on:
      - redis-master

volumes:
  redis_master_data:
```

### Multi-Level Caching

**Implement L1 (local) + L2 (Redis) cache:**

```python
# enhanced_cache.py
import redis
from functools import wraps
from performance_optimizer import cache_manager as l1_cache

# L2 Redis cache
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

def multi_level_cache(ttl=3600):
    """Two-level caching: L1 (memory) + L2 (Redis)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try L1 cache (fastest)
            result = l1_cache.get(cache_key)
            if result is not None:
                return result
            
            # Try L2 cache (Redis)
            result = redis_client.get(cache_key)
            if result is not None:
                # Populate L1 cache
                l1_cache.set(cache_key, result)
                return result
            
            # Compute and cache in both levels
            result = func(*args, **kwargs)
            l1_cache.set(cache_key, result)
            redis_client.setex(cache_key, ttl, result)
            
            return result
        return wrapper
    return decorator
```

---

## Load Testing

### Using Locust

**1. Create locustfile.py:**

```python
from locust import HttpUser, task, between
import random

class PortfolioUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def run_simulation(self):
        """Simulate running Monte Carlo"""
        self.client.get("/")
        
        # Typical simulation parameters
        data = {
            "starting_portfolio": random.randint(500000, 2000000),
            "monthly_spending": random.randint(3000, 8000),
            "n_scenarios": random.choice([100, 500, 1000]),
            "years": random.choice([20, 30, 40])
        }
        
        with self.client.post(
            "/run_simulation",
            json=data,
            catch_response=True,
            name="/run_simulation"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check"""
        self.client.get("/health")
    
    @task(1)
    def view_results(self):
        """View results"""
        self.client.get("/results")
```

**2. Run load test:**

```bash
# Install locust
pip install locust

# Run test - 100 users, spawn 10 per second
locust -f locustfile.py --host=http://localhost:8501 --users 100 --spawn-rate 10

# Headless mode with duration
locust -f locustfile.py --host=http://localhost:8501 --users 100 --spawn-rate 10 --run-time 5m --headless
```

**3. Monitor results:**
- Open http://localhost:8089
- Watch requests/sec, response times, error rates
- Identify performance bottlenecks

### Stress Testing

```bash
# Simple stress test with Apache Bench
ab -n 1000 -c 10 http://localhost:8501/health

# With wrk
wrk -t4 -c100 -d30s http://localhost:8501/

# With hey
hey -n 1000 -c 50 -m GET http://localhost:8501/health
```

---

## Capacity Planning

### Calculate Required Resources

**1. Baseline Metrics:**

```python
# Measure resource usage per request
import psutil
import time

def measure_request():
    process = psutil.Process()
    
    # Before
    cpu_before = process.cpu_percent()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    start_time = time.time()
    
    # Execute simulation
    run_monte_carlo(inputs)
    
    # After
    duration = time.time() - start_time
    cpu_after = process.cpu_percent()
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    
    return {
        'duration_sec': duration,
        'cpu_usage': cpu_after - cpu_before,
        'memory_mb': mem_after - mem_before
    }
```

**2. Capacity Formula:**

```
Requests per Second (RPS) = (Number of Instances × CPU Cores × CPU Efficiency) / Avg Request Duration

Example:
- 3 instances
- 2 CPU cores each
- 80% efficiency
- 0.2 seconds per request

RPS = (3 × 2 × 0.8) / 0.2 = 24 requests/second
```

**3. Plan for Growth:**

| Users | Concurrent Requests | Required Instances | Total Capacity |
|-------|--------------------|--------------------|----------------|
| 100   | 10                 | 2                  | 24 RPS         |
| 500   | 50                 | 5                  | 60 RPS         |
| 1,000 | 100                | 10                 | 120 RPS        |
| 5,000 | 500                | 50                 | 600 RPS        |

---

## Monitoring Scaling

### Key Metrics to Watch

**1. Application Metrics:**
```bash
# Request rate
docker logs portfolio-app | grep "correlation_id" | wc -l

# Response time (p95)
docker logs portfolio-app | grep "duration_ms" | awk '{print $NF}' | sort -n | awk '{arr[NR]=$1} END {print arr[int(NR*0.95)]}'

# Error rate
docker logs portfolio-app | grep -c "ERROR"
```

**2. Resource Metrics:**
```bash
# CPU usage
docker stats --no-stream portfolio-app | awk '{print $3}'

# Memory usage
docker stats --no-stream portfolio-app | awk '{print $7}'

# Disk I/O
iostat -x 1 5
```

**3. Database Metrics:**
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Slow queries
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Cache hit ratio
SELECT 
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;
```

### Alerting Thresholds

```yaml
alerts:
  - name: High CPU Usage
    condition: cpu_usage > 80%
    duration: 5m
    action: scale_up
  
  - name: High Memory Usage
    condition: memory_usage > 85%
    duration: 5m
    action: scale_up
  
  - name: High Request Latency
    condition: p95_latency > 2s
    duration: 2m
    action: investigate
  
  - name: High Error Rate
    condition: error_rate > 5%
    duration: 1m
    action: alert_oncall
  
  - name: Low CPU Usage
    condition: cpu_usage < 20%
    duration: 30m
    action: scale_down
```

---

## Cost Optimization

### Right-Sizing

**1. Analyze usage patterns:**
```bash
# Get 7-day average CPU usage
docker stats portfolio-app --no-stream | awk '{print $3}' | sed 's/%//' | awk '{sum+=$1; count+=1} END {print sum/count}'
```

**2. Adjust resources:**
- If avg CPU < 30%: Consider smaller instances
- If avg CPU > 70%: Consider larger instances or more replicas

### Spot/Preemptible Instances

**AWS ECS with Spot:**
```json
{
  "capacityProviders": ["FARGATE", "FARGATE_SPOT"],
  "defaultCapacityProviderStrategy": [
    {
      "capacityProvider": "FARGATE_SPOT",
      "weight": 4,
      "base": 2
    },
    {
      "capacityProvider": "FARGATE",
      "weight": 1
    }
  ]
}
```

**GKE with Preemptible Nodes:**
```bash
gcloud container node-pools create preemptible-pool \
    --cluster=portfolio-cluster \
    --preemptible \
    --num-nodes=3 \
    --machine-type=n1-standard-2
```

---

## Scaling Checklist

Before scaling:
- [ ] Establish baseline metrics
- [ ] Identify bottlenecks
- [ ] Set up monitoring
- [ ] Configure health checks
- [ ] Test load balancing
- [ ] Implement connection pooling
- [ ] Configure autoscaling
- [ ] Set resource limits
- [ ] Enable logging
- [ ] Create runbooks

During scaling:
- [ ] Monitor key metrics
- [ ] Watch error rates
- [ ] Check response times
- [ ] Verify cache hit rates
- [ ] Monitor database connections
- [ ] Check memory usage
- [ ] Verify load distribution

After scaling:
- [ ] Validate performance improvement
- [ ] Review costs
- [ ] Update capacity plan
- [ ] Document changes
- [ ] Update alerts
- [ ] Conduct load test

---

## Additional Resources

- [Incident Response Runbook](INCIDENT_RESPONSE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Performance Optimization Guide](../PERFORMANCE_OPTIMIZATION_GUIDE.md)
