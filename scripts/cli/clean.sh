#!/usr/bin/env bash

set -e

echo "Cleaning build directories..."

if mountpoint -q work 2>/dev/null; then
    echo "  work is mounted (tmpfs) — cleaning contents..."
    sudo find work -mindepth 1 -delete 2>/dev/null || sudo rm -rf work/* 2>/dev/null || true
else
    sudo rm -rf work
fi
sudo rm -rf out
mkdir -p out

echo "Done."
