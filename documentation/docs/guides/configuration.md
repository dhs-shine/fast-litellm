# Configuration

Fast LiteLLM works with zero configuration, but provides extensive options for fine-tuning behavior.

## Environment Variables

### Global Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `FAST_LITELLM_ENABLED` | `true` | Enable/disable all acceleration |
| `FAST_LITELLM_FEATURE_CONFIG` | - | Path to JSON configuration file |

### Feature Toggles

Enable or disable specific features:

```bash
# Disable specific features
export FAST_LITELLM_RUST_ROUTING=false
export FAST_LITELLM_RUST_TOKEN_COUNTING=false
export FAST_LITELLM_RUST_RATE_LIMITING=false
export FAST_LITELLM_RUST_CONNECTION_POOL=false
```

### Gradual Rollout

Enable features for a percentage of traffic:

```bash
# Enable for 10% of traffic (canary deployment)
export FAST_LITELLM_BATCH_TOKEN_COUNTING=canary:10

# Enable for 50% of traffic
export FAST_LITELLM_RUST_ROUTING=rollout:50
```

## Configuration File

Create a JSON configuration file for complex setups:

```json
{
  "features": {
    "rust_routing": {
      "enabled": true,
      "rollout_percentage": 100
    },
    "rust_token_counting": {
      "enabled": true,
      "rollout_percentage": 100
    },
    "rust_rate_limiting": {
      "enabled": true,
      "rollout_percentage": 100,
      "config": {
        "requests_per_minute": 100,
        "burst_size": 10
      }
    },
    "rust_connection_pool": {
      "enabled": true,
      "rollout_percentage": 100,
      "config": {
        "max_connections_per_endpoint": 10,
        "idle_timeout_seconds": 300
      }
    }
  },
  "monitoring": {
    "enabled": true,
    "sample_rate": 0.1
  },
  "fallback": {
    "auto_disable_on_errors": true,
    "max_errors_before_disable": 10
  }
}
```

Load the configuration:

```bash
export FAST_LITELLM_FEATURE_CONFIG=/path/to/config.json
```

## Programmatic Configuration

Configure features at runtime:

```python
import fast_litellm

# Check current feature status
features = fast_litellm.get_feature_status()
print(features)

# Features are controlled via environment variables
# or configuration file - no runtime toggle API
```

## Rate Limiter Configuration

### Default Settings

```python
from fast_litellm import SimpleRateLimiter

# Default: 60 requests per minute
limiter = SimpleRateLimiter()

# Custom rate
limiter = SimpleRateLimiter(requests_per_minute=100)
```

### Per-Key Limits

Rate limits are applied per-key, allowing different limits for different users:

```python
from fast_litellm import SimpleRateLimiter

# Create limiters with different rates
standard_limiter = SimpleRateLimiter(requests_per_minute=60)
premium_limiter = SimpleRateLimiter(requests_per_minute=300)

def handle_request(user_type: str, user_id: str):
    if user_type == "premium":
        allowed = premium_limiter.is_allowed(user_id)
    else:
        allowed = standard_limiter.is_allowed(user_id)
    return allowed
```

## Connection Pool Configuration

### Pool Settings

```python
from fast_litellm import SimpleConnectionPool

# Default pool
pool = SimpleConnectionPool()

# Named pool
pool = SimpleConnectionPool(pool_name="openai_pool")
```

### Connection Cleanup

Configure automatic cleanup:

```python
import threading
import time
import fast_litellm

def cleanup_worker():
    while True:
        fast_litellm.cleanup_expired_connections()
        time.sleep(60)  # Run every minute

# Start background cleanup
thread = threading.Thread(target=cleanup_worker, daemon=True)
thread.start()
```

## Router Configuration

### Strategy Selection

```python
from fast_litellm import AdvancedRouter

# Available strategies
router_shuffle = AdvancedRouter(strategy="simple_shuffle")
router_busy = AdvancedRouter(strategy="least_busy")
router_latency = AdvancedRouter(strategy="latency_based")
router_cost = AdvancedRouter(strategy="cost_based")
```

## Monitoring Configuration

### Enable Performance Tracking

Performance tracking is enabled by default. Configure sampling:

```json
{
  "monitoring": {
    "enabled": true,
    "sample_rate": 0.1
  }
}
```

### Export Data

```python
import fast_litellm

# Export as JSON
json_data = fast_litellm.export_performance_data(format="json")

# Export as CSV
csv_data = fast_litellm.export_performance_data(format="csv")

# Export specific component
routing_data = fast_litellm.export_performance_data(
    component="routing",
    format="json"
)
```

## Error Handling Configuration

### Automatic Fallback

Configure automatic fallback behavior:

```json
{
  "fallback": {
    "auto_disable_on_errors": true,
    "max_errors_before_disable": 10
  }
}
```

### Reset Errors

```python
import fast_litellm

# Reset all error counts
fast_litellm.reset_errors()

# Reset specific feature
fast_litellm.reset_errors("rust_routing")
```

## Production Recommendations

### Recommended Configuration

```json
{
  "features": {
    "rust_routing": {
      "enabled": true,
      "rollout_percentage": 100
    },
    "rust_token_counting": {
      "enabled": true,
      "rollout_percentage": 100
    },
    "rust_rate_limiting": {
      "enabled": true,
      "rollout_percentage": 100
    },
    "rust_connection_pool": {
      "enabled": true,
      "rollout_percentage": 100
    }
  },
  "monitoring": {
    "enabled": true,
    "sample_rate": 0.01
  },
  "fallback": {
    "auto_disable_on_errors": true,
    "max_errors_before_disable": 10
  }
}
```

### Gradual Rollout Strategy

1. **Start with canary** (5-10% of traffic):
   ```bash
   export FAST_LITELLM_RUST_ROUTING=canary:5
   ```

2. **Monitor metrics** for errors and performance

3. **Increase rollout** gradually:
   ```bash
   export FAST_LITELLM_RUST_ROUTING=rollout:50
   ```

4. **Full rollout** when confident:
   ```bash
   export FAST_LITELLM_RUST_ROUTING=true
   ```

## Next Steps

- [Performance Tuning](performance.md) - Optimize for your workload
- [Monitoring](monitoring.md) - Set up monitoring and alerting
