from collections.abc import Generator
from functools import cached_property
from pathlib import Path
from typing import Optional

from policy import Policy


class Snapshot:
    def __init__(self, directory: str):
        self.directory = directory
        self._file_paths = sorted([path for path in Path(self.directory).rglob("*") if path.is_file()])
        self._policies_iterator: Optional[Generator] = None
        pass

    @property
    def policies(self) -> Generator[Policy]:
        if self._policies_iterator is None:
            self._policies_iterator = (Policy.get_new_policy(file) for file in self._file_paths)
        return self._policies_iterator

    @cached_property
    def file_paths(self) -> list[Path]:
        return [Path(*path.parts[1:]) for path in self._file_paths]
