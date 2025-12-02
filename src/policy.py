import json
from pathlib import Path
from typing import NamedTuple


class Policy(NamedTuple):
    path: Path
    content: dict

    @staticmethod
    def get_new_policy(path: Path) -> "Policy":
        with open(path, encoding="utf-8") as file:
            content = json.load(file)
            path = Path(*path.parts[1:])
        return Policy(path, content)
