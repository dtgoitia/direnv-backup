import os
from pathlib import Path
from textwrap import dedent, indent
from unittest import mock

import pytest

from devex.cli.update_pkgbuild import update_pkgbuild_cmd
from devex.exceptions import MissingEnvironmentVariable
from devex.pkgbuild import (
    LOCAL_AUR_REPO_DIR_ENVVAR_NAME,
    SemVer,
    find_aur_pkgbuild_path,
)
from tests.helpers.diff import UnexpectedDiff, diff_texts, join_lines
from tests.helpers.environment import MockDevelopmentEnvironment


def test_find_aur_pkgbuild_path(fake_environment, tmp_path):
    dir: Path = tmp_path / "dir"
    dir.mkdir(parents=True, exist_ok=True)
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(dir.absolute())

    result = find_aur_pkgbuild_path()

    assert result == dir / "PKGBUILD"


def test_find_aur_pkgbuild_path_if_env_var_mising(fake_environment):
    assert LOCAL_AUR_REPO_DIR_ENVVAR_NAME not in os.environ

    with pytest.raises(MissingEnvironmentVariable) as e:
        find_aur_pkgbuild_path()

    exc = e.value

    assert exc.args == ("Please set LOCAL_AUR_REPO_DIR",)


def test_find_aur_pkgbuild_path_if_env_var_path_does_not_exist(fake_environment):
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = "non_existing_path"

    with pytest.raises(ValueError) as e:
        find_aur_pkgbuild_path()

    exc = e.value

    assert exc.args == (
        "The LOCAL_AUR_REPO_DIR environment variable points to a path that does not "
        "exist: non_existing_path",
    )


def test_find_aur_pkgbuild_path_if_env_var_path_is_a_file(fake_environment, tmp_path):
    path = tmp_path / "file"
    path.touch()
    os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(path.absolute())

    with pytest.raises(ValueError) as e:
        find_aur_pkgbuild_path()

    exc = e.value

    assert exc.args == (
        "The LOCAL_AUR_REPO_DIR environment variable points to a path that is not a "
        f"directory: {path.absolute()}",
    )


@mock.patch("devex.pkgbuild.sync_git_tag")
def test_error_if_invalid_bump_type(fake_environment, tmp_path: Path):
    with MockDevelopmentEnvironment(
        test_dir=tmp_path,
        pkgbuild="foo",
        pyproject="foo",
    ):
        exit_value = update_pkgbuild_cmd(args=["--bump", "foo"])
        assert exit_value == (
            "'foo' is not a valid bump type. Supported values: major, minor, patch"
        )


def test_semver_to_str():
    version = SemVer(major=1, minor=2, patch=3)
    assert str(version) == "1.2.3"


@mock.patch("devex.pkgbuild.sync_git_tag")
def test_bump_patch(fake_environment, tmp_path: Path):
    pkgbuild = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    pyproject = dedent(
        """
        version = "0.0.1"
        description = "Tool to backup/restore direnv files with optional encryption"
        """
    )

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=0.0.2",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    with MockDevelopmentEnvironment(
        test_dir=tmp_path,
        pkgbuild=pkgbuild,
        pyproject=pyproject,
    ) as mock_env:
        assert update_pkgbuild_cmd(args=["--bump", "patch"]) is None

        updated_pkgbuild = mock_env.pkgbuild

    # Assert
    diff = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(join_lines(diff_with_context), prefix="  ")}\n'
            )
        )


@mock.patch("devex.pkgbuild.sync_git_tag")
def test_bump_minor(fake_environment, tmp_path: Path):
    pkgbuild = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    pyproject = dedent(
        """
        version = "0.0.1"
        description = "Tool to backup/restore direnv files with optional encryption"
        """
    )

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=0.1.0",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    with MockDevelopmentEnvironment(
        test_dir=tmp_path,
        pkgbuild=pkgbuild,
        pyproject=pyproject,
    ) as mock_env:
        assert update_pkgbuild_cmd(args=["--bump", "minor"]) is None

        updated_pkgbuild = mock_env.pkgbuild

    os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
    # Assert
    diff = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=False)
        breakpoint()
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(join_lines(diff_with_context), prefix="  ")}\n'
            )
        )


@mock.patch("devex.pkgbuild.sync_git_tag")
def test_bump_major(fake_environment, tmp_path: Path):
    pkgbuild = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    pyproject = dedent(
        """
        version = "0.0.1"
        description = "Tool to backup/restore direnv files with optional encryption"
        """
    )

    expected_diff = [
        "-pkgver=0.0.1",
        "+pkgver=1.0.0",
        "-pkgrel=2",
        "+pkgrel=1",
    ]

    with MockDevelopmentEnvironment(
        test_dir=tmp_path,
        pkgbuild=pkgbuild,
        pyproject=pyproject,
    ) as mock_env:
        assert update_pkgbuild_cmd(args=["--bump", "major"]) is None

        updated_pkgbuild = mock_env.pkgbuild

    # Assert
    diff = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(join_lines(diff_with_context), prefix="  ")}\n'
            )
        )


@pytest.mark.skip(reason="need more thinking: how to test pkgrel update effectively")
def test_bump_pkgrel(fake_environment, tmp_path: Path):
    pkgbuild = dedent(
        """
        _name=my-super-package
        pkgname="${_name}-git"
        pkgver=0.0.1
        pkgrel=2
        pkgdesc="Tool to backup/restore direnv files with optional encryption"
        source=("${_name}-${pkgver}::git+https://github.com/dtgoitia/${_name}.git")
        """
    ).strip()

    pyproject = dedent(
        """
        version = "0.0.1"
        description = "Tool to backup/restore direnv files"
        """
    )

    expected_diff = [
        "-pkgrel=2",
        "+pkgrel=3",
        '-pkgdesc="Tool to backup/restore direnv files with optional encryption"',
        '+pkgdesc="Tool to backup/restore direnv files"',
    ]

    with MockDevelopmentEnvironment(
        test_dir=tmp_path,
        pkgbuild=pkgbuild,
        pyproject=pyproject,
    ) as mock_env:
        assert update_pkgbuild_cmd(args=[]) is None

        updated_pkgbuild = mock_env.pkgbuild

    # Assert
    diff = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=True)
    if sorted(diff) != sorted(expected_diff):
        diff_with_context = diff_texts(a=pkgbuild, b=updated_pkgbuild, minimal=False)
        raise UnexpectedDiff(
            (
                "\n"
                f"Expected this diff\n"
                "\n"
                f'{indent(join_lines(expected_diff), prefix="  ")}\n'
                "\n"
                "but got this instead:\n"
                "\n"
                f'{indent(join_lines(diff_with_context), prefix="  ")}\n'
            )
        )
