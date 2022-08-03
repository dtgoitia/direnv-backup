from pathlib import Path

from direnv_backup.cli.backup import main


def test_exit_if_config_not_specified():
    assert main([]) == "Please specify a config (see --help)"


def test_exit_if_config_file_does_not_exist():
    assert main(["--config", "nonexistent_file.json"]) == (
        "Provided path for the config file does not exit: nonexistent_file.json"
    )


def test_exit_if_config_file_is_empty(tmp_path: Path) -> None:
    empty_file_path = tmp_path / "empty_file.json"
    empty_file_path.touch()
    assert empty_file_path.exists()
    assert empty_file_path.read_text() == ""

    assert main(["--config", str(empty_file_path)]) == ("Config file is empty")


def test_exit_if_config_file_is_not_valid_json(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid_json.json"
    invalid_json.write_text("{1234")

    assert main(["--config", str(invalid_json)]) == (
        "Provided config file contains invalid JSON"
    )


def test_exit_if_config_is_not_valid(tmp_path: Path) -> None:
    valid_json_but_invalid_config = tmp_path / "valid_json_but_invalid_config.json"
    valid_json_but_invalid_config.write_text('{"a":1}')

    assert main(["--config", str(valid_json_but_invalid_config)]) == (
        "Provided config is missing the 'root_dir' field.\n"
        "The config should look like this:\n"
        "{\n"
        '  "backup_dir": <Path>,\n'
        '  "encrypt_backup": <bool>,\n'
        '  "encryption_recipient": <str | None>,\n'
        '  "exclude": <list[str]>,\n'
        '  "root_dir": <Path>,\n'
        "}\n"
        "\n"
    )
