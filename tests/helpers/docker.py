from pathlib import Path


def inside_container() -> bool:
    return Path("/.dockerenv").exists()
