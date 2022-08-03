import logging
import subprocess
import tarfile
from pathlib import Path

logger = logging.getLogger(__name__)


def archive_dir(dir: Path, base: Path, output: Path) -> Path:
    """
    Build an archive that includes the `dir` directory and every file inside. Every file
    will be added to the archive with its relative path from the `base` path:

    dir:  /foo
    base: /foo/bar

            original path          in archive
    file 1: /foo/bar/baz/kk.1      baz/kk.1
    file 2: /foo/bar/baz/kk.2      baz/kk.2
    file 3: /foo/bar/kk.3          kk.3
    file 4: /foo/kk.4              (not included, it's outside `dir`)
    """

    assert output.suffixes == [".tar"]

    with tarfile.open(output, "w") as tar:
        files = (path for path in dir.rglob("*") if path.is_file())
        for file_path in files:
            file_path_in_archive = file_path.relative_to(base)
            logger.debug(f"Adding file to archive as {file_path_in_archive}")
            tar.add(file_path, arcname=file_path_in_archive)

    return output


def extract(path: Path, extract_to_dir: Path) -> None:
    # tar --extract --verbose -f $decrypted_file --directory $test_dir
    cmd = [
        "tar",
        "--extract",
        "--verbose",
        "-f",
        str(path),
        "--directory",
        str(extract_to_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")
    stderr = proc.stderr.decode("utf-8")

    something_went_wrong = stdout or stderr

    if something_went_wrong:
        # TODO: handle this with the corresponding exceptions - if key missing, etc.
        print(f"{stdout=}")
        print(f"{stderr=}")

    logger.debug(f"Extraction output: {extract_to_dir}")
