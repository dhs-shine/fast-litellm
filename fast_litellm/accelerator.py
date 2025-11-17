"""
LiteLLM Rust Acceleration - Drop-in replacement for performance-critical components
"""
import logging
from typing import Any, Dict, Optional

from .rust_extensions import (
    RUST_ACCELERATION_AVAILABLE,
    fast_litellm,
    _rust,
    _rust,
    _rust,
)
from . import monkeypatch

# Set up logging
logger = logging.getLogger(__name__)

def apply_acceleration() -> bool:
    """
    Apply Rust acceleration by monkeypatching LiteLLM classes.
    
    Returns:
        bool: True if acceleration was applied successfully, False otherwise
    """
    if not RUST_ACCELERATION_AVAILABLE:
        logger.warning("Rust acceleration is not available. Falling back to Python implementations.")
        return False
    
    logger.info("Applying Rust acceleration to LiteLLM components...")
    
    # Use the monkeypatch module to apply acceleration
    try:
        # Create a mock module with the rust extensions
        class MockRustExtensions:
            pass
        
        mock_module = MockRustExtensions()
        mock_module.RUST_ACCELERATION_AVAILABLE = RUST_ACCELERATION_AVAILABLE
        mock_module.fast_litellm = fast_litellm
        mock_module._rust = _rust
        mock_module._rust = _rust
        mock_module._rust = _rust
        
        return monkeypatch.apply_acceleration(mock_module)
    except Exception as e:
        logger.error(f"Failed to apply Rust acceleration: {e}")
        return False

def remove_acceleration() -> None:
    """
    Remove Rust acceleration and restore original Python implementations.
    """
    monkeypatch.remove_acceleration()

# Automatically apply acceleration when the module is imported
if RUST_ACCELERATION_AVAILABLE:
    apply_acceleration()
else:
    logger.info("Rust acceleration is not available. Install with Rust components for better performance.")