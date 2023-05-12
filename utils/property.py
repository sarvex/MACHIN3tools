def step_list(current, list, step, loop=True):
    item_idx = list.index(current)

    step_idx = item_idx + step

    if (
        step_idx >= len(list)
        and loop
        or step_idx < len(list)
        and step_idx < 0
        and not loop
    ):
        step_idx = 0
    elif step_idx >= len(list) or step_idx < 0:
        step_idx = len(list) - 1

    return list[step_idx]


def step_enum(current, items, step, loop=True):
    item_list = [item[0] for item in items]
    item_idx = item_list.index(current)

    step_idx = item_idx + step

    if (
        step_idx >= len(item_list)
        and loop
        or step_idx < len(item_list)
        and step_idx < 0
        and not loop
    ):
        step_idx = 0
    elif step_idx >= len(item_list) or step_idx < 0:
        step_idx = len(item_list) - 1
    return item_list[step_idx]


def step_collection(object, currentitem, itemsname, indexname, step):
    item_list = list(getattr(object, itemsname))
    item_idx = item_list.index(currentitem)

    step_idx = item_idx + step

    if step_idx >= len(item_list):
        # step_idx = 0
        step_idx = len(item_list) - 1
    elif step_idx < 0:
        # step_idx = len(item_list) - 1
        step_idx = 0

    setattr(object, indexname, step_idx)

    return getattr(object, itemsname)[step_idx]
