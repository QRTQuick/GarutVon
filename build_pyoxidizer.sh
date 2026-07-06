#!/usr/bin/env bash
set -e

# Build the GarutVON Desktop application with PyOxidizer for supported targets.
# Cross-building may require the appropriate host toolchain and target Python interpreter.

pyoxidizer build --release --target-triple x86_64-unknown-linux-gnu
pyoxidizer build --release --target-triple x86_64-apple-darwin
pyoxidizer build --release --target-triple x86_64-pc-windows-msvc

echo "Build complete. Artifacts are written to build/<target>/release/exe/."
