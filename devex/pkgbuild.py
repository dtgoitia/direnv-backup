import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from textwrap import indent
from typing import Callable

from devex.exceptions import MissingEnvironmentVariable, UnexpectedScenario
from devex.git import (
    GitTagAlreadyExists,
    create_tag_in_current_commit,
    get_last_git_tag_version_in_master,
)
from devex.pyproject import get_pyproject_description, get_pyproject_version
from devex.semver import SemVer, SemVerBumpType
from tests.helpers.diff import diff_texts, join_lines

LOCAL_AUR_REPO_DIR_ENVVAR_NAME = "LOCAL_AUR_REPO_DIR"

logger = logging.getLogger(__name__)

RawPkgbuild = str


def assert_file_exists(path: Path) -> None:
    if path.exists():
        return

    raise FileNotFoundError(f"{path.absolute()} must exist")


def find_pkgbuild_path() -> Path:
    path = Path("PKGBUILD")
    assert_file_exists(path=path)
    return path


def find_aur_pkgbuild_path() -> Path:
    envvar_name = LOCAL_AUR_REPO_DIR_ENVVAR_NAME
    if envvar_name not in os.environ:
        raise MissingEnvironmentVariable(f"Please set {envvar_name}")

    raw = os.environ[envvar_name]
    local_aur_repo_dir = Path(raw).expanduser()

    if not local_aur_repo_dir.exists():
        raise ValueError(
            f"The {envvar_name} environment variable points to a path that does not"
            f" exist: {local_aur_repo_dir}"
        )

    if not local_aur_repo_dir.is_dir():
        raise ValueError(
            f"The {envvar_name} environment variable points to a path that is not a"
            f" directory: {local_aur_repo_dir}"
        )

    pkgbuild_path = local_aur_repo_dir / "PKGBUILD"

    return pkgbuild_path


def read_pkgver(raw: str) -> SemVer:
    pkgver_line = next(line for line in raw.split("\n") if "pkgver" in line)
    _, raw_version = pkgver_line.split("=")
    raw_mayor, raw_minor, raw_patch = raw_version.split(".")
    semver = SemVer(
        major=int(raw_mayor),
        minor=int(raw_minor),
        patch=int(raw_patch),
    )
    return semver


def bump_version(current: SemVer, bump_type: SemVerBumpType) -> SemVer:
    if bump_type == SemVerBumpType.major:
        return SemVer(
            major=current.major + 1,
            minor=0,
            patch=0,
        )

    if bump_type == SemVerBumpType.minor:
        return SemVer(
            major=current.major,
            minor=current.minor + 1,
            patch=0,
        )

    if bump_type == SemVerBumpType.patch:
        return SemVer(
            major=current.major,
            minor=current.minor,
            patch=current.patch + 1,
        )

    raise UnexpectedScenario("You should have never reached this point in code")


def _replace_line(
    *,
    file_content: str,
    starting_with: str,
    new_line: str,
) -> str:
    new_lines: list[str] = []

    for line in file_content.split("\n"):
        if line.startswith(starting_with):
            line = new_line
        new_lines.append(line)

    updated_pkgbuild = "\n".join(new_lines)
    return updated_pkgbuild


def _replace_value(
    *,
    pkgbuild: RawPkgbuild,
    starting_with: str,
    new_value: str,
) -> RawPkgbuild:
    new_lines: list[str] = []

    for line in pkgbuild.split("\n"):
        if line.startswith(starting_with):
            line = f"{starting_with}={new_value}"
        new_lines.append(line)

    updated_pkgbuild = "\n".join(new_lines)
    return updated_pkgbuild


def replace_version(old: RawPkgbuild, version: SemVer) -> RawPkgbuild:
    return _replace_value(pkgbuild=old, starting_with="pkgver", new_value=str(version))


def bump_pkgver(pkgbuild: RawPkgbuild, bump_type: SemVerBumpType) -> RawPkgbuild:
    current_version = read_pkgver(raw=pkgbuild)
    new_version = bump_version(current=current_version, bump_type=bump_type)

    updated_pkgbuild = replace_version(old=pkgbuild, version=new_version)
    return updated_pkgbuild


def read_current_pkgrel(pkgbuild: RawPkgbuild) -> int:
    for line in pkgbuild.splitlines():
        if not line.startswith("pkgrel"):
            continue
        _, raw_pkgrel = line.strip().split("=")
        pkgrel = int(raw_pkgrel)
        return pkgrel

    raise UnexpectedScenario("You should have never reached this point in code")


def replace_pkgrel(old: RawPkgbuild, pkgrel: int) -> RawPkgbuild:
    return _replace_value(pkgbuild=old, starting_with="pkgrel", new_value=str(pkgrel))


