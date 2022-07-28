#!/usr/bin/env bash

# exit when a command fails
set -e

echo ""
echo "Deleting all .envrc files:"
echo ""
find $HOME | grep ".envrc" | xargs rm
echo ""