import json
from pathlib import Path
from typing import NamedTuple

from utils import sort_dict_in_place


class Policy(NamedTuple):
    path: Path
    content: dict

    @staticmethod
    def get_new_policy(path: Path) -> "Policy":
        with open(path, encoding="utf-8") as file:
            content = sort_dict_in_place(json.load(file))
            path = Path(*path.parts[1:])
        return Policy(path, content)