def _update_pkgrel(pkgbuild: RawPkgbuild, func: Callable[[int], int]) -> RawPkgbuild:
    current_pkgrel = read_current_pkgrel(pkgbuild=pkgbuild)
    new_pkgrel = func(current_pkgrel)

    updated_pkgbuild = replace_pkgrel(old=pkgbuild, pkgrel=new_pkgrel)
    return updated_pkgbuild


def reset_pkgrel(pkgbuild: RawPkgbuild) -> RawPkgbuild:
    def _set_to_one(_: int) -> int:
        return 1

    return _update_pkgrel(pkgbuild=pkgbuild, func=_set_to_one)


def bump_pkgrel(pkgbuild: RawPkgbuild) -> RawPkgbuild:
    def _increment_by_one(current: int) -> int:
        return current + 1

    return _update_pkgrel(pkgbuild=pkgbuild, func=_increment_by_one)


def read_pkgdesc(pkgbuild: RawPkgbuild) -> str:
    for line in pkgbuild.splitlines():
        if not line.startswith("pkgdesc"):
            continue
        _, raw_pkgdesc = line.strip().split("=")
        pkgdesc = raw_pkgdesc.strip("'\"")
        return pkgdesc

    raise UnexpectedScenario("You should have never reached this point in code")


def git_tag_and_pyproject_version_match(pyproject: str) -> bool:
    logger.info("Checking that git tag and pyproject.toml version match...")
    last_git_version = get_last_git_tag_version_in_master()
    logger.debug(f"  last git tag: {last_git_version}")
    pyproject_version = get_pyproject_version(pyproject=pyproject)
    logger.debug(f"  pyproject.toml version: {pyproject_version}")

    return last_git_version == pyproject_version


def pyproject_and_pkgbuild_match(pkgbuild: RawPkgbuild, pyproject: str) -> bool:
    logger.info("Checking that pyproject.toml and PKGBUILD match...")
    pyproject_version = get_pyproject_version(pyproject=pyproject)
    logger.debug(f"  pyproject.toml version: {pyproject_version}")
    pkgver = read_pkgver(raw=pkgbuild)
    logger.debug(f"  PKGBUILD pkgver: {pkgver}")

    versions_aligned = pyproject_version == pkgver

    pyproject_description = get_pyproject_description(pyproject=pyproject)
    logger.debug(f"  pyproject.toml description: {pyproject_description}")

    pkgdesc = read_pkgdesc(pkgbuild=pkgbuild)
    logger.debug(f"  PKGBUILD pkgdesc: {pkgdesc}")

    descriptions_aligned = pyproject_description == pkgdesc

    return versions_aligned and descriptions_aligned


def pkgbuild_and_local_aur_pkgbuild_match(
    pkgbuild: RawPkgbuild, aur_pkgbuild: RawPkgbuild
) -> bool:
    logger.info("Checking that PKGBUILD and local AUR repo PKGBUILD match...")
    diff = diff_texts(a=pkgbuild, b=aur_pkgbuild, minimal=True)
    aligned = set(diff) == set()
    if not aligned:
        full_diff = diff_texts(a=pkgbuild, b=aur_pkgbuild, minimal=False)
        logger.debug(indent(join_lines(full_diff), prefix="  "))
        logger.debug("when no diff was expected")
    else:
        logger.debug("  PKGBUILD and local AUR repo PKGBUILD are aligned")

    return aligned


class MakepkgError(Exception):
    ...


Checksum = str


def set_checksum(pkgbuild: RawPkgbuild, checksum: Checksum) -> RawPkgbuild:
    return _replace_line(
        file_content=pkgbuild,
        starting_with="sha256sums",
        new_line=checksum,
    )


def calculate_new_checksum(pkgbuild_path: Path) -> Checksum:
    assert_file_exists(pkgbuild_path)

    original_workding_dir = Path.cwd()

    # `makepkg` leaves empty folders behind. To avoid collisions, use `/tmp` to generate
    # the PKGBUILD checksum and then discard it
    tmp = Path("/tmp")
    random_dir_name = str(int(time.time() * 1000))
    random_dir = tmp / "direnv-backup" / random_dir_name
    random_dir.mkdir(parents=True, exist_ok=True)
    tmp_pkgbuild_path = random_dir / pkgbuild_path.name
    shutil.copy(src=str(pkgbuild_path), dst=tmp_pkgbuild_path)

    os.chdir(random_dir)

    cmd = "makepkg --force --geninteg"

    proc = subprocess.run(cmd.split(" "), capture_output=True)
    os.chdir(original_workding_dir)

    if proc.returncode:
        stderr = proc.stderr.decode("utf-8")
        raise MakepkgError(stderr)

    stdout = proc.stdout.decode("utf-8")

    new_checksum = stdout.strip()

    return new_checksum


