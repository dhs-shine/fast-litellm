"""Basic tests for fast_litellm package"""

import pytest


def test_import_package():
    """Test that the package can be imported"""
    try:
        import fast_litellm
        assert hasattr(fast_litellm, '__version__')
        assert hasattr(fast_litellm, 'RUST_ACCELERATION_AVAILABLE')
    except ImportError:
        pytest.skip("Package not built yet")


def test_health_check():
    """Test basic health check functionality"""
    try:
        import fast_litellm
        health = fast_litellm.health_check()
        assert isinstance(health, dict)
        assert 'status' in health
    except ImportError:
        pytest.skip("Package not built yet")


def test_feature_flags():
    """Test feature flag functionality"""
    try:
        import fast_litellm

        # Test getting feature status
        status = fast_litellm.get_feature_status()
        assert isinstance(status, dict)

        # Test checking if a feature is enabled
        enabled = fast_litellm.is_enabled('test_feature')
        assert isinstance(enabled, bool)

    except ImportError:
        pytest.skip("Package not built yet")


def test_performance_monitoring():
    """Test performance monitoring functionality"""
    try:
        import fast_litellm

        # Test recording performance data
        fast_litellm.record_performance(
            component="test",
            operation="test_op",
            duration_ms=10.5,
            success=True
        )

        # Test getting performance stats
        stats = fast_litellm.get_performance_stats()
        assert isinstance(stats, dict)

    except ImportError:
        pytest.skip("Package not built yet")


@pytest.mark.asyncio
async def test_async_compatibility():
    """Test that the package works with async code"""
    try:
        import fast_litellm
        import asyncio

        # Test async health check
        async def async_health_check():
            return fast_litellm.health_check()

        result = await async_health_check()
        assert isinstance(result, dict)

    except ImportError:
        pytest.skip("Package not built yet")