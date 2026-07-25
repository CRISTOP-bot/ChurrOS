#!/usr/bin/env bash

VERSION_FILE="$(cd "$(dirname "$0")/../.." && pwd)/VERSION"

echo "===================================="
echo "          ChurrOS CLI"
echo "===================================="
echo

echo "Project      : ChurrOS"
echo "Version      : $(cat "$VERSION_FILE")"
echo "Branch       : $(git branch --show-current)"
echo "Architecture : $(uname -m)"
echo "Kernel        : $(uname -r)"
echo

echo "Directories"
echo "-----------"

echo "Profile : archiso/"
echo "Output  : out/"
echo "Work    : work/"
echo "Scripts : scripts/"