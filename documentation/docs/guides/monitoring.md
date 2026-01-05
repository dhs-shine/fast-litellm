# Monitoring

Monitor Fast LiteLLM performance and health in production environments.

## Health Checks

### Basic Health Check

```python
import fast_litellm

health = fast_litellm.health_check()

print(f"Status: {health['status']}")
print(f"Rust Available: {health['rust_available']}")
print(f"Components: {health['components']}")
```

### HTTP Health Endpoint

Integrate with your web framework:

```python
from flask import Flask, jsonify
import fast_litellm

app = Flask(__name__)

@app.route('/health')
def health():
    health_status = fast_litellm.health_check()
    status_code = 200 if health_status['status'] == 'ok' else 503
    return jsonify(health_status), status_code

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        'health': fast_litellm.health_check(),
        'features': fast_litellm.get_feature_status(),
        'patch_status': fast_litellm.get_patch_status(),
    })
```

## Performance Metrics

### Collecting Metrics

Fast LiteLLM automatically collects performance metrics:

```python
import fast_litellm

# Get all performance stats
stats = fast_litellm.get_performance_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

# Get stats for specific component
routing_stats = fast_litellm.get_performance_stats(component="routing")
```

### Recording Custom Metrics

Record your own performance data:

```python
import fast_litellm
import time

start = time.perf_counter()
# Your operation
result = do_something()
duration_ms = (time.perf_counter() - start) * 1000

fast_litellm.record_performance(
    component="my_component",
    operation="do_something",
    duration_ms=duration_ms,
    success=True,
    input_size=len(input_data),
    output_size=len(result)
)
```

### Comparing Implementations

Compare Rust vs Python performance:

```python
import fast_litellm

comparison = fast_litellm.compare_implementations(
    rust_component="rust_rate_limiter",
    python_component="python_rate_limiter"
)

print(f"Rust avg: {comparison.get('rust_avg_ms', 'N/A')}ms")
print(f"Python avg: {comparison.get('python_avg_ms', 'N/A')}ms")
print(f"Speedup: {comparison.get('speedup', 'N/A')}x")
```

## Feature Status Monitoring

### Check Feature Status

```python
import fast_litellm

features = fast_litellm.get_feature_status()

for name, status in features.items():
    enabled = "ON" if status.get('enabled') else "OFF"
    errors = status.get('errors', 0)
    rollout = status.get('rollout_percentage', 100)

    print(f"{name}: {enabled} (errors: {errors}, rollout: {rollout}%)")
```

### Monitor Error Rates

```python
import fast_litellm

features = fast_litellm.get_feature_status()

for name, status in features.items():
    errors = status.get('errors', 0)
    if errors > 5:
        print(f"WARNING: {name} has {errors} errors")

    # Auto-disabled after 10 errors by default
    if errors >= 10 and status.get('enabled'):
        print(f"CRITICAL: {name} should be disabled")
```

## Component-Specific Monitoring

### Rate Limiter Stats

```python
import fast_litellm

stats = fast_litellm.get_rate_limit_stats()
print(f"Total checks: {stats.get('total_checks', 0)}")
print(f"Allowed: {stats.get('allowed_count', 0)}")
print(f"Denied: {stats.get('denied_count', 0)}")
```

### Connection Pool Stats

```python
import fast_litellm

stats = fast_litellm.get_connection_pool_stats()
print(f"Total connections: {stats.get('total_connections', 0)}")
print(f"Active: {stats.get('active_connections', 0)}")
print(f"Idle: {stats.get('idle_connections', 0)}")
```

## Exporting Data

### JSON Export

```python
import fast_litellm
import json

# Export all data
data = fast_litellm.export_performance_data(format="json")
parsed = json.loads(data)

# Save to file
with open('metrics.json', 'w') as f:
    f.write(data)
```

### CSV Export

```python
import fast_litellm

csv_data = fast_litellm.export_performance_data(format="csv")

with open('metrics.csv', 'w') as f:
    f.write(csv_data)
```

### Component-Specific Export

```python
import fast_litellm

# Export only rate limiter data
rate_limit_data = fast_litellm.export_performance_data(
    component="rate_limiter",
    format="json"
)
```

