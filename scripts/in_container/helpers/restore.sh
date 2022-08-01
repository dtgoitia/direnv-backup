#!/usr/bin/env bash

# exit when a command fails
set -e

python -m direnv_backup.cli.restore --verbose --config=container_config.json
