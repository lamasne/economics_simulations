import meta.globals as globals
import numpy as np


def get_key_from_value(d, val):
    keys_list = [k for k, v in d.items() if v == val]
    if len(keys_list) == 0:
        raise Exception("Value not found in dictionnary")
    else:
        key = keys_list[0]
        if not all(key_test == key for key_test in keys_list):
            raise Exception("Value associated with different keys")
    return key


# def is_iterable(object):
#     try:
#         iter(object)
#         if len(object) > 0:
#             return True
#     except TypeError:
#         pass
#     return False


def is_a_compound(object):
    if (
        isinstance(object, list)
        or isinstance(object, tuple)
        or isinstance(object, dict)
        or isinstance(object, np.ndarray)
    ):
        return True
    else:
        return False


def get_values_from_compound(object):
    return list(object.values()) if isinstance(object, dict) else object
