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
