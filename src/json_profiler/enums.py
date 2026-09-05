from enum import Enum
from typing import Any

class JsonType(Enum):
    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    BOOL = "boolean"
    NULL = "null"
    ROOT = "root"

def map_object_type(data: Any) -> JsonType:
    if isinstance(data, dict):
        return JsonType.OBJECT
    if isinstance(data, list):
        return JsonType.ARRAY
    if isinstance(data, str):
        return JsonType.STRING
    if isinstance(data, bool):
        return JsonType.BOOL
    if isinstance(data, (int, float)):
        return JsonType.NUMBER
    if data is None:
        return JsonType.NULL

    raise ValueError(f"type {type(data)} is not convertible to JSON type")