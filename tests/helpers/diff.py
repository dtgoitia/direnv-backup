import difflib


def diff_texts(a: str, b: str, minimal=False) -> list[str]:
    if minimal is False:
        return "\n".join(difflib.Differ().compare(a.splitlines(), b.splitlines()))

    result: list[str] = []
    for line in difflib.unified_diff(a.splitlines(), b.splitlines()):
        if line.startswith(("---", "+++", "@@", " ")):
            continue
        result.append(line)

    return result


def join_lines(l: list[str]) -> str:
    return "\n".join(l)


class UnexpectedDiff(Exception):
    ...
