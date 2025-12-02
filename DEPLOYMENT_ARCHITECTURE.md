# Deployment Architecture

## 🏗️ Production Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer / CDN                       │
│                    (CloudFlare / AWS ALB / etc.)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster / ECS                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Streamlit Application                    │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Frontend (Streamlit UI)                            │  │  │
│  │  │  - Health checks: /health, /ready                   │  │  │
│  │  │  - Metrics: /metrics (Prometheus)                   │  │  │
│  │  │  - Port: 8501                                       │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Backend Services                                   │  │  │
│  │  │  - Monte Carlo Engine (vectorized)                  │  │  │
│  │  │  - AI Analysis Engine                               │  │  │
│  │  │  - PDF Generation                                   │  │  │
│  │  │  - Cache Manager (500MB TTL)                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Replicas: 3-10 (auto-scaling based on CPU/Memory)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
    ┌───────────────────────┐  ┌─────────────────────┐
    │   Redis (Cache)       │  │   PostgreSQL        │
    │   - Shared cache      │  │   - Audit logs      │
    │   - Session store     │  │   - User data       │
    │   - Rate limiting     │  │   - Simulations     │
    └───────────────────────┘  └─────────────────────┘
                    │                 │
                    └────────┬────────┘
                             ▼
            ┌─────────────────────────────────┐
            │   Observability Stack           │
            │  - Logs → CloudWatch/DataDog    │
            │  - Metrics → Prometheus         │
            │  - Traces → Jaeger/DataDog      │
            │  - Errors → Sentry              │
            └─────────────────────────────────┘
```

---

## 🐳 Docker Architecture

### Multi-Stage Build Strategy

```dockerfile
# Stage 1: Builder (compile/install dependencies)
FROM python:3.12-slim as builder
# Install build dependencies
# Create optimized wheel packages

# Stage 2: Runtime (minimal, production-ready)
FROM python:3.12-slim
# Copy only runtime dependencies
# Run as non-root user
# Expose only necessary ports
```

### Container Components

1. **Application Container** (`app`)
   - **Base:** `python:3.12-slim` (security-hardened)
   - **User:** `appuser` (UID 1000, non-root)
   - **Ports:** 8501 (Streamlit)
   - **Health Check:** `/health` endpoint
   - **Size:** ~300MB (optimized)

2. **Cache Container** (`redis`) - Optional
   - **Base:** `redis:7-alpine`
   - **Purpose:** Shared cache for multi-instance deployments
   - **Port:** 6379
   - **Persistence:** Volume-backed

3. **Database Container** (`postgres`) - Optional
   - **Base:** `postgres:16-alpine`
   - **Purpose:** Audit logs, user data, simulation history
   - **Port:** 5432
   - **Persistence:** Volume-backed

---

## 🔧 Environment Configuration

### Configuration Layers

```
Environment Variables (12-factor app)
          ↓
    .env files (local dev)
          ↓
    Secrets Manager (prod)
          ↓
    Config Class (app)
```

### Configuration by Environment

| Config | Dev | Staging | Production |
|--------|-----|---------|------------|
| **DEBUG** | True | False | False |
| **LOG_LEVEL** | DEBUG | INFO | WARNING |
| **CACHE_TTL** | 600s | 1800s | 3600s |
| **MAX_SCENARIOS** | 1000 | 5000 | 10000 |
| **RATE_LIMIT** | None | 100/min | 60/min |
| **REPLICAS** | 1 | 2 | 3-10 |
| **DB_POOL_SIZE** | 5 | 10 | 20 |
| **REDIS_ENABLED** | False | True | True |

### Secret Management

**Development:**
- `.env` files (gitignored)
- Local environment variables

**Production:**
- AWS Secrets Manager / Azure Key Vault / GCP Secret Manager
- Kubernetes Secrets
- Environment variables injected at runtime

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows

```
┌─────────────────────────────────────────────────────────────┐
│                         PR Opened                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  1. Code Quality Checks     │
        │     - Lint (flake8/black)   │
        │     - Type check (mypy)     │
        │     - Security scan (bandit)│
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  2. Unit Tests              │
        │     - pytest                │
        │     - Coverage > 80%        │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  3. Integration Tests       │
        │     - test_integration.py   │
        │     - test_performance.py   │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  4. Docker Build Test       │
        │     - Build image           │
        │     - Run smoke tests       │
        └─────────────────────────────┘
                      │
                      ▼ PR Approved & Merged
