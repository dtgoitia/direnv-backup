import logging
import subprocess

from devex.semver import SemVer

logger = logging.getLogger(__name__)

GitTag = str


class NoGitTagsFound(Exception):
    ...


class InvalidVersionInGitTag(Exception):
    ...


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
