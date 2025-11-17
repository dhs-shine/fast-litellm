"""
Rust extensions compatibility layer.
This module provides access to the Rust acceleration components.
"""

# All Rust functionality is now in the main _rust module
# This file is kept for backwards compatibility

try:
    from fast_litellm import _rust
    RUST_ACCELERATION_AVAILABLE = True
except ImportError as e:
    _rust = None
    RUST_ACCELERATION_AVAILABLE = False

__all__ = [
    "RUST_ACCELERATION_AVAILABLE",
    "_rust",
]