┌─────────────────────────────────────────────────────────────┐
│                      Push to Main                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  5. Build & Push Images     │
        │     - Build production img  │
        │     - Tag: latest, SHA      │
        │     - Push to registry      │
        │     - Scan for vulns        │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  6. Deploy to Staging       │
        │     - Auto-deploy           │
        │     - Smoke tests           │
        │     - Integration tests     │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  7. Manual Approval Gate    │
        │     - Review staging        │
        │     - Approve for prod      │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  8. Deploy to Production    │
        │     - Blue/green deploy     │
        │     - Health checks         │
        │     - Rollback on failure   │
        └─────────────────────────────┘
```

### Deployment Strategies

1. **Rolling Update** (default)
   - Deploy new pods one at a time
   - Health check each pod before proceeding
   - Automatic rollback on failure

2. **Blue/Green** (production)
   - Deploy to new environment (green)
   - Switch traffic when healthy
   - Keep old environment (blue) for quick rollback

3. **Canary** (high-traffic scenarios)
   - Deploy to 10% of pods first
   - Monitor metrics for 15 minutes
   - Gradually increase to 100%

---

## 📊 Observability

### 1. Structured Logging

```python
{
  "timestamp": "2025-12-02T10:15:30.123Z",
  "level": "INFO",
  "correlation_id": "req-abc123",
  "user_id": "user-456",
  "operation": "monte_carlo_simulation",
  "duration_ms": 51.4,
  "scenarios": 1000,
  "success": true,
  "environment": "production"
}
```

**Log Aggregation:**
- AWS CloudWatch Logs
- DataDog
- ELK Stack (Elasticsearch, Logstash, Kibana)

### 2. Metrics

**Application Metrics:**
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate (errors/sec)
- Monte Carlo simulations (scenarios/sec)
- Cache hit rate (%)

**Infrastructure Metrics:**
- CPU usage (%)
- Memory usage (MB)
- Disk I/O (IOPS)
- Network traffic (MB/s)

**Business Metrics:**
- Active users
- Simulations per user
- PDF downloads
- AI analysis requests

### 3. Health Checks

**Liveness Probe** (`/health`)
- Simple check: Is app running?
- Responds in <100ms
- Returns 200 if alive

**Readiness Probe** (`/ready`)
- Deep check: Is app ready for traffic?
- Checks:
  - Cache available
  - DB connected (if applicable)
  - Dependencies loaded
- Returns 200 if ready

**Startup Probe** (`/startup`)
- Initial check: Has app finished starting?
- Allows longer startup time
- Prevents premature traffic

### 4. Distributed Tracing

**Trace Context:**
- Request ID: Unique per request
- Span ID: Unique per operation
- Parent Span: For nested operations

**Trace Example:**
```
Request: Calculate Monte Carlo
├─ Span: validate_inputs (2ms)
├─ Span: run_monte_carlo_vectorized (51ms)
│  ├─ Span: generate_random_returns (10ms)
│  └─ Span: calculate_statistics (5ms)
├─ Span: render_charts (30ms)
└─ Span: cache_results (1ms)
Total: 84ms
```

### 5. Error Tracking

**Sentry Integration:**
- Automatic error capture
- Stack traces
- Environment context
- User context
- Breadcrumbs (events leading to error)

**Alerting:**
- Error rate > 1%
- Response time p95 > 2000ms
- Memory usage > 80%
- Failed health checks

---

## 🔒 Security & Hardening

### 1. Container Security

**Image Hardening:**
```dockerfile
# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Minimal base image
FROM python:3.12-slim  # Not python:3.12 (full)

# No unnecessary packages
RUN apt-get remove --purge -y build-essential

