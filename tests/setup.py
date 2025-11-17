import os
from setuptools import setup
from setuptools_rust import RustExtension, Binding

# Read the README for the long description
with open("README_pypi.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the Rust extensions
rust_extensions = [
    RustExtension(
        "fast_litellm.fast_litellm",
        path="litellm-core/Cargo.toml",
        binding=Binding.PyO3,
    ),
    RustExtension(
        "fast_litellm._rust",
        path="litellm-token/Cargo.toml",
        binding=Binding.PyO3,
    ),
    RustExtension(
        "fast_litellm._rust",
        path="litellm-connection-pool/Cargo.toml",
        binding=Binding.PyO3,
    ),
    RustExtension(
        "fast_litellm._rust",
        path="litellm-rate-limiter/Cargo.toml",
        binding=Binding.PyO3,
    ),
]

setup(
    name="fast-litellm",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="High-performance Rust acceleration for LiteLLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/fast-litellm",
    packages=["fast_litellm"],
    rust_extensions=rust_extensions,
    zip_safe=False,  # Required for Rust extensions
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Rust",
    ],
    python_requires=">=3.8",
    install_requires=[
        "litellm>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-benchmark>=3.4",
        ],
    },
)