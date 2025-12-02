# Troubleshooting Guide

## Quick Diagnostics

Run these commands first for any issue:

```bash
# Check all services
docker-compose ps

# View all logs
docker-compose logs --tail=100

# Check resource usage
docker stats --no-stream

# Test health endpoint
curl -i http://localhost:8501/health
```

---

## Application Issues

### Application Won't Start

**Check container status:**
```bash
docker ps -a | grep portfolio-app
```

**View startup logs:**
```bash
docker logs portfolio-app
```

**Common causes:**

1. **Port already in use:**
   ```bash
   # Check what's using port 8501
   lsof -i :8501
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **Missing environment variables:**
   ```bash
   # Check .env file exists
   ls -la .env
   
   # Verify required variables
   docker-compose config
   ```

3. **Python dependency issues:**
   ```bash
   # Check if requirements installed
   docker-compose exec app pip list
   
   # Reinstall dependencies
   docker-compose build --no-cache app
   ```

4. **Permission issues:**
   ```bash
   # Check file permissions
   ls -la /workspaces/portfolio-monte-carlo-app
   
   # Fix permissions
   chmod -R 755 /workspaces/portfolio-monte-carlo-app
   ```

**Solution:**
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

### Health Check Failing

**Test health endpoint:**
```bash
curl -v http://localhost:8501/health
```

**Check health check script:**
```bash
docker-compose exec app python healthcheck.py
```

**Common causes:**

1. **Application not fully started:**
   - Wait 30 seconds and retry
   - Check logs for initialization errors

2. **Database connection issues:**
   ```bash
   # Test database connectivity
   docker-compose exec app python -c "
   from config import get_config
   import psycopg2
   config = get_config()
   conn = psycopg2.connect(config.DATABASE_URL)
   print('Connected!')
   "
   ```

3. **Cache issues:**
   ```bash
   # Clear cache
   docker-compose exec app python -c "
   from performance_optimizer import cache_manager
   cache_manager.clear()
   print('Cache cleared')
   "
   ```

**Solution:**
```bash
# Restart with clean state
docker-compose restart app
docker-compose exec app python healthcheck.py
```

---

### Slow Performance

**Check performance metrics:**
```bash
# View recent operation times
docker logs portfolio-app | grep "duration_ms" | tail -20

# Check cache hit rate
docker logs portfolio-app | grep "cache_stats"
```

**Monitor real-time performance:**
```bash
# Create curl timing file
cat > curl-format.txt << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF

# Test response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8501/health
```

**Common causes:**

1. **High CPU usage:**
   ```bash
   docker stats portfolio-app --no-stream
   ```
   Solution: Scale resources or optimize code

2. **Memory issues:**
   ```bash
   docker stats portfolio-app | grep MEM
   ```
   Solution: Increase memory limit or clear cache

3. **Large simulation workload:**
   ```bash
   # Check for large simulations
   docker logs portfolio-app | grep "n_scenarios.*[5-9][0-9][0-9][0-9]"
   ```
   Solution: Implement request queuing or scale horizontally

4. **Cache disabled or full:**
   ```bash
   # Check cache configuration
   docker-compose exec app python -c "
   from performance_optimizer import cache_manager
   print(cache_manager.get_stats())
   "
   ```

**Performance optimization steps:**

```bash
# 1. Clear cache
curl -X POST http://localhost:8501/admin/clear-cache

# 2. Restart application
docker-compose restart app

# 3. Increase resources
docker update --memory=4g --cpus=2 portfolio-app

# 4. Enable performance profiling
docker-compose exec app python -m cProfile -o profile.stats app.py
```

---

### Memory Issues

**Check memory usage:**
```bash
docker stats portfolio-app --no-stream
```

**Monitor memory over time:**
```bash
while true; do
  docker stats --no-stream portfolio-app | tail -1
  sleep 5
