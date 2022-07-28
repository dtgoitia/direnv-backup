#!/usr/bin/env bash

# exit when a command fails
set -e

base="scripts/in_container/helpers"

bash $base/show_current_state.sh

# Set up container
bash $base/populate_container_with_sample_direnv_files.sh
bash $base/add_gpg_key.sh

bash $base/show_current_state.sh

bash $base/backup.sh

bash $base/show_current_state.sh

bash $base/delete_all_direnv_files.sh

bash $base/show_current_state.sh

bash $base/restore.sh

bash $base/show_current_state.sh