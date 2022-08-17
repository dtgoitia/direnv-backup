from __future__ import annotations

import enum
from dataclasses import dataclass


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_str(cls, raw: str) -> SemVer:
        # TODO: add test

        try:
            raw_major, raw_minor, raw_patch = raw.strip().split(".")
            major = int(raw_major)
            minor = int(raw_minor)
            patch = int(raw_patch)
        except ValueError:
            raise ValueError(f"{raw!r} is not a valid semantic version")

        return cls(major=major, minor=minor, patch=patch)


class SemVerBumpType(enum.Enum):
    major = 0
    minor = 1
    patch = 2
