# Proxy Integration Guide

This guide covers deploying Fast LiteLLM with LiteLLM's proxy server for production use.

## Overview

Fast LiteLLM accelerates LiteLLM through import-time monkeypatching. For proxy mode, the key is ensuring `fast_litellm` is imported **before** the proxy server loads `litellm`.

## Gunicorn Deployment

### Option 1: Wrapper Module (Recommended)

The simplest approach is a two-line wrapper module.

**Create `app.py`:**

```python
import fast_litellm  # Apply acceleration before litellm loads
from litellm.proxy.proxy_server import app
```

**Run with gunicorn:**

```bash
gunicorn app:app --preload -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:4000
```

The `--preload` flag is important: it loads the app in the master process before forking workers. This means:
- Fast LiteLLM patches litellm once in the master process
- All workers inherit the accelerated components
- No redundant patching overhead per worker

### Option 2: Gunicorn Config File

For more control, use a gunicorn configuration file.

**Create `gunicorn_conf.py`:**

```python
import fast_litellm  # Applied before workers fork

# Server socket
bind = "0.0.0.0:4000"

# Worker processes
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

def on_starting(server):
    """Called before the master process is initialized."""
    print("Fast LiteLLM acceleration enabled")

def post_fork(server, worker):
    """Called after a worker has been forked."""
    # Verify acceleration is active in worker
    import fast_litellm
    if fast_litellm.RUST_ACCELERATION_AVAILABLE:
        print(f"Worker {worker.pid}: Rust acceleration active")
```

**Run with:**

```bash
gunicorn litellm.proxy.proxy_server:app -c gunicorn_conf.py
```

### Option 3: Combined Wrapper with Config

For production deployments, combine both approaches.

**Create `proxy_app.py`:**

```python
"""
Fast LiteLLM accelerated proxy server.

Usage:
    gunicorn proxy_app:app -c gunicorn_conf.py
"""
import os

# Configure features before import
os.environ.setdefault("FAST_LITELLM_RUST_ROUTING", "enabled")
os.environ.setdefault("FAST_LITELLM_RUST_RATE_LIMITING", "enabled")
os.environ.setdefault("FAST_LITELLM_RUST_CONNECTION_POOLING", "enabled")

# Apply acceleration
import fast_litellm

# Import the proxy app
from litellm.proxy.proxy_server import app

# Optional: Add startup event to log status
@app.on_event("startup")
async def log_acceleration_status():
    health = fast_litellm.health_check()
    print(f"Fast LiteLLM Status: {health['status']}")
    print(f"Rust Available: {health['rust_available']}")
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY gunicorn_conf.py .

# Expose port
EXPOSE 4000

# Run with gunicorn
CMD ["gunicorn", "app:app", "-c", "gunicorn_conf.py"]
```

### requirements.txt

```
fast-litellm
litellm
gunicorn
uvicorn
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  litellm-proxy:
    build: .
    ports:
      - "4000:4000"
    environment:
      - FAST_LITELLM_RUST_ROUTING=enabled
      - FAST_LITELLM_RUST_RATE_LIMITING=enabled
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
    volumes:
      - ./litellm_config.yaml:/app/litellm_config.yaml
    command: >
      gunicorn app:app
      --preload
      -w 4
      -k uvicorn.workers.UvicornWorker
      -b 0.0.0.0:4000
```

## Systemd Deployment

### Service File

Create `/etc/systemd/system/litellm-proxy.service`:

```ini
[Unit]
Description=LiteLLM Proxy with Fast LiteLLM Acceleration
After=network.target

[Service]
Type=notify
User=litellm
Group=litellm
WorkingDirectory=/opt/litellm
Environment="PATH=/opt/litellm/venv/bin"
Environment="FAST_LITELLM_RUST_ROUTING=enabled"
Environment="FAST_LITELLM_RUST_RATE_LIMITING=enabled"
ExecStart=/opt/litellm/venv/bin/gunicorn app:app \
    --preload \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:4000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable litellm-proxy
sudo systemctl start litellm-proxy
sudo systemctl status litellm-proxy
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm-proxy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: litellm-proxy
  template:
    metadata:
      labels:
        app: litellm-proxy
    spec:
      containers:
      - name: litellm-proxy
        image: your-registry/litellm-proxy:latest
        ports:
        - containerPort: 4000
        env:
        - name: FAST_LITELLM_RUST_ROUTING
          value: "enabled"
        - name: FAST_LITELLM_RUST_RATE_LIMITING
          value: "enabled"
        - name: LITELLM_MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: litellm-secrets
              key: master-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 4000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: litellm-proxy
spec:
  selector:
    app: litellm-proxy
  ports:
  - port: 4000
    targetPort: 4000
  type: ClusterIP
```

