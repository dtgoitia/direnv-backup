import json
import logging
import os
from dataclasses import Field, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

config_envvar_name = "DIRENV_BACKUP_CONFIG"

Email = str


@dataclass(frozen=True)
class Config:
    root_dir: Path  # top of the filesystem where to start scanning for direnv files
    backup_dir: Path  # folder where the backup will be stored
    #
    # patterns to ignore while scanning direnv files
    exclude: set[str] = set  # type: ignore
    #
    # If true, encrypt the tar file
    # this way you can start using it with Dropbox without encryption if you want to
    encrypt_backup: bool = True
    #
    # email used to select the public key used to encrypt the data.
    # required if `Config.encrypt == True`
    encryption_recipient: Email | None = None

    @property
    def tmp_dir(self) -> Path:
        return self.backup_dir / ".tmp"

    @classmethod
    @property
    def expected_json(self) -> str:
        fields = Config.__dataclass_fields__

        formatted_attributes: list[str] = []

        for field_name in sorted(fields.keys()):
            field: Field = fields[field_name]

            if str(field.type).startswith("<class "):
                field_type = field.type.__name__
            else:
                field_type = str(field.type)
            field_type = field_type.replace("set", "list")

            attribute = f'  "{field_name}": <{field_type}>,'

            formatted_attributes.append(attribute)

        return "\n".join(["{", *formatted_attributes, "}"])


class ConfigError(Exception):
    ...


def load_config_from_envvar(envvar_name: str) -> Config:
    raise NotImplementedError()
    if path_str := os.environ.get(envvar_name):
        logger.debug(f"{envvar_name!r} found set to {path_str}")
        path = Path(path_str)
        if not path.exists():
            logger.debug(f"{envvar_name!r} environment variable not set")
            raise ConfigError(f"{envvar_name!r} environment variable not set")
        config = read_config(path=path)
        return config
    else:
        raise ConfigError(f"{config_envvar_name!r} environment variable not set")


def try_loading_config_from_cli():
    raise NotImplementedError()


def load_config(cli_path: str) -> Config | None:
    try:
        return load_config_from_envvar(envvar_name=config_envvar_name)
    except ConfigError as env_error:
        logger.debug(env_error)

    if not cli_path:
        raise ConfigError("Config not found")

    try:
        return try_loading_config_from_cli()
    except ConfigError as env_error:
        logger.debug(env_error)

    return None


def validate_config(config: Config) -> None:
    if config.encrypt_backup and not config.encryption_recipient:
        raise ConfigError(
            "Encryption is enabled (by default), but no recipient is specified. Please,"
            " either specify a recipient in the config file, or explictly disable"
            " encryption in the config file."
        )
    else:
        logger.debug("Configuration validation: encryption disabled")


def read_config(path: Path) -> Config:
    """
    Assumption: path exists
    If paths contain curly braces, try to replace interpolate with env vars
    """

    raw_config = path.read_text()
    if not raw_config:
        raise ConfigError("Config file is empty")

    # interpolate environemnt variables
    # TODO
    interpolated_config = raw_config

    # parse from JSON string
    try:
        config_data = json.loads(interpolated_config)
    except json.JSONDecodeError:
        raise ConfigError("Provided config file contains invalid JSON")

    try:
        config = Config(
            root_dir=Path(config_data["root_dir"]),
            exclude=set(config_data["exclude"]),
            backup_dir=Path(config_data["backup_dir"]),
            encrypt_backup=config_data.get("encrypt_backup"),
            encryption_recipient=config_data.get("encryption_recipient"),
        )
    except KeyError as missing_field:
        raise ConfigError(
            f"Provided config is missing the {missing_field} field.\n"
            "The config should look like this:\n"
            f"{Config.expected_json}\n"
            "\n"
        )

    validate_config(config=config)

    return config
