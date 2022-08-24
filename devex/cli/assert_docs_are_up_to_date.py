import argparse
import logging
import sys

from devex.docs import (
    find_readme_path,
    systemd_service_unit_is_up_to_date_in_readme,
    systemd_timer_unit_is_up_to_date_in_readme,
)
from devex.systemd import find_service_unit_path, find_timer_unit_path

logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    arguments = parser.parse_args(args)
    return arguments


def _assert() -> str | None:
    readme = find_readme_path().read_text()
    timer_unit = find_timer_unit_path().read_text()
    service_unit = find_service_unit_path().read_text()

    if not systemd_timer_unit_is_up_to_date_in_readme(readme=readme, unit=timer_unit):
        return "systemd timer unit file content and README docs do not match"

    if not systemd_service_unit_is_up_to_date_in_readme(
        readme=readme, unit=service_unit
    ):
        return "systemd service unit file content and README docs do not match"

    return None  # all good :)


def assert_docs_are_up_to_date(args: list[str] | None = None) -> str | None:
    arguments = parse_arguments(args=args)

    if arguments.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    try:
        mismatch_found = _assert()
        if not mismatch_found:
            logger.info("All files aligned :)")

        return mismatch_found

    except FileNotFoundError as error:
        return str(error)


if __name__ == "__main__":
    if exit_value := assert_docs_are_up_to_date():
        sys.exit(exit_value)
