# direnv-backup

Tool to backup/restore direnv files.

Purely written in Python.

## Development

### Build a wheel

```shell
python -m build --wheel
```

You should be able to run this outside a container.

## Publish `PKGBUILD`

1. Clone AUR repo locally - this only needs to be done the first time:

  ```bash
  # in ~/projects
  mkdir aur
  cd aur
  git clone ssh://aur@aur.archlinux.org/direnv-backup.git
  cd direnv-backup
  ```

2. In the current repo, amend `PKGBUILD` as needed:

  ```bash
  # TODO: script to bump version
  bash scripts/generate_pkgbuild.sh
  ```

3. Test `PKGBUILD` in container:

  ```bash
  docker-compose run --rm direnv-backup-only-pkgbuild \
    bash test_pkgbuild_file.sh
  ```

4. Push `PKGBUILD` to local AUR repo:

  ```bash
  python scripts/push_pkgbuild_to_local_aur_repo.py
  ```

5. Commit in local AUR repo and push to remote AUR:

  ```bash
  $ pwd
  ~projects/aur/direnv-backup

  $ git commit -m <Message here>   # "Bump version to 1.2.3"
  $ git push
  ```
