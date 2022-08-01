from pathlib import Path

from direnv_backup.config import Config


def test_encryption_is_enabled_by_default():
    any_path = Path("foo")
    config = Config(root_dir=any_path, backup_dir=any_path)
    assert config.encrypt_backup is True
