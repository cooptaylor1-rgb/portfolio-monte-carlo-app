# Incident Response Runbook

## Quick Reference

| Severity | Response Time | Escalation |
|----------|--------------|------------|
| P0 (Critical) | 15 minutes | Immediate |
| P1 (High) | 1 hour | If unresolved in 2 hours |
| P2 (Medium) | 4 hours | If unresolved in 8 hours |
| P3 (Low) | 24 hours | As needed |

---

## Common Incidents

### 1. Application Down / Not Responding

**Symptoms:**
- Health check failing
- 502/503 errors
- No response from application

**Immediate Actions:**

```bash
# Check if container is running
docker ps | grep portfolio-app

# Check logs for errors
docker logs portfolio-app --tail=100

# Check resource usage
docker stats portfolio-app

# Check health endpoint
curl http://localhost:8501/health
```

**Resolution Steps:**

1. **Check Container Status:**
   ```bash
   docker ps -a | grep portfolio-app
   ```
   
2. **View Recent Logs:**
   ```bash
   docker logs portfolio-app --tail=500 | grep -i "error\|exception\|fatal"
   ```

3. **Check Resource Constraints:**
   ```bash
   # CPU/Memory usage
   docker stats --no-stream portfolio-app
   
   # Disk space
   df -h
   ```

4. **Restart Container (if needed):**
   ```bash
   docker-compose restart app
   ```

5. **If restart fails, rebuild:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

**Root Cause Analysis:**
- Check application logs for stack traces
- Review recent deployments
- Check for configuration changes
- Review resource metrics before incident

---

### 2. High Latency / Slow Response Times

**Symptoms:**
- Requests taking >5 seconds
- Users reporting slow page loads
- Timeout errors

**Immediate Actions:**

```bash
# Check current performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8501/health

# Monitor real-time performance
watch -n 1 'curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8501/health'
```

**Diagnostic Steps:**

1. **Check Application Metrics:**
   ```bash
   # View performance logs
   docker logs portfolio-app | grep "duration_ms"
   
   # Check for slow operations
   docker logs portfolio-app | grep "WARNING.*took"
   ```

2. **Check Resource Utilization:**
   ```bash
   # CPU and memory
   docker stats portfolio-app
   
   # Check if CPU throttling
   docker inspect portfolio-app | grep -i cpu
   ```

3. **Check Cache Performance:**
   ```python
   # In Python console connected to app
   from performance_optimizer import cache_manager
   print(cache_manager.get_stats())
   ```

4. **Review Recent Simulations:**
   ```bash
   # Check for large scenario counts
   docker logs portfolio-app | grep "n_scenarios"
   ```

**Resolution Steps:**

1. **Clear Cache (if cache bloat suspected):**
   ```python
   # Via application admin endpoint
   curl -X POST http://localhost:8501/admin/clear-cache
   ```

2. **Scale Resources (if resource constrained):**
   ```bash
   # Increase memory limit
   docker update --memory=4g portfolio-app
   ```

3. **Enable Performance Profiling:**
   ```bash
   # Set environment variable
   docker-compose exec app sh -c "export ENABLE_PROFILING=true"
   ```

**Prevention:**
- Set up performance monitoring alerts
- Implement request timeouts
- Add rate limiting for expensive operations
- Monitor cache hit rates

---

### 3. Memory Leak / OOM Errors

**Symptoms:**
- Container restarting frequently
- OOMKilled in logs
- Memory usage continuously increasing

**Immediate Actions:**

```bash
# Check memory usage trend
docker stats portfolio-app --no-stream

# Check for OOM kills
dmesg | grep -i "out of memory"

# Check container events
docker events --since 1h | grep portfolio-app
```

**Diagnostic Steps:**

1. **Monitor Memory Growth:**
   ```bash
   # Watch memory over time
   watch -n 5 'docker stats portfolio-app --no-stream | tail -1'
   ```

2. **Check Cache Size:**
   ```bash
   docker logs portfolio-app | grep "cache.*size"
   ```

3. **Review Recent Operations:**
   ```bash
   # Look for large simulations
   docker logs portfolio-app | grep "scenarios.*5000"
   ```

