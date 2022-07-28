#!/usr/bin/env bash

# exit when a command fails
set -e

create_envrc () {
    path=$1
    dir=$(dirname $path)
    mkdir -p "${dir}"
    touch    "${path}"
    echo "Created ${path}"
}

# Create sample direnv files
create_envrc "$HOME/projects/.envrc"
create_envrc "$HOME/projects/foo/.envrc"
create_envrc "$HOME/projects/bar/.envrc"
create_envrc "$HOME/projects/bar/baz/.envrc"
