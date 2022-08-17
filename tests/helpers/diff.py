import difflib


# TODO: move this to a non-test folder!
def diff_texts(a: str, b: str, minimal: bool = False) -> list[str]:
    if minimal is False:
        return list(difflib.Differ().compare(a.splitlines(), b.splitlines()))

    result: list[str] = []
    for line in difflib.unified_diff(a.splitlines(), b.splitlines()):
        if line.startswith(("---", "+++", "@@", " ")):
            continue
        result.append(line)

    return result


def join_lines(lines: list[str]) -> str:
    return "\n".join(lines)


class UnexpectedDiff(Exception):
    ...
