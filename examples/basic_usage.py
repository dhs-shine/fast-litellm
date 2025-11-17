#!/usr/bin/env python3
"""
Example usage of LiteLLM Rust acceleration.
"""

import fast_litellm

def main():
    print("LiteLLM Rust Acceleration Example")
    print("=" * 35)
    
    # Check if Rust acceleration is available
    if fast_litellm.RUST_ACCELERATION_AVAILABLE:
        print("✓ Rust acceleration is available")
    else:
        print("✗ Rust acceleration is not available")
        return
    
    # Run health check
    from fast_litellm.diagnostics import health_check
    health = health_check()
    print(f"✓ Overall health: {health['overall_healthy']}")
    
    # Show component health
    for component_name, component_data in health["components"].items():
        healthy = component_data.get("healthy", False) or component_data.get("core_healthy", False) or component_data.get("token_healthy", False) or component_data.get("connection_pool_healthy", False) or component_data.get("rate_limiter_healthy", False)
        print(f"  {component_name}: {'✓' if healthy else '✗'}")
    
    # Demonstrate usage of Rust components
    print("\nDemonstrating Rust components:")
    
    # Token counting
    try:
        from fast_litellm.rust_extensions import _rust
        counter = _rust.SimpleTokenCounter(100)
        text = "This is a sample text for token counting."
        token_count = counter.count_tokens(text, "gpt-3.5-turbo")
        print(f"✓ Token count for '{text}': {token_count}")
    except Exception as e:
        print(f"✗ Token counting failed: {e}")
    
    # Rate limiting
    try:
        from fast_litellm.rust_extensions import _rust
        limiter = _rust.SimpleRateLimiter()
        within_limit = limiter.check_rate_limit("user123", 100, 60)
        print(f"✓ Rate limit check: {within_limit}")
    except Exception as e:
        print(f"✗ Rate limiting failed: {e}")
    
    # Core functionality
    try:
        from fast_litellm.rust_extensions import fast_litellm
        core = fast_litellm.LiteLLMCore()
        print(f"✓ Core available: {core.is_available()}")
    except Exception as e:
        print(f"✗ Core functionality failed: {e}")

if __name__ == "__main__":
    main()