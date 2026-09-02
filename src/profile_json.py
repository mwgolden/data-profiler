import random
import math
from enum import Enum
from typing import Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileOptions:
    pct_sample: float = 1.0

class JsonType(Enum):
    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    BOOL = "boolean"
    NULL = "null"

def convertible_str_to_bool(data: str) -> dict:
    if not isinstance(data, str):
        raise ValueError(f"expected a string but receive {type(data)}")

    true_values =  {"true", "y", "t", "yes", "1"}
    false_values = { "false", "n", "f", "no", 0}
    normalized_string = data.strip().lower()

    if normalized_string in true_values:
        return {
            "convertible_to_boolean": True,
            "boolean_representation": True
        }
    
    if normalized_string in false_values:
        return {
                "convertible_to_boolean": True,
                "boolean_representation": False
            }
    
    return {
        "convertible_to_boolean": False,
        "boolean_representation": None
    }

def convertable_str_to_int(data: str) -> bool:
    if not isinstance(data, str):
            raise ValueError(f"expected a string but receive {type(data)}")
    
    try:
        int(data)
        return True
    except (ValueError, TypeError):
        return False

def convertable_str_to_float(data: Any) -> bool:
    try:
        float(data)
        return True
    except (ValueError, TypeError):
        return False

def convertible_str_to_date(data: str) -> dict: 
    if not isinstance(data, str):
            raise ValueError(f"expected a string but receive {type(data)}")
    
    common_format_strings =  [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y%m%d",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
        "%Y-%m-%dT%H:%M:%S%z"
    ]

    for format_string in common_format_strings:
        try:
            dt = datetime.strptime(data, format_string)
            return {
                "convertible_to_date": True,
                "date_format_string": format_string,
                "date_representation": dt.strftime(format_string)
            }
        except ValueError:
            pass

    return  {
        "convertible_to_date": False,
        "date_format_string": None,
        "date_representation": None
    }



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

def profile_string(data: str, cur, path) -> dict:
    profile = dict()

    if map_object_type(data) != JsonType.STRING:
         raise ValueError(f"Attempt to profile string on type {type(data)}")

    obj_path = path + "." + cur

    convertible = False
    converted_str = None
    if convertable_str_to_int(data):
        convertible = True
        converted_str = int(data)
    elif convertable_str_to_float(data):
        convertible = True
        converted_str = float(data)

    date_profile = convertible_str_to_date(data)

    bool_profile = convertible_str_to_bool(data)

    profile["source_value"] = data
    profile["type"] = JsonType.STRING.value
    profile["length"] = len(data)
    profile["is_whitespace_or_empty"] = not data.strip()
    profile["has_leading_whitespace"] = data != data.lstrip()
    profile["has_trailing_whitespace"] = data != data.rstrip()
    profile["convertible_to_number"] = convertible
    profile["numeric_representation"] = converted_str
    profile.update(date_profile)
    profile.update(bool_profile)
    profile["path"] = obj_path
    profile["parent_path"] = path

    return profile

def profile_number(data: int|float, cur, path) -> dict:
    profile = dict()

    if map_object_type(data) != JsonType.NUMBER: 
        raise ValueError(f"Attempt to profile numeric on type {type(data)}")

    obj_path = path + "." + cur

    profile["source_value"] = data
    profile["type"] = JsonType.NUMBER.value
    profile["python_type"] = type(data).__name__
    profile["value"] = data
    profile["path"] = obj_path
    profile["parent_path"] = path

    return profile

def profile_bool(data: bool, cur, path) -> dict:
    profile = dict()

    if map_object_type(data) != JsonType.BOOL: 
        raise ValueError(f"Attempt to profile boolean on type {type(data)}")

    obj_path = path + "." + cur

    profile["source_value"] = data
    profile["type"] = JsonType.BOOL.value
    profile["value"] = data
    profile["path"] = obj_path
    profile["parent_path"] = path

    return profile

def profile_null(data, cur, path) -> dict:
    profile = dict()

    if data is not None:
        raise ValueError("Attempt to profile Null on Non-null value")

    obj_path = path + "." + cur

    profile["source_value"] = data
    profile["type"] = JsonType.NULL.value
    profile["path"] = obj_path
    profile["parent_path"] = path

    return profile

def profile_array(data: list, options: ProfileOptions, depth: int, cur: str, path: str) -> dict:
    profile = dict()
    sample_count = max(1, math.floor(float(len(data)) * options.pct_sample)) if data else 0

    if map_object_type(data) != JsonType.ARRAY: 
        raise ValueError(f"Attempt to profile array on type {type(data)}")

    obj_path = path + "." + cur + "[*]"

    profile["type"] = JsonType.ARRAY.value
    profile["array_count"] = len(data)
    profile["sample_count"] = sample_count
    profile["parent_path"] = path

    sample = random.sample(data, sample_count)
    profile["items"] = [profile_data(item, options, depth, None, obj_path) for item in sample]

    return profile


def profile_object(data: dict, options: ProfileOptions, depth: int, cur: str|None, path: str) -> dict:
    profile = dict()

    if map_object_type(data) != JsonType.OBJECT: 
        raise ValueError(f"Attempt to profile object on type {type(data)}")

    obj_path = path + "." + cur if cur else path

    profile["type"] = JsonType.OBJECT.value
    profile["keys"] = list(data.keys())
    profile["depth"] = depth
    profile["parent_path"] = path
    profile["path"] = obj_path

    for key ,val in data.items():
        profile[key] = profile_data(val, options, depth+1, cur=key, path=obj_path)

    return profile


def profile_data(data: Any, options: ProfileOptions, depth: int, cur: str, path: str) -> dict:
    json_type = map_object_type(data=data)

    if json_type == JsonType.OBJECT:
        return profile_object(data, options, depth, cur, path)
    if json_type == JsonType.ARRAY:
        return profile_array(data, options, depth, cur, path)
    if json_type == JsonType.STRING:
       return profile_string(data, cur, path)
    if json_type == JsonType.NUMBER:
        return profile_number(data, cur, path)
    if json_type == JsonType.BOOL:
        return profile_bool(data, cur, path)
    if json_type == JsonType.NULL:
        return profile_null(data, cur, path)

def profile_json(data: Any, options: ProfileOptions) -> dict:
    if options.pct_sample <= 0.0 or options.pct_sample > 1.0:
        raise ValueError(f"pct_sample must be in range (0.0, 1.0]. {options.pct_sample} provided")
    
    profile = dict()
    profile["type"] = map_object_type(data).value
    profile["root"] = profile_data(data, options, depth=0, cur="root", path="$")

    return profile