## Feature Configuration

Configure which Rust components are active via environment variables:

```bash
# Enable all Rust acceleration (default)
export FAST_LITELLM_RUST_ROUTING=enabled
export FAST_LITELLM_RUST_TOKEN_COUNTING=enabled
export FAST_LITELLM_RUST_RATE_LIMITING=enabled
export FAST_LITELLM_RUST_CONNECTION_POOLING=enabled

# Gradual rollout (10% of requests)
export FAST_LITELLM_RUST_ROUTING=canary:10

# Disable specific feature
export FAST_LITELLM_RUST_ROUTING=disabled
```

## Verifying Acceleration

### Health Check Endpoint

Add a custom health check to verify acceleration:

```python
# app.py
import fast_litellm
from litellm.proxy.proxy_server import app
from fastapi import Response
import json

@app.get("/acceleration/health")
async def acceleration_health():
    health = fast_litellm.health_check()
    status_code = 200 if health["status"] == "healthy" else 503
    return Response(
        content=json.dumps(health, indent=2),
        media_type="application/json",
        status_code=status_code
    )

@app.get("/acceleration/stats")
async def acceleration_stats():
    stats = fast_litellm.get_performance_stats()
    return stats
```

### Manual Verification

```bash
# Check if acceleration is active
curl http://localhost:4000/acceleration/health

# Get performance stats
curl http://localhost:4000/acceleration/stats
```

## Performance Tuning

### Worker Count

For CPU-bound workloads (token counting, routing):
```bash
workers = (2 * CPU_CORES) + 1
```

For I/O-bound workloads (API calls):
```bash
workers = (4 * CPU_CORES)
```

### Memory Considerations

Rust components use less memory than Python equivalents:
- Rate limiting: ~42x less memory for high-cardinality keys
- Connection pooling: ~3x more efficient

Adjust worker count based on available memory:
```python
# gunicorn_conf.py
import os

# Auto-calculate workers based on memory
total_memory_gb = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024**3)
workers = min(int(total_memory_gb / 0.5), os.cpu_count() * 2 + 1)
```

## Troubleshooting

### Acceleration Not Applied

**Symptom:** `RUST_ACCELERATION_AVAILABLE` is `False`

**Solutions:**
1. Ensure `fast_litellm` is imported before `litellm`
2. Use `--preload` flag with gunicorn
3. Check that the Rust extension is installed: `python -c "import fast_litellm._rust"`

### Import Order Issues

**Symptom:** Patching warnings or missing acceleration

**Solution:** Use the wrapper module approach to guarantee import order.

### Worker Isolation

**Symptom:** Different workers have different acceleration status

**Solution:** Always use `--preload` to ensure consistent state across workers.

### Performance Degradation

**Symptom:** Slower than expected performance

**Solutions:**
1. Check feature flags are enabled: `fast_litellm.get_feature_status()`
2. Review performance stats: `fast_litellm.get_performance_stats()`
3. Ensure Rust components are being used (not Python fallbacks)

## Monitoring

### Prometheus Metrics

Expose acceleration metrics for Prometheus:

```python
# app.py
import fast_litellm
from litellm.proxy.proxy_server import app
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

rust_calls = Counter('fast_litellm_rust_calls_total', 'Total Rust accelerated calls', ['component'])
rust_latency = Histogram('fast_litellm_rust_latency_seconds', 'Rust call latency', ['component'])

@app.get("/metrics")
async def metrics():
    # Add fast_litellm stats to metrics
    stats = fast_litellm.get_performance_stats()
    for component, data in stats.items():
        if isinstance(data, dict) and 'total_calls' in data:
            rust_calls.labels(component=component)._value.set(data['total_calls'])

    return Response(content=generate_latest(), media_type="text/plain")
```

## Next Steps

- [API Reference](api.md) - Complete API documentation
- [Contributing Guide](contributing.md) - Development setup
- [Troubleshooting Guide](../TROUBLESHOOTING.md) - Common issues
