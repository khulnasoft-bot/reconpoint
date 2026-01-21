#!/bin/bash
set -e

# DevContainer Initialization Script (runs before container is created)
# This is a lightweight setup that runs on the host

echo "Initializing DevContainer..."

# Ensure .devcontainer directory exists
mkdir -p .devcontainer

# Ensure .vscode directory exists
mkdir -p .vscode

echo "DevContainer initialization complete."
