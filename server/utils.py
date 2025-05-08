import random
import string
import datetime
import warnings
import functools

from bson import ObjectId  # only if you're checking type explicitly

def probability_generator(failure_rate: int = 50) -> bool:
    """
    Returns True with a probability equal to `failure_rate` percent.
    True means NOT failed.
    """
    if not 0 <= failure_rate <= 100:
        return False

    return random.randint(0, 99) >= failure_rate


def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def convert_str(obj):
    if isinstance(obj, str):
        return ObjectId(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def deprecated(reason: str, disable_execution: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__}() is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            if disable_execution:
                raise NotImplementedError(f"{func.__name__} is disabled: {reason}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def generateRandomString():
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(32))
    # return random.randint(1000000000, 9999999999)

def truncate_string(input_string: str, max_length: int = 20) -> str:
    if len(input_string) > max_length:
        return input_string[:max_length] + "..."
    return input_string

def updateData(dataToUpdate, updateQuery, unupdatableKeys):

    def set_nested(data, key, value):
        keys = key.split('.')
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value

    for key, value in updateQuery.items():
        if key in unupdatableKeys:
            raise ValueError(f'{key} is not updatable')
        firstKey = key.split('.')[0]
        if firstKey not in dataToUpdate.keys():
            raise ValueError(f'{key} is not a valid parameter')

        # if it has a dot, it means it is a nested object
        if '.' in key:
            set_nested(dataToUpdate, key, value)
        else:
            dataToUpdate[key] = value
    return dataToUpdate
    