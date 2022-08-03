import subprocess
from pathlib import Path

import pytest

from tests.helpers.docker import inside_container
from tests.helpers.environment import command_exists


def build_wheel(output_dir: Path) -> Path:
    cmd = f"python -m build --wheel --outdir {output_dir}"
    process = subprocess.run(cmd.split(" "), capture_output=True)
    stdout = process.stdout.decode("utf-8")
    stderr = process.stderr.decode("utf-8")

    if stderr:
        print()
        print(f"{stdout=}")
        print(f"{stderr=}")
        error_last_line = stderr.strip().split("\n")[-1]
        raise Exception(f"{error_last_line}\n\n{stderr}")

    last_stdout_line = stdout.strip().split("\n")[-1]

    assert "Successfully built " in last_stdout_line
    _, wheel_file_name = last_stdout_line.rsplit(" ", maxsplit=1)

    wheel_path = output_dir / wheel_file_name
    return wheel_path


@pytest.mark.skipif(not inside_container(), reason="must run in container")
def test_build_and_install_wheel(tmp_path: Path) -> None:
    commands = ["direnv-backup", "direnv-restore"]

    # ----------------------------------------------------------------------------------
    #  build wheel
    # ----------------------------------------------------------------------------------

    # Setup
    output_dir = tmp_path / "dist"

    # Act
    wheel_path = build_wheel(output_dir=output_dir)

    # Assert: there is a single wheel package in the output directory
    wheels = list(output_dir.glob("*.whl"))
    assert len(wheels) == 1

    # ----------------------------------------------------------------------------------
    #  install wheel
    # ----------------------------------------------------------------------------------

    # Setup: ensure command does not exist
    for undesired_command in commands:
        assert not command_exists(command=undesired_command)

    # Act: install wheel using pip
    cmd = f"pip install {wheel_path.absolute()}"
    subprocess.run(cmd.split(" "), capture_output=True)

    # Assert
    for desired_command in commands:
        assert command_exists(command=desired_command)
