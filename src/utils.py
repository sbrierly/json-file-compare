from collections.abc import Iterator


def sort_dict_in_place(input: dict) -> dict:
    for value in input.values():
        if isinstance(value, dict):
            sort_dict_in_place(value)
        elif isinstance(value, list):
            sort_list_in_place(value)

    sorted_items = sorted(input.items())
    input.clear()
    input.update(sorted_items)
    return input


def sort_list_in_place(input: list) -> list:
    for item in input:
        if isinstance(item, dict):
            sort_dict_in_place(item)
        elif isinstance(item, list):
            sort_list_in_place(item)

    input.sort(key=lambda x: (isinstance(x, (dict, list)), x) if not isinstance(x, (dict, list)) else (True, id(x)))
    return input


class Committable(Iterator):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self._buffer = []
        self._exhausted = False
        self._current = None

    def __next__(self):
        """Returns the next item for review without consuming it."""
        if not self._buffer and not self._exhausted:
            try:
                self._buffer.append(next(self.iterator))
            except StopIteration:
                self._exhausted = True
                raise StopIteration("No more items")

        if self._buffer:
            self._current = self._buffer[0]
            return self._current
        raise StopIteration("No more items")

    def commit(self):
        """Fully consume/commit the current item."""
        if self._buffer:
            return self._buffer.pop(0)
        raise StopIteration("No item to commit")

    def __iter__(self):
        return self


class Peekable(Iterator):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self._buffer = []
        self._exhausted = False

    def peek(self):
        if not self._buffer and not self._exhausted:
            try:
                self._buffer.append(next(self.iterator))
            except StopIteration:
                self._exhausted = True
                raise StopIteration("No more items to peek")

        if self._buffer:
            return self._buffer[0]
        raise StopIteration("No more items to peek")

    def __next__(self):
        if self._buffer:
            return self._buffer.pop(0)

        if self._exhausted:
            raise StopIteration

        value = next(self.iterator)
        return value