done
```

**Common causes:**

1. **Cache growing too large:**
   ```bash
   # Check cache size
   docker logs portfolio-app | grep "cache.*size"
   
   # Clear cache
   docker-compose exec app python -c "
   from performance_optimizer import cache_manager
   cache_manager.clear()
   "
   ```

2. **Large DataFrame operations:**
   ```bash
   # Check for large data operations
   docker logs portfolio-app | grep "scenarios.*10000"
   ```

3. **Memory leak:**
   ```bash
   # Profile memory usage
   docker-compose exec app python -m memory_profiler app.py
   ```

**Solution:**

```bash
# Immediate: Restart
docker-compose restart app

# Short-term: Increase memory
docker-compose down
# Edit docker-compose.yml - increase mem_limit
docker-compose up -d

# Long-term: Investigate leak
docker-compose exec app python -c "
import gc
gc.collect()
print(f'Unreachable: {gc.collect()}')
"
```

---

### Database Connection Issues

**Test database connectivity:**
```bash
# Check if database is running
docker-compose ps db

# Test connection
docker-compose exec db pg_isready -U portfolio

# Test from application
docker-compose exec app python -c "
from config import get_config
import psycopg2
config = get_config()
try:
    conn = psycopg2.connect(config.DATABASE_URL)
    print('✓ Database connection successful')
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

**Common causes:**

1. **Database not running:**
   ```bash
   docker-compose ps db
   docker-compose start db
   ```

2. **Wrong connection string:**
   ```bash
   # Check environment variable
   docker-compose exec app env | grep DATABASE_URL
   
   # Should be: postgresql://portfolio:password@db:5432/portfolio_db
   ```

3. **Network issues:**
   ```bash
   # Check network
   docker network inspect portfolio-network
   
   # Test connectivity
   docker-compose exec app nc -zv db 5432
   ```

4. **Database initialization failed:**
   ```bash
   # Check database logs
   docker logs portfolio-db
   
   # Reinitialize database
   docker-compose down -v
   docker-compose up -d db
   # Wait for initialization
   sleep 10
   docker-compose up -d app
   ```

**Solution:**

```bash
# Full database reset (WARNING: destroys data)
docker-compose down -v
docker volume rm portfolio-monte-carlo-app_postgres_data
docker-compose up -d db
# Wait for initialization
sleep 15
docker-compose up -d app
```

---

## Docker Issues

### Container Won't Start

**Check container logs:**
```bash
docker logs portfolio-app
```

**Common causes:**

1. **Image build failed:**
   ```bash
   # Rebuild image
   docker-compose build --no-cache app
   ```

2. **Volume mount issues:**
   ```bash
   # Check volume permissions
   ls -la /workspaces/portfolio-monte-carlo-app
   
   # Fix permissions
   sudo chown -R 1000:1000 /workspaces/portfolio-monte-carlo-app
   ```

3. **Resource limits:**
   ```bash
   # Check Docker resources
   docker info | grep -E "CPUs|Memory"
   ```

### Image Build Fails

**Common causes:**

1. **Build context too large:**
   ```bash
   # Check .dockerignore
   cat .dockerignore
   
   # Verify build context size
   tar -czf - . | wc -c
   ```

2. **Dependency installation fails:**
   ```bash
   # Test requirements
   docker run --rm -v $(pwd):/app python:3.11-slim pip install -r /app/requirements.txt
   ```

3. **Multi-stage build issues:**
   ```bash
   # Build with debug output
   docker build --progress=plain --no-cache -t portfolio-app:debug .
   ```

**Solution:**

```bash
# Clean build
docker system prune -af
docker-compose build --no-cache
```

### Network Issues

**Check networks:**
```bash
docker network ls
docker network inspect portfolio-network
```

**Test connectivity:**
```bash
# Test between containers
docker-compose exec app ping db

# Test DNS resolution
docker-compose exec app nslookup db
```

**Solution:**

```bash
# Recreate network
docker-compose down
docker network rm portfolio-network
docker-compose up -d
```

---

## Configuration Issues

### Environment Variables Not Loaded

**Check .env file:**
```bash
# Verify file exists
ls -la .env

# Check contents (safely)
cat .env | grep -v PASSWORD
```

**Verify variables in container:**
```bash
docker-compose exec app env | grep -E "ENV|LOG_LEVEL|DATABASE"
```

