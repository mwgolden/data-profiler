import random
import math
from typing import Any
from dataclasses import dataclass
from datetime import datetime
from .enums import JsonType, map_object_type
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

def profile_string(key: str, data: str, node: JsonNode, source_array_index: int | None) -> JsonNode:
    if map_object_type(data) != JsonType.STRING:
         raise ValueError(f"Attempt to profile string on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path

    instance_path = obj_path
    instance_parent_path = parent_path
    if source_array_index:
        instance_path = obj_path.replace("[*]", f"[{source_array_index}]")
        instance_parent_path = parent_path.replace("[*]", f"[{source_array_index}]")


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
        source_key=key,
        path=obj_path,
        parent_path=parent_path,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path,
        source_value=data,
        str_length=len(data),
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

def profile_number(key: str, data: int|float, node: JsonNode, source_array_index: int | None) -> JsonNode:
    if map_object_type(data) != JsonType.NUMBER: 
        raise ValueError(f"Attempt to profile numeric on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path

    instance_path = obj_path
    instance_parent_path = parent_path
    if source_array_index:
        instance_path = obj_path.replace("[*]", f"[{source_array_index}]")
        instance_parent_path = parent_path.replace("[*]", f"[{source_array_index}]")

    return JsonNode(
        json_type=JsonType.NUMBER,
        source_key=key,
        source_value=data,
        python_datatype=type(data).__name__,
        path=obj_path,
        parent_path=parent_path,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path
    )

def profile_bool(key: str, data: bool, node: JsonNode, source_array_index: int | None) -> JsonNode:
    if map_object_type(data) != JsonType.BOOL: 
        raise ValueError(f"Attempt to profile boolean on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path

    instance_path = obj_path
    instance_parent_path = parent_path
    if source_array_index:
        instance_path = obj_path.replace("[*]", f"[{source_array_index}]")
        instance_parent_path = parent_path.replace("[*]", f"[{source_array_index}]")

    return JsonNode(
        json_type=JsonType.BOOL,
        source_key=key,
        source_value=data,
        python_datatype=type(data).__name__,
        parent_path=parent_path,
        path=obj_path,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path
    )

def profile_null(key: str, data, node: JsonNode, source_array_index: int | None) -> JsonNode:
    if data is not None:
        raise ValueError("Attempt to profile Null on Non-null value")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path

    instance_path = obj_path
    instance_parent_path = parent_path
    if source_array_index:
        instance_path = obj_path.replace("[*]", f"[{source_array_index}]")
        instance_parent_path = parent_path.replace("[*]", f"[{source_array_index}]")

    return JsonNode(
        json_type=JsonType.NULL,
        source_key=key,
        source_value=data,
        path=obj_path,
        parent_path=parent_path,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path
    )

def profile_array(key: str, data: list, options: ProfileOptions, node: JsonNode) -> JsonNode:
    sample_count = max(1, math.floor(float(len(data)) * options.pct_sample)) if data else 0

    if map_object_type(data) != JsonType.ARRAY: 
        raise ValueError(f"Attempt to profile array on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key + "[*]"
    obj_depth = node.depth # arrays inherit the current depth; using object nesting depth instead of generic tree depth

    instance_path = obj_path
    instance_parent_path = parent_path

    sample_indexes = random.sample(range(len(data)), sample_count)

    profile = JsonNode(
        json_type=JsonType.ARRAY,
        source_key=key,
        array_length=len(data),
        sample_array_length=sample_count,
        parent_path=parent_path,
        path=obj_path,
        depth=obj_depth,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path
    )

    profile.children = [
            profile_data(
                key=None, 
                val=data[source_index], 
                options=options, 
                node=profile, 
                source_array_index=source_index
            ) 
            for source_index in sample_indexes
        ]

    return profile


def profile_object(key: str, data: dict, options: ProfileOptions, node: JsonNode, source_array_index: int | None) -> JsonNode:
    if map_object_type(data) != JsonType.OBJECT: 
        raise ValueError(f"Attempt to profile object on type {type(data)}")

    parent_path = node.path
    obj_path = node.path + "." + key if key else node.path
    obj_depth = node.depth + 1

    instance_path = obj_path
    instance_parent_path = parent_path
    if source_array_index:
        instance_path = obj_path.replace("[*]", f"[{source_array_index}]")
        instance_parent_path = parent_path.replace("[*]", f"[{source_array_index}]")
        
    profile = JsonNode(
        json_type=JsonType.OBJECT,
        source_key=key,
        keys=list(data.keys()),
        depth=obj_depth,
        parent_path=parent_path,
        path=obj_path,
        instance_path=instance_path,
        instance_parent_path=instance_parent_path
    )

    profile.children = [profile_data(key, val, options, profile, source_array_index=source_array_index) for key, val in data.items()]

    return profile


def profile_data(key: str, val: Any, options: ProfileOptions, node: JsonNode, source_array_index: int | None) -> JsonNode:
    json_type = map_object_type(data=val)

    if json_type == JsonType.OBJECT:
        return profile_object(key, val, options, node, source_array_index)
    if json_type == JsonType.ARRAY:
        return profile_array(key, val, options, node)
    if json_type == JsonType.STRING:
       return profile_string(key, val, node, source_array_index)
    if json_type == JsonType.NUMBER:
        return profile_number(key, val, node, source_array_index)
    if json_type == JsonType.BOOL:
        return profile_bool(key, val, node, source_array_index)
    if json_type == JsonType.NULL:
        return profile_null(key, val, node, source_array_index)

def profile_json(data: Any, options: ProfileOptions) -> JsonNode:
    if options.pct_sample <= 0.0 or options.pct_sample > 1.0:
        raise ValueError(f"pct_sample must be in range (0.0, 1.0]. {options.pct_sample} provided")

    profile = JsonNode(
        json_type=JsonType.ROOT,
        path="$",
        depth=0
    )

    if map_object_type(data) == JsonType.OBJECT:
        profile.children = [profile_data(key, val, options, profile, source_array_index=None) for key, val in data.items()]

    if map_object_type(data) == JsonType.ARRAY:
        profile.children = [profile_data("", data, options, profile, source_array_index=None)]

    return profile
