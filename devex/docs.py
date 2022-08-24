import logging
from pathlib import Path
from textwrap import dedent

logger = logging.getLogger(__name__)


def find_readme_path() -> Path:
    path = Path("README.md")
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} must exist")

    return path


def _find_markdown_codeblock_in(*, _document: str, starting_with: str) -> str | None:
    _end_of_codeblock = "```"

    block_lines: list[str] = []

    code_block_found = False
    for line in _document.splitlines():
        line_is_end_of_block = line == _end_of_codeblock

        if code_block_found and not line_is_end_of_block:
            block_lines.append(line)

        elif code_block_found and line_is_end_of_block:
            code_block_found = False

        elif line == starting_with:
            code_block_found = True

        else:
            continue  # skip line

    if not block_lines:
        return None

    return "\n".join(block_lines)


def systemd_timer_unit_is_up_to_date_in_readme(readme: str, unit: str) -> bool:
    block_top = "# ~/.config/systemd/user/direnv-backup.timer"
    if block := _find_markdown_codeblock_in(_document=readme, starting_with=block_top):
        return dedent(block).strip() == unit.strip()

    logger.debug("systemd timer unit not found in README")
    return False


def systemd_service_unit_is_up_to_date_in_readme(readme: str, unit: str) -> bool:
    block_top = "# ~/.config/systemd/user/direnv-backup.service"
    if block := _find_markdown_codeblock_in(_document=readme, starting_with=block_top):
        return dedent(block).strip() == unit.strip()

    logger.debug("systemd service unit not found in README")
    return False
