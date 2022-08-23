#!/usr/bin/env bash

set -eo pipefail

docker-compose run \
    --no-TTY \
    --rm \
    direnv-backup-with-dev-deps \
        pytest -vv -s .

docker-compose run \
    --no-TTY \
    --rm \
    direnv-backup-only-pkgbuild \
        bash test_pkgbuild_file.sh
