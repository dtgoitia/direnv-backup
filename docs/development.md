## Development

## Install

```shell
python -m venv .venv
. .venv/bin/activate
make install-dev-tools install_development_dependencies
```

### Build a wheel

With development dependencies installed:

```
python -m build --wheel
```

You should be able to run this outside a container.

### Test service unit

1. Symlink the service unit to the user folder for testing:

    ```bash
    ln -s \
      "$(pwd)/systemd/direnv-backup.service" \
      ~/.config/systemd/user/direnv-backup.service
    ```

2. Make sure systemd can find the service unit:

    ```bash
    $ systemctl --user status direnv-backup
    ○ direnv-backup.service - Run direnv-backup with user config.
        Loaded: loaded (~/.config/systemd/user/direnv-backup.service; linked; preset: enabled)
        Active: inactive (dead)
    ```

3. Run the service unit once:

    ```bash
    $ systemctl --user start direnv-backup
    ○ direnv-backup.service - Run direnv-backup with user config.
        Loaded: loaded (~/.config/systemd/user/direnv-backup.service; linked; preset: enabled)
        Active: inactive (dead)
    ```

4. Check logs:

    ```bash
    $ systemctl --user status direnv-backup
    ```

### Publish `PKGBUILD`

1. Clone AUR repo locally - this only needs to be done the first time:

    ```bash
    # in ~/projects
    mkdir aur
    cd aur
    git clone ssh://aur@aur.archlinux.org/direnv-backup-git.git
    cd direnv-backup-git
    ```

2. In the current repo, amend `PKGBUILD` as needed:

    ```bash
    python -m devex.cli.update_pkgbuild --bump patch   # patch, minor, major
    ```

    This command will:

    - sync `pyroject.toml` metadata and `PKGBUILD` metadata
    - push local `PKGBUILD` to local AUR repo

    Make sure to commit current changes.

3. Add git tag to current commit.

4. Ensure that the above sync worked fine:

    ```bash
    python -m devex.cli.assert_pkgbuild_status
    ```

5. Test `PKGBUILD` in container:

    ```bash
    docker-compose run --rm direnv-backup-only-pkgbuild \
      bash test_pkgbuild_file.sh
    ```

6. Commit in local AUR repo and push to remote AUR:

    ```bash
    $ pwd
    ~/projects/aur/direnv-backup

    $ git commit -m <Message here>   # "Bump version to 1.2.3"
    $ git push
    ```