def set_pkgver(pkgbuild: RawPkgbuild, version: SemVer) -> RawPkgbuild:
    updated_pkgbuild = _replace_value(
        pkgbuild=pkgbuild,
        starting_with="pkgver",
        new_value=str(version),
    )

    # Ensure that the pkgrel goes back to `1` after changing `pkgver`
    updated_pkgbuild = reset_pkgrel(pkgbuild=updated_pkgbuild)

    return updated_pkgbuild


def set_pkgdesc(pkgbuild: RawPkgbuild, description: str) -> RawPkgbuild:
    return _replace_value(
        pkgbuild=pkgbuild,
        starting_with="pkgdesc",
        new_value=f'"{description}"',
    )


def sync_git_tag(version: SemVer) -> None:
    """
    Assumptions:
        - tags are only created with this script - never manually
        - existing tags are correct
    """
    try:
        new_tag = str(version)
        create_tag_in_current_commit(new_tag=new_tag)
    except GitTagAlreadyExists:
        raise GitTagAlreadyExists(
            f"Git tag {new_tag!r} exists. This tag was not supposed to exist - manual"
            " intervention required"
        )


def update_pyproject_version(path: Path, version: SemVer) -> None:
    pyproject = path.read_text()

    updated_pyproject = _replace_line(
        file_content=pyproject,
        starting_with="version",
        new_line=f'version = "{version}"',
    )

    path.write_text(updated_pyproject)


def sync_pkg_metadata(
    pkgbuild_path: Path,
    pyproject_path: Path,
    action: None | SemVerBumpType = None,
) -> None:
    """
    Make sure that all metadata is aligned between git tags, pyproject.toml and PKGBUILD
    where metadata is: version, description, git tags, checksum, pkgrel

    Bottom line, do not manually update:
        - git tags
        - pyproject.toml version
        - PKGBUILD version

    """
    logger.info("Updating PKGBUILD...")

    pkgbuild = pkgbuild_path.read_text()
    pyproject = pyproject_path.read_text()

    logger.info("Propagating pyproject.toml description to PKGBUILD...")
    pyproject_description = get_pyproject_description(pyproject=pyproject)
    updated_pkgbuild = set_pkgdesc(pkgbuild=pkgbuild, description=pyproject_description)
    pkgdesc_changed = pkgbuild != updated_pkgbuild

    pkgver_changed = False

    pyproject_version = get_pyproject_version(pyproject=pyproject)
    if action:
        assert isinstance(action, SemVerBumpType)
        bump_type = action
        logger.info("Calculating new version from current pyproject.toml version...")
        new_version = bump_version(current=pyproject_version, bump_type=bump_type)
        logger.info(f"Bumping version: {pyproject_version} --> {new_version}")

        logger.info(f"Updating pyproject.toml version to {new_version} ...")
        update_pyproject_version(path=pyproject_path, version=new_version)
        logger.info(f"Updating PKGBUILD pkgver to {new_version} ...")
        updated_pkgbuild = set_pkgver(pkgbuild=updated_pkgbuild, version=new_version)

        logger.info(f"Creating git tag for version {new_version} ...")
        sync_git_tag(version=pyproject_version)

        pkgver_changed = True
    else:
        logger.info("Propagating pyproject.toml version to PKGBUILD...")
        updated_pkgbuild = set_pkgver(
            pkgbuild=updated_pkgbuild,
            version=pyproject_version,
        )

    # To recalculate the checksum, `makepkg` needs to read from a file. This means that
    # any changes you've done in memory need to be persisted to the file before
    # recalculating the checksum
    pkgbuild_path.write_text(updated_pkgbuild)

    logger.info("Calculating PKGBUILD checksum...")
    checksum = calculate_new_checksum(pkgbuild_path=pkgbuild_path)
    logger.debug(f"New checksum: {checksum}")
    pkgbuild = pkgbuild_path.read_text()
    updated_pkgbuild = set_checksum(pkgbuild=pkgbuild, checksum=checksum)

    checksum_changed = pkgbuild != updated_pkgbuild

    # If any change at all happens to the PKGBUILD
    pkgbuild_changed = pkgdesc_changed or pkgver_changed or checksum_changed

    # If any change happens to the packaged piece of software
    packaged_software_changed = pkgver_changed

    # Reminder: the PKGBUILD pkgver (aka, the version of the pacman package) must be the
    # same as the wrapped software version. If the sofware packages did not change, but
    # PKGBUILD does, the way to express this scenario is to change the PKGBUILD pkgrel.
    pkgrel_needs_to_increase = pkgbuild_changed and not packaged_software_changed
    if pkgrel_needs_to_increase:
        logger.debug("Increasing PKGBUILD pkgrel...")
        updated_pkgbuild = bump_pkgrel(pkgbuild=updated_pkgbuild)

    pkgbuild_path.write_text(updated_pkgbuild)
