#!/usr/bin/env bash

# exit when a command fails
set -e

python -m src.cli.backup --verbose --config=container_config.json

echo "Backups folder:"
ls -al "${HOME}/backups"