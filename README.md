# direnv-backup

Tool to backup/restore direnv files.

Purely written in Python.

## Development

### Build a wheel

```shell
python -m build --wheel
```

You should be able to run this outside a container.

### Semi maManually test PKGBUILD within container

1. Remove `PKGBUILD_files/TO_DELETE` directory if exists:

  ```shell
  rm -rf PKGBUILD_files/TO_DELETE
  ```

2. Start a clean container and shell into it:

  ```shell
  docker-compose down
  make rebuild_container_image shell_in_container
  ```

3. Create the pacman package:

  ```shell
  bash build.sh
  ```

  You will need to type the password of the user (see `Dockerfile`) and press `Y` to temporarily install dependencies for the buld.

4. Check that the `direnvbackup` command is not available.

  ```shell
  $ direnvbackup --help
  Unknown command: direnvbackup
  ```

5. Install the package

  ```shell
  bash install.sh
  ```

6. Check that the `direnvbackup` command is available.

  ```shell
  direnvbackup --help
  # no errors
  ```
