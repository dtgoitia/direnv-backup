#!/usr/bin/env bash

# exit when a command fails
set -e

python -m src.cli.restore --verbose --config=container_config.json
