#!/usr/bin/env python3
"""
Test script to verify that the package structure is correct and can be imported.
"""

def test_package_import():
    """Test that the package can be imported."""
    try:
        import fast_litellm
        print("✓ fast_litellm package imported successfully")
        print(f"  Version: {fast_litellm.__version__}")
        print(f"  Rust acceleration available: {fast_litellm.RUST_ACCELERATION_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import fast_litellm: {e}")
        return False

def test_package_components():
    """Test that package components can be accessed."""
    try:
        import fast_litellm
        
        # Test that key functions are available
        assert hasattr(fast_litellm, 'apply_acceleration')
        assert hasattr(fast_litellm, 'remove_acceleration')
        assert hasattr(fast_litellm, 'health_check')
        assert hasattr(fast_litellm, 'get_performance_stats')
        
        print("✓ All package components are accessible")
        return True
    except (ImportError, AssertionError) as e:
        print(f"✗ Failed to access package components: {e}")
        return False

def test_rust_extensions():
    """Test that Rust extensions can be imported."""
    try:
        import fast_litellm
        
        if fast_litellm.RUST_ACCELERATION_AVAILABLE:
            # Try to import the Rust extensions directly
            from fast_litellm import fast_litellm
            from fast_litellm import _rust
            from fast_litellm import _rust
            from fast_litellm import _rust
            
            print("✓ All Rust extensions imported successfully")
            return True
        else:
            print("ℹ Rust acceleration not available, skipping extension tests")
            return True
    except ImportError as e:
        print(f"✗ Failed to import Rust extensions: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing LiteLLM Rust Acceleration Package Structure")
    print("=" * 55)
    
    tests = [
        test_package_import,
        test_package_components,
        test_rust_extensions,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All package structure tests passed!")
        return True
    else:
        print("❌ Some package structure tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)