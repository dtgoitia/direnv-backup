from pathlib import Path

from direnv_backup.config import Config


def test_encryption_is_enabled_by_default():
    any_path = Path("foo")
    config = Config(root_dir=any_path, backup_dir=any_path)
    assert config.encrypt_backup is True


def test_get_config_template_json():
    assert Config.expected_json == (  # type: ignore
        "{\n"
        '  "backup_dir": <Path>,\n'
        '  "encrypt_backup": <bool>,\n'
        '  "encryption_recipient": <str | None>,\n'
        '  "exclude": <list[str]>,\n'
        '  "root_dir": <Path>,\n'
        "}"
    )