**Resolution Steps:**

1. **Immediate Relief - Restart:**
   ```bash
   docker-compose restart app
   ```

2. **Clear Caches:**
   ```bash
   # Via API
   curl -X POST http://localhost:8501/admin/clear-cache
   ```

3. **Increase Memory Limit:**
   ```yaml
   # docker-compose.yml
   services:
     app:
       mem_limit: 4g
       mem_reservation: 2g
   ```

4. **Enable Memory Profiling:**
   ```bash
   docker-compose exec app python -m memory_profiler app.py
   ```

**Root Cause Analysis:**
- Use memory profiler to identify leaks
- Review cache eviction policies
- Check for large object retention
- Review recent code changes

**Prevention:**
- Implement cache size limits (already done: 500MB)
- Add memory usage monitoring
- Set up OOM alerts
- Implement periodic cache cleanup

---

### 4. High Error Rate

**Symptoms:**
- Multiple 500 errors
- Exception stack traces in logs
- Users reporting errors

**Immediate Actions:**

```bash
# Count recent errors
docker logs portfolio-app --since 10m | grep -c "ERROR"

# View error details
docker logs portfolio-app --since 10m | grep "ERROR" | tail -20

# Check error patterns
docker logs portfolio-app | grep "ERROR" | cut -d':' -f3 | sort | uniq -c | sort -rn
```

**Diagnostic Steps:**

1. **Identify Error Types:**
   ```bash
   # Group by error type
   docker logs portfolio-app | grep "Traceback" -A 10
   ```

2. **Check Recent Changes:**
   ```bash
   # Review recent deployments
   git log -5 --oneline
   ```

3. **Verify Configuration:**
   ```bash
   docker-compose exec app env | grep -E "ENV|DEBUG|LOG_LEVEL"
   ```

**Resolution Steps:**

1. **Rollback (if recent deployment):**
   ```bash
   # Pull previous image
   docker pull your-registry/portfolio-app:previous-tag
   
   # Update docker-compose.yml and restart
   docker-compose up -d
   ```

2. **Enable Debug Logging:**
   ```bash
   # Update environment
   echo "LOG_LEVEL=DEBUG" >> .env
   docker-compose restart app
   ```

3. **Check Dependencies:**
   ```bash
   docker-compose exec app pip list | grep -E "streamlit|pandas|numpy"
   ```

**Prevention:**
- Implement comprehensive error tracking
- Add input validation
- Implement circuit breakers
- Set up error rate alerts

---

### 5. Database Connection Issues

**Symptoms:**
- "Connection refused" errors
- Timeout errors
- Failed audit log writes

**Immediate Actions:**

```bash
# Check database container
docker ps | grep postgres

# Test connection
docker-compose exec app nc -zv db 5432

# Check database logs
docker logs portfolio-db --tail=100
```

**Diagnostic Steps:**

1. **Verify Database is Running:**
   ```bash
   docker-compose ps db
   ```

2. **Check Connection String:**
   ```bash
   docker-compose exec app env | grep DATABASE_URL
   ```

3. **Test Connection:**
   ```bash
   docker-compose exec db psql -U portfolio -d portfolio_db -c "SELECT 1;"
   ```

**Resolution Steps:**

1. **Restart Database:**
   ```bash
   docker-compose restart db
   ```

2. **Check Database Health:**
   ```bash
   docker-compose exec db pg_isready -U portfolio
   ```

3. **Verify Network:**
   ```bash
   docker network inspect portfolio-network
   ```

4. **Check Connection Pool:**
   ```python
   # In application
   from config import get_config
   config = get_config()
   print(config.DATABASE_URL)
   ```

**Prevention:**
- Implement connection pooling
- Add database health checks
- Set up connection retry logic
- Monitor database metrics

---

### 6. Deployment Failed

**Symptoms:**
- CI/CD pipeline failed
- Container won't start
- Health checks failing

**Immediate Actions:**

```bash
# Check CI/CD logs
gh run view --log

# View deployment logs
docker-compose logs app

# Check build logs
docker-compose build --progress=plain app
```

