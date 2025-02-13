def is_int(value: str) -> bool:
    """
    Check if a string is an integer
    Args:
        value (str): the putative integer

    Returns bool:
        true is if its an integer

    """
    result = False
    try:
        int(value)
        result = True
    except (ValueError, TypeError):
        pass

    return result


def is_float(value: str) -> bool:
    """
    Check if a string is an float
    Args:
        value (str): the putative float

    Returns bool:
        true is if its an integer

    """
    result = False
    try:
        float(value)
        result = True
    except (ValueError, TypeError):
        pass

    return result
