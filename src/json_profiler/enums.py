from enum import Enum

class JsonType(Enum):
    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    BOOL = "boolean"
    NULL = "null"
    ROOT = "root"