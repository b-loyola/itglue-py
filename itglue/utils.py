from copy import deepcopy
from typing import Mapping


def prepare_tag_traits_for_upload(traits: Mapping):
    newtraits = {}

    for key, val in traits.items():
        if isinstance(val, Mapping):
            # For tag fields, we only want a list of IDs
            newtraits[key] = [str(tag['id']) for tag in val['values'] if tag.get('id') is not None]
        else:
            newtraits[key] = deepcopy(val)

    return newtraits
