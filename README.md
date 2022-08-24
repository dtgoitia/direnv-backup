# direnv-backup

Tool to backup/restore direnv files.

Purely written in Python.

## Rationale

If you use [direnv][1] (*), you have probably built up a few dozens of carefully crafted `.envrc` files over time that now quietly live somewhere scattered across your projects directory making your developer experience much nicer almost for free.

Wouldn't it be great if you could back up all those precious files?

[direnv-backup][2] is a simple CLI utility to backup/restore your direnv files. It is designed to be [config driven](#configuration). Just drop your dotfiles, install direnv-backup and you are ready to go.

Optionally, you can encrypt your backups using [GPG][3]. I strongly suggest you to enable encryption.

\*: if you don't use it yet, you should definitely try it.

## Installation

* Install with your AUR package manager:

  ```bas
  $ aurman -S direnv-backup
  ```

* Create mandatory config file, see [how to](#configuration).

* Enable automatic backups:

  ```bash
  $ systemd --user enable direnv-backup.timer
  ```

## Configuration

`direnv-backup` is driven by configuration. Create a file at `~/.config/direnv-backup/config.json` and add the following:

```json
{
  "root_dir": "/home/janedoe/projects",
  "exclude": [
    "__pycache_ _",
    ".git",
    ".venv",
    "node_modules"
  ],
  "backup_dir": "/home/janedoe/my-direnv-backups",
  "encrypt_backup": true,
  "encryption_recipient": "john@doe.com"
}
```

where:

  * `root_dir` (string): path where the backup command looks for direnv files to back them up, and the reference the restore command uses to know where to put the direnv files back.

  * `exclude` (string list): list of directory names to skip during the `root_dir` traversal. Suggestion: populate this list with big directories that do not contain direnv files to considerably **reduce the execution time**.

  * `backup_dir` (string): path where the backups will be stored.

  * `encrypt_backup` (boolean, _optional_): if `true` the backups will be encrypted. Requires `encryption_recipient`.

  * `encryption_recipient` (string, _optional_): email set in the GPG key pair that will be used to encrypt (on back up) and decrypt (on restore) the backups.

### A backup frequency

To tune how frequently automatic backups are created, create a user service unit:

```bash
# ~/.config/systemd/user/direnv-backup.service
[Unit]
Description=back up with direnv-backup and user config

[Service]
Type=simple
ExecStart=direnv-backup --config=%h/.config/direnv-backup/config.json

[Install]
WantedBy=default.target
```

and a user timer unit:

```bash
# ~/.config/systemd/user/direnv-backup.timer
[Unit]
Description=schedule to backup direnv files every hour
# Allow manual starts
RefuseManualStart=false
# Allow manual stops
RefuseManualStop=false

[Timer]
# Do not execute job if it missed a run due to machine being off
Persistent=false
# Run 3600 seconds after boot for the first time
OnBootSec=3600
# Run every 1 hour thereafter
OnUnitActiveSec=3600
# File describing job to execute
Unit=direnv-backup.service

[Install]
WantedBy=timers.target
```

and, in the new file, set `OnUnitActiveSec` to the amount of seconds you want between each backup:

```diff
- OnUnitActiveSec=3600
+ OnUnitActiveSec=1234567
```

You might need to ask systemd to reload units after this change.

## Commands

**IMPORTANT**: a working [configuration](#configuration) must be in place.

* Create a new backup:

  ```shell
  direnv-backup --config=/path/to/config.json
  ```

* Restore the last backup:

  ```shell
  direnv-restore --config=/path/to/config.json
  ```

## Development

See [development docs](./docs/development.md).

<!-- External references -->

[1]: https://direnv.net/ "direnv official site"
[2]: https://aur.archlinux.org/packages/direnv-backup "AUR direnv-backup"
[3]: https://www.gnupg.org/ "GnuPG official site"
