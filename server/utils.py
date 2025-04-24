import random
import string
import datetime


def generateRandomString():
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(32))
    # return random.randint(1000000000, 9999999999)

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
    