## Integration with Monitoring Systems

### Prometheus

```python
from prometheus_client import Gauge, Counter
import fast_litellm

# Define metrics
rust_available = Gauge('fast_litellm_rust_available', 'Rust acceleration available')
feature_enabled = Gauge('fast_litellm_feature_enabled', 'Feature enabled', ['feature'])
feature_errors = Counter('fast_litellm_feature_errors', 'Feature errors', ['feature'])

def update_metrics():
    # Health status
    health = fast_litellm.health_check()
    rust_available.set(1 if health['rust_available'] else 0)

    # Feature status
    features = fast_litellm.get_feature_status()
    for name, status in features.items():
        feature_enabled.labels(feature=name).set(1 if status.get('enabled') else 0)
        feature_errors.labels(feature=name).inc(status.get('errors', 0))
```

### Datadog

```python
from datadog import statsd
import fast_litellm

def send_metrics():
    # Health check
    health = fast_litellm.health_check()
    statsd.gauge('fast_litellm.healthy', 1 if health['status'] == 'ok' else 0)

    # Performance stats
    stats = fast_litellm.get_performance_stats()
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            statsd.gauge(f'fast_litellm.{key}', value)

    # Component stats
    pool_stats = fast_litellm.get_connection_pool_stats()
    statsd.gauge('fast_litellm.connections.active',
                 pool_stats.get('active_connections', 0))
```

### CloudWatch

```python
import boto3
import fast_litellm

cloudwatch = boto3.client('cloudwatch')

def publish_metrics():
    health = fast_litellm.health_check()

    cloudwatch.put_metric_data(
        Namespace='FastLiteLLM',
        MetricData=[
            {
                'MetricName': 'Healthy',
                'Value': 1 if health['status'] == 'ok' else 0,
                'Unit': 'Count'
            },
        ]
    )
```

## Alerting

### Error Threshold Alerts

```python
import fast_litellm

def check_alerts():
    alerts = []

    # Check feature errors
    features = fast_litellm.get_feature_status()
    for name, status in features.items():
        errors = status.get('errors', 0)
        if errors >= 5:
            alerts.append(f"HIGH: {name} has {errors} errors")
        elif errors >= 10:
            alerts.append(f"CRITICAL: {name} disabled due to errors")

    # Check connection pool
    pool_stats = fast_litellm.get_connection_pool_stats()
    active = pool_stats.get('active_connections', 0)
    if active > 100:
        alerts.append(f"WARNING: High connection count: {active}")

    return alerts
```

### Recommendations

```python
import fast_litellm

recommendations = fast_litellm.get_recommendations()

for rec in recommendations:
    priority = rec.get('priority', 'medium')
    message = rec.get('message', 'Unknown recommendation')
    print(f"[{priority.upper()}] {message}")
```

## Dashboard Example

Create a simple monitoring dashboard:

```python
import fast_litellm
from flask import Flask, render_template_string

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Fast LiteLLM Dashboard</title></head>
<body>
    <h1>Fast LiteLLM Status</h1>

    <h2>Health</h2>
    <p>Status: {{ health.status }}</p>
    <p>Rust Available: {{ health.rust_available }}</p>

    <h2>Features</h2>
    <table border="1">
        <tr><th>Feature</th><th>Enabled</th><th>Errors</th></tr>
        {% for name, status in features.items() %}
        <tr>
            <td>{{ name }}</td>
            <td>{{ 'Yes' if status.enabled else 'No' }}</td>
            <td>{{ status.errors }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Connection Pool</h2>
    <p>Active: {{ pool_stats.active_connections }}</p>
    <p>Idle: {{ pool_stats.idle_connections }}</p>
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    return render_template_string(
        DASHBOARD_TEMPLATE,
        health=fast_litellm.health_check(),
        features=fast_litellm.get_feature_status(),
        pool_stats=fast_litellm.get_connection_pool_stats()
    )
```

## Next Steps

- [Configuration](configuration.md) - Fine-tune monitoring settings
- [Performance Tuning](performance.md) - Optimize based on metrics