# Read-only filesystem
docker run --read-only ...

# Drop capabilities
docker run --cap-drop ALL ...
```

### 2. Input Validation

**Validation Rules:**
- Portfolio value: $1,000 - $100,000,000
- Spending: $0 - $1,000,000/year
- Scenarios: 10 - 10,000
- Years: 1 - 100
- Equity allocation: 0% - 100%

**Sanitization:**
- Strip HTML/JavaScript from text inputs
- Validate file uploads (PDF size < 10MB)
- Rate limit API calls

### 3. Rate Limiting

**Limits by Environment:**
- **Development:** No limit
- **Staging:** 100 requests/minute per IP
- **Production:** 60 requests/minute per IP

**Patterns:**
- Token bucket algorithm
- Redis-backed (distributed)
- Per-user limits (authenticated)
- Per-IP limits (unauthenticated)

### 4. Secrets Management

**Never in Code:**
❌ `API_KEY = "abc123"`

**Environment Variables:**
✅ `API_KEY = os.getenv("API_KEY")`

**Secrets Manager:**
✅ AWS Secrets Manager / Azure Key Vault

**Rotation:**
- Auto-rotate secrets every 90 days
- Alert on failed rotation

### 5. Network Security

**Firewall Rules:**
- Allow: Port 8501 (Streamlit) from load balancer
- Allow: Port 6379 (Redis) from app only
- Allow: Port 5432 (PostgreSQL) from app only
- Deny: All other traffic

**TLS/SSL:**
- TLS 1.3 only
- Strong cipher suites
- HSTS headers
- Certificate auto-renewal (Let's Encrypt)

---

## 🚨 Reliability & Resilience

### 1. Graceful Shutdown

**Shutdown Sequence:**
```python
1. Receive SIGTERM signal
2. Stop accepting new requests
3. Complete in-flight Monte Carlo simulations (timeout: 30s)
4. Flush logs and metrics
5. Close DB/cache connections
6. Exit with code 0
```

### 2. Circuit Breaker

**Pattern:**
```
[CLOSED] → Normal operation
    ↓ (5 failures)
[OPEN] → Reject requests immediately
    ↓ (30s timeout)
[HALF-OPEN] → Try 1 request
    ↓ (success)
[CLOSED] → Resume normal
```

### 3. Retry Logic

**Exponential Backoff:**
```
Attempt 1: 0s wait
Attempt 2: 1s wait
Attempt 3: 2s wait
Attempt 4: 4s wait
Attempt 5: 8s wait (max 3 retries)
```

### 4. Timeout Configuration

| Operation | Timeout |
|-----------|---------|
| Health check | 1s |
| Cache lookup | 100ms |
| DB query | 5s |
| Monte Carlo (1000) | 5s |
| PDF generation | 30s |
| Full request | 60s |

### 5. Auto-Scaling

**Horizontal Pod Autoscaler (HPA):**
```yaml
minReplicas: 3
maxReplicas: 10
targetCPUUtilization: 70%
targetMemoryUtilization: 80%
```

**Scale-up Triggers:**
- CPU > 70% for 1 minute
- Memory > 80% for 1 minute
- Request queue > 100

**Scale-down Triggers:**
- CPU < 30% for 5 minutes
- Memory < 40% for 5 minutes

---

## 📦 Deployment Targets

### Option 1: AWS (ECS Fargate)

**Pros:**
- Serverless (no EC2 management)
- Auto-scaling built-in
- Integrates with AWS services

**Components:**
- ECS Cluster + Fargate
- Application Load Balancer
- ElastiCache (Redis)
- RDS PostgreSQL
- CloudWatch Logs
- Secrets Manager

**Cost:** ~$200-500/month (3 tasks)

### Option 2: Kubernetes (EKS/GKE/AKS)

**Pros:**
- Portable across clouds
- Rich ecosystem
- Advanced features (service mesh, etc.)

**Components:**
- Kubernetes cluster (3 nodes)
- Ingress controller (Nginx)
- Redis Operator
- PostgreSQL Operator
- Prometheus + Grafana
- Cert-Manager (SSL)

**Cost:** ~$300-700/month

### Option 3: Azure App Service

**Pros:**
- Simplest deployment
- Integrated monitoring
- Auto-scaling

**Components:**
- App Service (P1v2 tier)
- Azure Cache for Redis
- Azure Database for PostgreSQL
- Application Insights
- Key Vault

**Cost:** ~$150-400/month

### Option 4: Google Cloud Run

**Pros:**
- Fully managed
- Pay-per-request
- Fast scaling

**Components:**
- Cloud Run service
- Cloud Memorystore (Redis)
- Cloud SQL (PostgreSQL)
- Cloud Logging
- Secret Manager

**Cost:** ~$100-300/month (varies with traffic)

---

## 🎯 Recommended Architecture

### For Production Launch: **AWS ECS Fargate**

**Why:**
1. ✅ No infrastructure management (serverless)
2. ✅ Simple deployment model
3. ✅ Cost-effective for moderate traffic
4. ✅ Easy integration with AWS services
5. ✅ Quick to set up (<1 day)

**Components:**
```
Application:
- ECS Fargate tasks (3 replicas)
- Application Load Balancer
- Auto Scaling (3-10 tasks)