**Common causes:**

1. **Missing .env file:**
   ```bash
   # Create from template
   cp .env.example .env
   # Edit with your values
   nano .env
   ```

2. **Wrong syntax in .env:**
   ```bash
   # Should be: KEY=value (no spaces, no quotes unless needed)
   # Wrong: KEY = "value"
   # Right: KEY=value
   ```

3. **Variables not passed to container:**
   ```bash
   # Check docker-compose.yml env_file section
   grep -A 5 "env_file" docker-compose.yml
   ```

**Solution:**

```bash
# Restart with new environment
docker-compose down
docker-compose up -d
```

### Configuration Not Applied

**Check configuration loading:**
```bash
docker-compose exec app python -c "
from config import get_config
config = get_config()
print(f'Environment: {config.ENV}')
print(f'Debug: {config.DEBUG}')
print(f'Log Level: {config.LOG_LEVEL}')
"
```

**Verify config file:**
```bash
# Check if config.py exists
docker-compose exec app ls -la config.py

# Test import
docker-compose exec app python -c "import config; print(dir(config))"
```

---

## Performance Issues

### Monte Carlo Simulation Too Slow

**Check simulation parameters:**
```bash
# Find recent simulations
docker logs portfolio-app | grep "n_scenarios\|n_months" | tail -10
```

**Profile performance:**
```bash
docker-compose exec app python -c "
from performance_optimizer import benchmark_monte_carlo
results = benchmark_monte_carlo()
print(results)
"
```

**Common causes:**

1. **Using loop-based implementation:**
   - Verify vectorized version is being used
   - Check `performance_optimizer.py` is imported

2. **Very large scenario counts:**
   - Consider chunking or async processing
   - Implement request queuing

3. **Cache disabled:**
   ```bash
   # Check cache status
   docker logs portfolio-app | grep cache
   ```

**Solution:**

```bash
# Ensure using vectorized implementation
docker-compose exec app python -c "
from app import run_monte_carlo
import inspect
print(inspect.getsource(run_monte_carlo))
" | grep vectorized
```

### Cache Not Working

**Check cache statistics:**
```bash
docker-compose exec app python -c "
from performance_optimizer import cache_manager
stats = cache_manager.get_stats()
print(f'Entries: {stats[\"num_entries\"]}')
print(f'Size: {stats[\"total_size_mb\"]:.2f} MB')
print(f'Utilization: {stats[\"utilization_pct\"]:.1f}%')
"
```

**Common causes:**

1. **Cache cleared on restart:**
   - Expected behavior (cache is in-memory)
   - Consider persistent cache (Redis)

2. **TTL expired:**
   - Check TTL settings (default 3600s = 1 hour)

3. **Cache keys not matching:**
   - Ensure input parameters are consistent

**Solution:**

```bash
# Clear and rebuild cache
docker-compose exec app python -c "
from performance_optimizer import cache_manager
cache_manager.clear()
print('Cache cleared')
"

# Restart application
docker-compose restart app
```

---

## Security Issues

### Suspicious Activity Detected

**Check logs for suspicious patterns:**
```bash
# Look for unusual access patterns
docker logs portfolio-app | grep -E "401|403|429"

# Check for injection attempts
docker logs portfolio-app | grep -E "DROP|SELECT|UNION|<script>"

# Review recent API calls
docker logs portfolio-app | grep "correlation_id" | tail -50
```

**Rate limiting triggered:**
```bash
# Check rate limit violations
docker logs portfolio-app | grep "rate_limit_exceeded"
```

**Action:**
```bash
# Block suspicious IP (if using reverse proxy)
# Add to firewall or WAF rules

# Increase security logging
docker-compose exec app python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"
```

### Exposed Secrets

**Check for secrets in logs:**
```bash
# Search for potential secrets (passwords, tokens, keys)
docker logs portfolio-app | grep -iE "password|secret|token|key" | grep -v "***"
```

**Immediate action:**
```bash
# 1. Rotate exposed secrets immediately
# 2. Clear logs
docker logs portfolio-app > /dev/null 2>&1

# 3. Update configuration
nano .env  # Update secrets

# 4. Restart with new secrets
docker-compose down
docker-compose up -d
```

