from pathlib import Path

from devex.semver import SemVer


class InvalidVersionInPyProjectToml(Exception):
    ...


def find_pyproject_path() -> Path:
    path = Path("pyproject.toml")
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} must exist")

    return path


def get_pyproject_version(pyproject: str) -> SemVer:
    line = next(line for line in pyproject.split("\n") if "version" in line)

    _, raw_version = line.split("=")

    raw_version = raw_version.strip(" '\"")
    try:
        version = SemVer.from_str(raw_version)
    except ValueError as error:
        raise InvalidVersionInPyProjectToml(
            f"pyproject.toml version {raw_version!r} is not valid: {error}"
        ) from None

    return version


def get_pyproject_description(pyproject: str) -> str:
    lines = next(line for line in pyproject.split("\n") if "description" in line)

    _, raw_description = lines.split("=")

    description = raw_description.strip(" '\"")
    return description
