import logging
import subprocess

from devex.semver import SemVer

logger = logging.getLogger(__name__)

GitTag = str


class NoGitTagsFound(Exception):
    ...


class InvalidVersionInGitTag(Exception):
    ...


class GitTagAlreadyExists(Exception):
    ...


def create_tag_in_current_commit(new_tag: GitTag) -> None:
    cmd = f"git tag {new_tag}"
    logger.debug(f"Executing {cmd!r} ...")
    proc = subprocess.run(cmd.split(" "), capture_output=True)
    stderr = proc.stderr.decode("utf-8")

    if proc.returncode != 0:
        if f"fatal: tag '{new_tag}' already exists" in stderr:
            logger.debug(f"STDERR: {stderr}")
            raise GitTagAlreadyExists(new_tag)

    return None  # all good


def get_last_tag_in_master() -> GitTag:
    cmd = "git describe --tags --abbrev=0".split(" ")
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")
    stderr = proc.stderr.decode("utf-8")

    if stderr:
        raise NoGitTagsFound(stderr)

    tag = stdout.strip()

    assert tag

    return tag


def get_last_git_tag_version_in_master() -> SemVer:
    last_tag = get_last_tag_in_master()

    try:
        last_git_version = SemVer.from_str(last_tag)
    except ValueError as error:
        raise InvalidVersionInGitTag(
            f"Last git tag {last_tag!r} is not valid: {error}"
        ) from None

    return last_git_version
