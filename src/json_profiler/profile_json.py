import random
import math
from enum import Enum
from typing import Any
from dataclasses import dataclass
from datetime import datetime
from .enums import JsonType
from .models import ProfileOptions, JsonNode


def convertible_str_to_bool(data: str) -> dict:
    if not isinstance(data, str):
        raise ValueError(f"expected a string but receive {type(data)}")

    true_values =  {"true", "y", "t", "yes", "1"}
    false_values = { "false", "n", "f", "no", "0"}
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

def profile_string(key: str, data: str, node: JsonNode) -> JsonNode:
    if map_object_type(data) != JsonType.STRING:
         raise ValueError(f"Attempt to profile string on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key

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

    return JsonNode(
        json_type=JsonType.STRING,
        path=obj_path,
        parent_path=parent_path,
        source_value=data,
        length=len(data),
        is_whitespace_or_empty=not data.strip(),
        has_leading_whitespace=data != data.lstrip(),
        has_trailing_whitespace=data != data.rstrip(),
        convertible_to_number=convertible,
        numeric_representation=converted_str,
        convertible_to_date=date_profile.get("convertible_to_date"),
        date_format_string=date_profile.get("date_format_string"),
        date_representation=date_profile.get("date_representation"),
        convertible_to_boolean=bool_profile.get("convertible_to_boolean"),
        boolean_representation=bool_profile.get("boolean_representation")
    )

def profile_number(key: str, data: int|float, node: JsonNode) -> JsonNode:
    if map_object_type(data) != JsonType.NUMBER: 
        raise ValueError(f"Attempt to profile numeric on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key

    return JsonNode(
        json_type=JsonType.NUMBER,
        source_value=data,
        python_datatype=type(data).__name__,
        path=obj_path,
        parent_path=parent_path
    )

def profile_bool(key: str, data: bool, node: JsonNode) -> JsonNode:
    if map_object_type(data) != JsonType.BOOL: 
        raise ValueError(f"Attempt to profile boolean on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key

    return JsonNode(
        json_type=JsonType.BOOL,
        source_value=data,
        python_datatype=type(data).__name__,
        parent_path=parent_path,
        path=obj_path
    )

def profile_null(key: str, data, node: JsonNode) -> JsonNode:
    if data is not None:
        raise ValueError("Attempt to profile Null on Non-null value")

    parent_path = node.path
    obj_path = node.path + "." + key

    return JsonNode(
        json_type=JsonType.NULL,
        source_value=data,
        path=obj_path,
        parent_path=parent_path
    )

def profile_array(key: str, data: list, options: ProfileOptions, node: JsonNode) -> JsonNode:
    sample_count = max(1, math.floor(float(len(data)) * options.pct_sample)) if data else 0

    if map_object_type(data) != JsonType.ARRAY: 
        raise ValueError(f"Attempt to profile array on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key + "[*]"
    obj_depth = node.depth # arrays inherit the current depth; using object nesting depth instead of generic tree depth

    sample = random.sample(data, sample_count)

    profile = JsonNode(
        json_type=JsonType.ARRAY,
        array_count=len(data),
        sample_count=sample_count,
        parent_path=parent_path,
        path=obj_path,
        depth=obj_depth
    )

    profile.children = [profile_data(key=None, val=item, options=options, node=profile) for item in sample]

    return profile


def profile_object(key: str, data: dict, options: ProfileOptions, node: JsonNode) -> JsonNode:
    if map_object_type(data) != JsonType.OBJECT: 
        raise ValueError(f"Attempt to profile object on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path
    obj_depth = node.depth + 1
    
    profile = JsonNode(
        json_type=JsonType.OBJECT,
        keys=list(data.keys()),
        depth=obj_depth,
        parent_path=parent_path,
        path=obj_path
    )

    profile.children = [profile_data(key, val, options, profile) for key, val in data.items()]

    return profile


def profile_data(key: str, val: Any, options: ProfileOptions, node: JsonNode) -> JsonNode:
    json_type = map_object_type(data=val)

    if json_type == JsonType.OBJECT:
        return profile_object(key, val, options, node)
    if json_type == JsonType.ARRAY:
        return profile_array(key, val, options, node)
    if json_type == JsonType.STRING:
       return profile_string(key, val, node)
    if json_type == JsonType.NUMBER:
        return profile_number(key, val, node)
    if json_type == JsonType.BOOL:
        return profile_bool(key, val, node)
    if json_type == JsonType.NULL:
        return profile_null(key, val, node)

def profile_json(data: Any, options: ProfileOptions) -> JsonNode:
    if options.pct_sample <= 0.0 or options.pct_sample > 1.0:
        raise ValueError(f"pct_sample must be in range (0.0, 1.0]. {options.pct_sample} provided")

    profile = JsonNode(
        json_type=JsonType.ROOT,
        path="$",
        depth=0
    )
    profile.children = [profile_data(key="root", val=data, options=options, node=profile)]

    return profile
