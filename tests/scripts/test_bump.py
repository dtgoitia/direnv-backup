import os
from pathlib import Path
from textwrap import dedent, indent

import pytest

from scripts.update_pkgbuild import (
    LOCAL_AUR_REPO_DIR_ENVVAR_NAME,
    MissingEnvironmentVariable,
    SemVer,
    find_pkgbuild_path,
    update_pkgbuild_cmd,
)
from tests.helpers.diff import UnexpectedDiff, diff_texts, join_lines


def test_find_pkgbuild_path(fake_environment, tmp_path):
    dir: Path = tmp_path / "dir"
    dir.mkdir(parents=True, exist_ok=True)
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(dir.absolute())

    result = find_pkgbuild_path()

    assert result == dir / "PKGBUILD"


def test_find_pkgbuild_path_if_env_var_mising(fake_environment):
    assert LOCAL_AUR_REPO_DIR_ENVVAR_NAME not in os.environ

    with pytest.raises(MissingEnvironmentVariable) as e:
        find_pkgbuild_path()

    exc = e.value

    assert exc.args == ("Please set LOCAL_AUR_REPO_DIR",)


def test_find_pkgbuild_path_if_env_var_path_does_not_exist(fake_environment):
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = "non_existing_path"

    with pytest.raises(ValueError) as e:
        find_pkgbuild_path()

    exc = e.value

    assert exc.args == (
        "The LOCAL_AUR_REPO_DIR environment variable points to a path that does not "
        "exist: non_existing_path",
    )


def test_find_pkgbuild_path_if_env_var_path_is_a_file(fake_environment, tmp_path):
    path = tmp_path / "file"
    path.touch()
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(path.absolute())

    with pytest.raises(ValueError) as e:
        find_pkgbuild_path()

    exc = e.value

    assert exc.args == (
        "The LOCAL_AUR_REPO_DIR environment variable points to a path that is not a "
        f"directory: {path.absolute()}",
    )


def test_error_if_invalid_bump_type(fake_environment, tmp_path: Path):
    pkgbuild_path = tmp_path / "PKGBUILD"
    pkgbuild_path.touch()
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(pkgbuild_path.parent.absolute())

    exit_value = update_pkgbuild_cmd(args=["--bump", "foo"])
    assert exit_value == (
        "'foo' is not a valid bump type. Supported values: major, minor, patch"
    )


def test_semver_to_str():
    version = SemVer(major=1, minor=2, patch=3)
    assert str(version) == "1.2.3"


def test_bump_patch(fake_environment, tmp_path: Path):
    pkgbuild_path = tmp_path / "PKGBUILD"
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(pkgbuild_path.parent.absolute())

    before = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=0.0.2",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    pkgbuild_path.write_text(before)

    # Act
    assert update_pkgbuild_cmd(args=["--bump", "patch"]) is None

    # Assert
    after = pkgbuild_path.read_text()
    diff = diff_texts(a=before, b=after, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=before, b=after, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(diff_with_context, prefix="  ")}\n'
            )
        )


def test_bump_minor(fake_environment, tmp_path: Path):
    pkgbuild_path = tmp_path / "PKGBUILD"
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(pkgbuild_path.parent.absolute())

    before = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=0.1.0",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    pkgbuild_path.write_text(before)

    # Act
    assert update_pkgbuild_cmd(args=["--bump", "minor"]) is None

    # Assert
    after = pkgbuild_path.read_text()
    diff = diff_texts(a=before, b=after, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=before, b=after, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(diff_with_context, prefix="  ")}\n'
            )
        )


def test_bump_major(fake_environment, tmp_path: Path):
    pkgbuild_path = tmp_path / "PKGBUILD"
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(pkgbuild_path.parent.absolute())

    before = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=1.0.0",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    pkgbuild_path.write_text(before)

    # Act
    assert update_pkgbuild_cmd(args=["--bump", "major"]) is None

    # Assert
    after = pkgbuild_path.read_text()
    diff = diff_texts(a=before, b=after, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=before, b=after, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(diff_with_context, prefix="  ")}\n'
            )
        )


def test_bump_pkgrel(fake_environment, tmp_path: Path):
    pkgbuild_path = tmp_path / "PKGBUILD"
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(pkgbuild_path.parent.absolute())

    before = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    expected_diff = [
        "-pkgrel=2",
        "+pkgrel=3",
    ]

    pkgbuild_path.write_text(before)

    # Act
    assert update_pkgbuild_cmd(args=[]) is None

    # Assert
    after = pkgbuild_path.read_text()
    diff = diff_texts(a=before, b=after, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=before, b=after, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(diff_with_context, prefix="  ")}\n'
            )
        )