---

## Monitoring Issues

### Logs Not Appearing

**Check logging configuration:**
```bash
# Verify log level
docker-compose exec app env | grep LOG_LEVEL

# Test logging
docker-compose exec app python -c "
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Test log message')
"
```

**Check log drivers:**
```bash
docker inspect portfolio-app | grep -A 5 LogConfig
```

### Metrics Not Collected

**Check observability module:**
```bash
# Test observability
docker-compose exec app python -c "
from observability import logger, get_correlation_id
logger.info('Test metrics', extra={'correlation_id': get_correlation_id()})
"
```

**Verify metrics endpoint:**
```bash
curl http://localhost:8501/metrics
```

---

## Deployment Issues

### CI/CD Pipeline Failing

**Check GitHub Actions:**
```bash
# View recent runs
gh run list --limit 5

# View specific run
gh run view <run-id> --log
```

**Common causes:**

1. **Test failures:**
   ```bash
   # Run tests locally
   docker-compose exec app pytest test_*.py -v
   ```

2. **Build failures:**
   ```bash
   # Test build locally
   docker build -t portfolio-app:test .
   ```

3. **Secrets not configured:**
   - Check GitHub repository secrets
   - Verify secret names match workflow

### Deployment to Cloud Failed

**Check deployment logs:**
```bash
# AWS ECS
aws ecs describe-services --cluster portfolio-cluster --services portfolio-app

# Kubernetes
kubectl describe deployment portfolio-app
kubectl logs -l app=portfolio-app --tail=100
```

**Common causes:**

1. **Image not pushed:**
   - Verify image in registry
   - Check registry authentication

2. **Resource constraints:**
   - Check cluster capacity
   - Verify resource requests/limits

3. **Configuration errors:**
   - Verify environment variables
   - Check secrets mounted correctly

---

## Emergency Procedures

### Complete System Reset

**⚠️ WARNING: This will destroy all data!**

```bash
# 1. Stop all services
docker-compose down -v

# 2. Remove all containers and images
docker system prune -af

# 3. Remove volumes
docker volume prune -f

# 4. Rebuild from scratch
docker-compose build --no-cache

# 5. Start services
docker-compose up -d

# 6. Verify health
sleep 30
curl http://localhost:8501/health
```

### Emergency Rollback

```bash
# 1. Identify working version
git log --oneline -10

# 2. Checkout previous version
git checkout <commit-hash>

# 3. Rebuild and deploy
docker-compose down
docker-compose build
docker-compose up -d

# 4. Verify
curl http://localhost:8501/health
```

---

## Getting Help

### Collect Diagnostic Information

```bash
#!/bin/bash
# Save as: collect-diagnostics.sh

echo "Collecting diagnostics..."
mkdir -p diagnostics

# System info
docker version > diagnostics/docker-version.txt
docker-compose version > diagnostics/compose-version.txt

# Container status
docker-compose ps > diagnostics/containers.txt

# Logs
docker logs portfolio-app > diagnostics/app-logs.txt 2>&1
docker logs portfolio-db > diagnostics/db-logs.txt 2>&1

# Configuration
docker-compose config > diagnostics/config.yml

# Resources
docker stats --no-stream > diagnostics/resources.txt

# Network
docker network inspect portfolio-network > diagnostics/network.json

# Create archive
tar -czf diagnostics-$(date +%Y%m%d-%H%M%S).tar.gz diagnostics/
echo "Diagnostics collected: diagnostics-$(date +%Y%m%d-%H%M%S).tar.gz"
```

### Contact Support

When contacting support, provide:

1. Diagnostics archive (see above)
2. What you were trying to do
3. What actually happened
4. Steps to reproduce
5. Expected vs actual behavior
6. Recent changes made

---

## Additional Resources

- [Incident Response Runbook](INCIDENT_RESPONSE.md)
- [Scaling Guide](SCALING.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Performance Optimization Guide](../PERFORMANCE_OPTIMIZATION_GUIDE.md)
