# Routing

Fast LiteLLM provides advanced routing capabilities for distributing requests across multiple model deployments. The router supports multiple strategies for optimal load distribution.

## Overview

The router helps you:

- Distribute requests across multiple deployments
- Implement failover and load balancing
- Optimize for latency or cost
- Handle blocked or unavailable models

### Key Features

- **Multiple routing strategies** (shuffle, least busy, latency-based, cost-based)
- **Thread-safe concurrent access** using DashMap
- **Real-time metrics tracking**
- **Automatic failover** to available deployments

## Performance

!!! note
    Routing performance depends heavily on the complexity of your model list and the routing strategy used. For simple cases, Python may be faster due to FFI overhead. For complex deployments with many models, Rust provides better scalability.

## Basic Usage

### Automatic Acceleration

Routing is automatically accelerated when you import `fast_litellm`:

```python
import fast_litellm
import litellm

# Configure multiple deployments
litellm.model_list = [
    {
        "model_name": "gpt-4",
        "litellm_params": {"model": "openai/gpt-4", "api_key": "key1"}
    },
    {
        "model_name": "gpt-4",
        "litellm_params": {"model": "azure/gpt-4", "api_key": "key2"}
    },
]

# Routing is now accelerated
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Direct API Access

Use the router directly:

```python
from fast_litellm import AdvancedRouter

router = AdvancedRouter(strategy="simple_shuffle")

# Define your deployments
deployments = [
    {"model_name": "gpt-4", "endpoint": "https://api.openai.com"},
    {"model_name": "gpt-4", "endpoint": "https://api.azure.com"},
    {"model_name": "gpt-3.5-turbo", "endpoint": "https://api.openai.com"},
]

# Get an available deployment
deployment = router.get_available_deployment(
    model_list=deployments,
    model="gpt-4"
)

if deployment:
    print(f"Using: {deployment['endpoint']}")
```

## Routing Strategies

### Simple Shuffle (Default)

Randomly selects from available deployments:

```python
router = AdvancedRouter(strategy="simple_shuffle")
```

Best for: Even distribution across healthy deployments

### Least Busy

Routes to the deployment with the fewest active requests:

```python
router = AdvancedRouter(strategy="least_busy")
```

Best for: Balancing load across deployments

### Latency-Based

Routes to the deployment with the lowest average latency:

```python
router = AdvancedRouter(strategy="latency_based")
```

Best for: Minimizing response time

### Cost-Based

Routes to the most cost-effective deployment:

```python
router = AdvancedRouter(strategy="cost_based")
```

Best for: Minimizing API costs

## API Reference

### AdvancedRouter

```python
class AdvancedRouter:
    def __init__(self, strategy: str = "simple_shuffle") -> None:
        """
        Create a router with specified strategy.

        Args:
            strategy: One of "simple_shuffle", "least_busy",
                     "latency_based", "cost_based"
        """

    def get_available_deployment(
        self,
        model_list: List[Dict],
        model: str,
        blocked_models: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get an available deployment for the specified model.

        Args:
            model_list: List of deployment configurations
            model: The model name to route to
            blocked_models: Models to exclude from routing

        Returns:
            A deployment dict or None if no deployment available
        """

    @property
    def strategy(self) -> str:
        """Get the current routing strategy."""
```

### Standalone Function

```python
deployment = fast_litellm.get_available_deployment(
    model_list=[...],
    model="gpt-4",
    blocked_models=["gpt-4-preview"],
    context=None,
    settings=None
)
```

## Blocking Models

Exclude specific models from routing:

```python
from fast_litellm import AdvancedRouter

router = AdvancedRouter()

# Block a problematic deployment
deployment = router.get_available_deployment(
    model_list=deployments,
    model="gpt-4",
    blocked_models=["gpt-4-azure-east"]  # Skip this deployment
)
```

## Deployment Configuration

Each deployment in the model list should include:

```python
deployment = {
    "model_name": "gpt-4",              # Model identifier
    "litellm_params": {
        "model": "openai/gpt-4",        # Provider/model
        "api_key": "your-api-key",      # API credentials
        "api_base": "https://...",      # Optional: custom endpoint
    },
    # Optional metadata
    "metadata": {
        "region": "us-east-1",
        "priority": 1,
    }
}
```

## Failover Example

Implement automatic failover:

```python
import fast_litellm
import litellm

def call_with_failover(messages, max_retries=3):
    deployments = litellm.model_list.copy()
    blocked = []

    for attempt in range(max_retries):
        deployment = fast_litellm.get_available_deployment(
            model_list=deployments,
            model="gpt-4",
            blocked_models=blocked
        )

        if not deployment:
            raise Exception("No deployments available")

        try:
            return litellm.completion(
                model=deployment["model_name"],
                messages=messages
            )
        except Exception as e:
            # Block this deployment and retry
            blocked.append(deployment["model_name"])
            print(f"Deployment failed, trying next: {e}")

    raise Exception("All deployments failed")
```

## Load Balancing Example

Implement weighted load balancing:

```python
from fast_litellm import AdvancedRouter

router = AdvancedRouter(strategy="least_busy")

# Deployments with different capacities
deployments = [
    {"model_name": "gpt-4", "capacity": 100, "endpoint": "primary"},
    {"model_name": "gpt-4", "capacity": 50, "endpoint": "secondary"},
]

def get_best_deployment():
    return router.get_available_deployment(
        model_list=deployments,
        model="gpt-4"
    )
```

## How It Works

The Rust implementation uses DashMap for thread-safe concurrent access:

```rust
// Simplified implementation
use dashmap::DashMap;

struct Router {
    metrics: DashMap<String, DeploymentMetrics>,
    strategy: String,
}

impl Router {
    fn get_deployment(&self, model: &str) -> Option<Deployment> {
        match self.strategy.as_str() {
            "least_busy" => self.get_least_busy(model),
            "latency_based" => self.get_lowest_latency(model),
            _ => self.get_random(model),
        }
    }
}
```

## Next Steps

- [Configuration](../guides/configuration.md) - Configure routing behavior
- [Performance Tuning](../guides/performance.md) - Optimize routing performance
