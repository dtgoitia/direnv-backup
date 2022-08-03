from dataclasses import dataclass
from pathlib import Path


@dataclass
class SampleEnvrc:
    path: Path  # relative path
    content: str


SAMPLE_ENVRC_FILES = [
    SampleEnvrc(path=Path(".envrc"), content="top level"),
    SampleEnvrc(path=Path("foo/.envrc"), content="foo"),
    SampleEnvrc(path=Path("bar/.envrc"), content="bar"),
]


def create_envrc(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def create_sample_envrc_files(root_dir: Path) -> None:
    for envrc in SAMPLE_ENVRC_FILES:
        create_envrc(path=root_dir / envrc.path, content=envrc.content)


def get_direnv_files(lookup_dir: Path) -> set[Path]:
    return {path for path in lookup_dir.glob("*.envrc")}


def assert_file(path: Path, content: str) -> None:
    assert path.exists()
    assert path.read_text() == content


def assert_all_envrc_files_are_in_place(root_dir: Path) -> None:
    for envrc in SAMPLE_ENVRC_FILES:
        assert_file(path=root_dir / envrc.path, content=envrc.content)


def assert_no_envrc_exists(root_dir: Path) -> None:
    for envrc in SAMPLE_ENVRC_FILES:
        assert (root_dir / envrc.path).exists() is False


def delete_envrc_files(root_dir: Path) -> None:
    for envrc in SAMPLE_ENVRC_FILES:
        path = root_dir / envrc.path

        if not path.exists():
            continue

        path.unlink()
        # This will leave empty directories - this doesn't seem a problem now
