# Token Counting

Fast LiteLLM provides accelerated token counting using Rust and tiktoken. For large texts, this achieves **1.5-1.7x faster** token counting compared to Python implementations.

## Overview

Token counting is essential for:

- Estimating API costs
- Validating input lengths
- Managing context windows
- Batch processing optimization

### Key Features

- **tiktoken-based counting** for accurate BPE tokenization
- **Model-specific encodings** for accurate results
- **Batch processing** for multiple texts
- **Cost estimation** based on model pricing

## Performance

| Text Size | Python | Rust | Improvement |
|-----------|--------|------|-------------|
| Small (< 100 tokens) | 1.6ms | 3.1ms | Python faster |
| Large (1000+ chars) | 23.4ms | 13.9ms | **1.7x faster** |

!!! note
    For small texts, Python's tiktoken has lower overhead due to FFI costs. Rust acceleration is most beneficial for large texts and batch operations.

## Basic Usage

### Automatic Acceleration

Token counting is automatically accelerated when you import `fast_litellm`:

```python
import fast_litellm
import litellm

# Token counting is now accelerated
tokens = litellm.encode(model="gpt-3.5-turbo", text="Hello, world!")
print(f"Token count: {len(tokens)}")

# Count tokens in messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"},
]
count = litellm.token_counter(model="gpt-3.5-turbo", messages=messages)
print(f"Message tokens: {count}")
```

### Direct API Access

Use the token counter directly:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

# Count tokens
count = counter.count_tokens("Hello, world!", model="gpt-3.5-turbo")
print(f"Tokens: {count}")

# Batch counting
texts = [
    "First text to count",
    "Second text to count",
    "Third text to count",
]
counts = counter.count_tokens_batch(texts, model="gpt-3.5-turbo")
print(f"Counts: {counts}")
```

## API Reference

### SimpleTokenCounter

```python
class SimpleTokenCounter:
    def __init__(self, model_max_tokens: int = 4096) -> None:
        """Create a token counter with optional max tokens limit."""

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in a text string."""

    def count_tokens_batch(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[int]:
        """Count tokens for multiple texts at once."""

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost for a request in USD."""

    def get_model_limits(self, model: str) -> Dict[str, Any]:
        """Get token limits for a model."""

    def validate_input(self, text: str, model: str) -> bool:
        """Validate that input doesn't exceed model limits."""

    @property
    def model_max_tokens(self) -> int:
        """Get the configured max tokens limit."""
```

## Model Support

The token counter supports all major models:

| Provider | Models | Encoding |
|----------|--------|----------|
| OpenAI | GPT-3.5, GPT-4, GPT-4o | cl100k_base |
| Anthropic | Claude 2, Claude 3 | cl100k_base |
| Google | Gemini, PaLM | cl100k_base |

## Cost Estimation

Estimate API costs before making requests:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

# Count tokens
text = "Your long prompt here..."
input_tokens = counter.count_tokens(text, "gpt-4")

# Estimate cost (assuming 100 output tokens)
cost = counter.estimate_cost(
    input_tokens=input_tokens,
    output_tokens=100,
    model="gpt-4"
)
print(f"Estimated cost: ${cost:.4f}")
```

## Input Validation

Validate inputs before sending to the API:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

text = "Your potentially long text..."

if counter.validate_input(text, "gpt-3.5-turbo"):
    # Text is within limits
    response = make_api_call(text)
else:
    # Text exceeds model limits
    print("Text is too long for this model")
```

## Model Limits

Get token limits for any model:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

limits = counter.get_model_limits("gpt-4")
print(f"Max input tokens: {limits.get('max_input_tokens', 'unknown')}")
print(f"Max output tokens: {limits.get('max_output_tokens', 'unknown')}")
print(f"Context window: {limits.get('context_window', 'unknown')}")
```

## Batch Processing

For processing multiple texts efficiently:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

# Process a batch of texts
texts = [
    "First document content...",
    "Second document content...",
    "Third document content...",
    # ... potentially many more
]

# Count all at once (more efficient)
counts = counter.count_tokens_batch(texts, model="gpt-3.5-turbo")

# Filter texts that exceed limits
max_tokens = 4000
valid_texts = [
    text for text, count in zip(texts, counts)
    if count <= max_tokens
]
```

## When to Use Rust vs Python

### Use Rust Acceleration For:

- Large documents (1000+ characters)
- Batch processing of multiple texts
- High-throughput token counting
- Memory-constrained environments

### Use Python For:

- Small texts (< 100 tokens)
- One-off token counts
- When FFI overhead matters

## How It Works

The Rust implementation uses tiktoken-rs with cached encodings:

```rust
// Simplified implementation
use std::sync::RwLock;
use tiktoken_rs::CoreBPE;

static ENCODINGS: RwLock<HashMap<String, CoreBPE>> = RwLock::new(HashMap::new());

fn count_tokens(text: &str, model: &str) -> usize {
    // Get or create encoding (cached)
    let encoding = get_encoding(model);
    encoding.encode_ordinary(text).len()
}
```

The caching strategy ensures that encoding initialization happens only once per model, amortizing the setup cost across many calls.

## Next Steps

- [Routing](routing.md) - Learn about advanced routing
- [Performance Tuning](../guides/performance.md) - Optimize token counting
