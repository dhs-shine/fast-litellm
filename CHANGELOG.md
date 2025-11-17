# Changelog

All notable changes to Fast LiteLLM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-11-17

### Added
- Initial release of Fast LiteLLM - high-performance Rust acceleration for LiteLLM
- Advanced routing with multiple strategies (SimpleShuffle, LeastBusy, LatencyBased, CostBased)
- Fast token counting using tiktoken-rs (5-20x performance improvement)
- Efficient rate limiting (4-12x performance improvement)
- Connection pooling (2-5x performance improvement)
- Feature flag system for gradual rollout and canary deployments
- Comprehensive performance monitoring with real-time metrics
- Automatic fallback to Python implementations on errors
- Lock-free data structures using DashMap for concurrent operations
- Full async/await compatibility with Tokio integration
- Zero-configuration automatic acceleration on import
- Complete type hints and type stubs
- Comprehensive documentation and examples