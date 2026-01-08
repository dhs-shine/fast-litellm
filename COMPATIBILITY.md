# Compatibility Report

Generated: 2026-01-08

## Supported Versions

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| **Python** | 3.9, 3.10, 3.11, 3.12, 3.13 | 3.11+ recommended |
| **Platforms** | Linux, macOS, Windows | See platform details below |
| **Rust** | 1.70+ | Only needed for building from source |
| **LiteLLM** | Latest stable | Some versions may have syntax incompatibilities |

## Test Matrix

### Verified Configurations

| Platform | Python | Fast LiteLLM | Status | Notes |
|----------|--------|--------------|--------|-------|
| Linux x86_64 | 3.11.14 | 0.1.7 | ✅ Pass | Primary test environment |

### Target Configurations (CI)

| Platform | Python Versions | Status |
|----------|-----------------|--------|
| Linux x86_64 | 3.9, 3.10, 3.11, 3.12, 3.13 | Targeted |
| Linux aarch64 | 3.9, 3.10, 3.11, 3.12, 3.13 | Targeted |
| macOS x86_64 | 3.9, 3.10, 3.11, 3.12, 3.13 | Targeted |
| macOS ARM64 | 3.9, 3.10, 3.11, 3.12, 3.13 | Targeted |
| Windows x86_64 | 3.9, 3.10, 3.11, 3.12, 3.13 | Targeted |

## Known Issues

### Python 3.9 - LiteLLM Syntax Compatibility

Some LiteLLM versions use Python 3.10+ union syntax (`str | List[str]`) which causes `TypeError` on Python 3.9.

**Workarounds:**
1. Upgrade to Python 3.10+
2. Use an older LiteLLM version
3. Fast LiteLLM core features work without LiteLLM integration

**Status:** Fast LiteLLM gracefully handles this with automatic fallback.

### macOS - ARM64 Build

Building from source on Apple Silicon requires:
```bash
rustup target add aarch64-apple-darwin
```

### Windows - Long Path Support

Windows users may need to enable long path support for deep node_modules:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## Platform Details

### Linux

- **Distributions tested:** Ubuntu 22.04, Debian 12
- **Architectures:** x86_64, aarch64
- **Notes:** Primary development platform, best tested

### macOS

- **Versions:** macOS 12+
- **Architectures:** x86_64 (Intel), ARM64 (Apple Silicon)
- **Notes:** Universal binary support planned

### Windows

- **Versions:** Windows 10+, Windows Server 2019+
- **Architecture:** x86_64
- **Notes:** MSVC toolchain required for building from source

## Installation Methods

| Method | Rust Required | Platform Support |
|--------|---------------|------------------|
| `pip install fast-litellm` | No | All (prebuilt wheels) |
| `uv add fast-litellm` | No | All (prebuilt wheels) |
| Build from source | Yes | All |

## Reporting Issues

If you encounter compatibility issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Run diagnostics: `python -c "import fast_litellm; print(fast_litellm.health_check())"`
3. Open an issue with:
   - Python version (`python --version`)
   - Platform (`uname -a` or `systeminfo`)
   - Fast LiteLLM version
   - Full error traceback
