from collections.abc import MutableMapping
from datetime import date, datetime, timedelta  # noqa
from typing import Dict, ForwardRef, List, Optional, Union

from pydantic import Field





def parse_field_info(field, required=False):
    type_annotation = parse_type(field)
    if not required:
        type_annotation = Optional[type_annotation]

    return (
        type_annotation, 
        Field(
            title=field.get('title'),
            default=field.get('default'),
        )
    )



def parse_type(p, schemas: Optional[dict] = None):
    # check for x-ref at root
    if "$ref" in p.keys():
        ref = p["$ref"].split("/")[-1]
        return schemas[ref] if schemas is not None else ForwardRef(ref)
    else:
        if "anyOf" in p.keys():
            any_of_types = tuple(parse_type(el) for el in p["anyOf"])
            if len(any_of_types) == 1:
                return any_of_types[0]
            else:
                return Union[any_of_types]  # noqa: F821

        if const := p.get("const"):
            return type(const)

        else:
            try:
                if p["type"] == "string":
                    _format = p.get("format")
                    if _format:
                        if _format == "date-time":
                            return datetime
                        elif _format == "date":
                            return date
                        elif _format == "binary":
                            return bytes
                        else:
                            return str
                    else:
                        return str
                elif p["type"] == "null":
                    return None
                elif p["type"] == "number":
                    return float
                elif p["type"] == "integer":
                    return int
                elif p["type"] == "array":
                    items = p.get("items") or p.get("prefixItems")
                    if isinstance(items, list):
                        array_of_types = [parse_type(el, schemas) for el in items]
                        return List[*list(set(array_of_types))]
                    else:
                        return conlist(
                            parse_type(items, schemas),
                            min_length=p.get("minItems", None),
                            max_length=p.get("maxItems", None),
                        )
                elif p["type"] == "boolean":
                    return bool
                elif p["type"] == "object":
                    if "additionalProperties" in p.keys():
                        return Dict[
                            str,
                            parse_type(
                                p["additionalProperties"], schemas  # noqa: F821
                            ),
                        ]
                    else:
                        return dict
                else:
                    raise ValueError(f'Type {p["type"]} not parseable')
            except KeyError:
                raise KeyError("Could not determine type from available keys")