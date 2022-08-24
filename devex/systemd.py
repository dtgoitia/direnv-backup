from pathlib import Path


def find_service_unit_path() -> Path:
    path = Path("systemd/direnv-backup.service")
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} must exist")

    return path


def find_timer_unit_path() -> Path:
    path = Path("systemd/direnv-backup.timer")
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} must exist")

    return path