**Diagnostic Steps:**

1. **Check Build Errors:**
   ```bash
   docker build -t portfolio-app:test . 2>&1 | tee build.log
   ```

2. **Verify Dependencies:**
   ```bash
   docker run --rm portfolio-app:test pip check
   ```

3. **Check Configuration:**
   ```bash
   docker run --rm portfolio-app:test python -c "from config import get_config; get_config()"
   ```

**Resolution Steps:**

1. **Fix Build Issues:**
   ```bash
   # Clear build cache
   docker builder prune -af
   
   # Rebuild from scratch
   docker-compose build --no-cache app
   ```

2. **Rollback Deployment:**
   ```bash
   # Revert to previous commit
   git revert HEAD
   git push origin main
   ```

3. **Test Locally:**
   ```bash
   docker-compose -f docker-compose.yml up --build
   ```

**Prevention:**
- Test builds locally before pushing
- Implement staging environment
- Add pre-deployment checks
- Use blue-green deployments

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | Slack: #on-call | 24/7 |
| DevOps Lead | devops-lead@company.com | Business hours |
| Product Owner | product@company.com | Business hours |
| Security Team | security@company.com | 24/7 for P0 |

---

## Escalation Matrix

```
P0 (Critical - Service Down)
├─ Immediate: Notify on-call engineer
├─ +15min: Page DevOps Lead
├─ +30min: Notify Product Owner
└─ +1hr: Executive escalation

P1 (High - Degraded Performance)
├─ Immediate: Notify on-call engineer
├─ +1hr: Page DevOps Lead
└─ +2hr: Notify Product Owner

P2 (Medium - Minor Issues)
├─ During business hours: Notify team
└─ Create ticket for next business day

P3 (Low - Cosmetic/Minor)
└─ Create ticket for backlog
```

---

## Post-Incident Review Template

```markdown
# Incident Post-Mortem

**Incident ID:** INC-YYYY-MM-DD-###
**Date:** YYYY-MM-DD
**Duration:** XX hours
**Severity:** P0/P1/P2/P3

## Summary
Brief description of what happened

## Impact
- Users affected: XX
- Downtime: XX minutes
- Revenue impact: $XX

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Service restored
- HH:MM - Incident closed

## Root Cause
Detailed explanation of what caused the incident

## Resolution
Steps taken to resolve the incident

## Action Items
1. [ ] Item 1 (Owner: NAME, Due: DATE)
2. [ ] Item 2 (Owner: NAME, Due: DATE)

## Lessons Learned
- What went well
- What could be improved
- What we learned
```

---

## Useful Commands

### Health Checks
```bash
# Basic health check
curl http://localhost:8501/health

# Detailed health with metrics
curl http://localhost:8501/health/detailed

# Readiness check
curl http://localhost:8501/ready
```

### Logs
```bash
# Tail logs
docker-compose logs -f app

# Search logs
docker logs portfolio-app | grep -i "error"

# Export logs
docker logs portfolio-app > app-logs-$(date +%Y%m%d-%H%M%S).log
```

### Metrics
```bash
# View performance metrics
docker logs portfolio-app | grep "PerformanceMetrics"

# Cache statistics
docker logs portfolio-app | grep "cache_stats"

# Request duration
docker logs portfolio-app | grep "duration_ms" | awk '{print $NF}' | sort -n
```

### Database
```bash
# Connect to database
docker-compose exec db psql -U portfolio -d portfolio_db

# Backup database
docker-compose exec db pg_dump -U portfolio portfolio_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U portfolio -d portfolio_db
```

### Performance
```bash
# CPU/Memory usage
docker stats portfolio-app --no-stream

# Network connections
docker exec portfolio-app netstat -an | grep ESTABLISHED

# Disk I/O
docker exec portfolio-app iostat -x 1 5
```

---

## Additional Resources

- [Deployment Guide](../DEPLOYMENT.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Scaling Guide](SCALING.md)
- [Monitoring Dashboard](http://grafana.company.com/d/portfolio-app)
- [Log Aggregation](http://kibana.company.com)