Data:
- ElastiCache Redis (cache.t3.micro)
- RDS PostgreSQL (db.t3.micro) - optional

Observability:
- CloudWatch Logs (structured)
- CloudWatch Metrics
- X-Ray (distributed tracing)
- Sentry (error tracking)

Security:
- Secrets Manager
- VPC with private subnets
- Security groups (least privilege)
- IAM roles (task execution)
```

**Estimated Cost Breakdown:**
- ECS Fargate (3 tasks): $120/month
- ALB: $25/month
- ElastiCache: $15/month
- RDS (optional): $20/month
- CloudWatch: $10/month
- Data transfer: $10/month
- **Total: ~$200/month**

---

## 📈 Scaling Strategy

### Phase 1: Launch (0-100 users)
- 3 ECS tasks
- Basic monitoring
- Manual deployments with approval

### Phase 2: Growth (100-1,000 users)
- Auto-scaling (3-10 tasks)
- Advanced monitoring (APM)
- Automated deployments
- Add Redis cache

### Phase 3: Scale (1,000-10,000 users)
- Kubernetes migration (more control)
- Multi-region deployment
- CDN for static assets
- Database read replicas

### Phase 4: Enterprise (10,000+ users)
- Service mesh (Istio)
- Advanced caching (multi-tier)
- GPU acceleration for simulations
- Dedicated infrastructure

---

## 🔄 Disaster Recovery

### Backup Strategy

**Application:**
- Docker images: Stored in registry (immutable)
- Config: Version controlled (Git)

**Data:**
- PostgreSQL: Daily backups (7-day retention)
- Redis: Snapshotting (optional)
- Audit logs: S3 archival (1-year retention)

**Recovery Time Objectives:**
- RTO (Recovery Time Objective): 15 minutes
- RPO (Recovery Point Objective): 1 hour

### Runbooks

1. **Application Crash**
   - Check logs in CloudWatch
   - Review error tracking (Sentry)
   - Restart tasks (auto-healing)

2. **Performance Degradation**
   - Check CPU/memory metrics
   - Review slow query logs
   - Scale up tasks temporarily

3. **Data Loss**
   - Restore from latest backup
   - Replay audit logs
   - Verify data integrity

4. **Security Breach**
   - Rotate all secrets immediately
   - Review access logs
   - Patch vulnerabilities
   - Incident report

---

## 📝 Next Steps

1. ✅ Implement Docker containerization
2. ✅ Add health/readiness endpoints
3. ✅ Implement structured logging
4. ✅ Add environment configuration
5. ✅ Create CI/CD pipelines
6. ✅ Security hardening
7. ✅ Documentation
8. 🚀 Deploy to staging
9. 🚀 Production launch

---

*This architecture provides a solid foundation for scaling from 0 to 10,000+ users while maintaining reliability, security, and observability.*
