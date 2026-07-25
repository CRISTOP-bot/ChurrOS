#!/usr/bin/env bash

VERSION_FILE="$(cd "$(dirname "$0")/../.." && pwd)/VERSION"

echo "ChurrOS CLI"
echo
echo "Version : $(cat "$VERSION_FILE")"
echo "Shell   : Bash"
echo