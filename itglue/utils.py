from copy import deepcopy
from typing import Any, Mapping, MutableMapping


def normalize_ids(obj: MutableMapping[str, Any], recurse=False):
    """
    Scans a dict for keys ending in '_id' with non-null values and converts the
    corresponding values to strings. Returns a new dict using deepcopy.
    """

    def modify_dict(obj: MutableMapping[str, Any], recurse):
        for key, val in obj.items():
            if key.endswith('_id') and val is not None:
                obj[key] = str(val)
            elif recurse and isinstance(val, MutableMapping):
                modify_dict(val, recurse)
        return obj

    return modify_dict(deepcopy(obj), recurse)


def prepare_tag_traits_for_upload(traits: Mapping):
    newtraits = {}

    for key, val in traits.items():
        if isinstance(val, Mapping):
            # For tag fields, we only want a list of IDs
            newtraits[key] = [str(tag['id']) for tag in val['values'] if tag.get('id') is not None]
        else:
            newtraits[key] = deepcopy(val)

    return newtraits
