from dataclasses import dataclass, field, fields
from .enums import JsonType
from typing import Any

@dataclass
class ProfileOptions:
    pct_sample: float = 1.0


@dataclass
class JsonNode:
    # common attributes
    json_type: JsonType
    source_key: str|None = None
    source_value: Any|None = None
    python_datatype: str|None = None
    path: str|None = None
    parent_path: str|None = None
    children: list["JsonNode"] = field(default_factory=list["JsonNode"])

    # string attributes
    str_length: int|None = None
    is_whitespace_or_empty: bool|None = None
    has_leading_whitespace: bool|None = None
    has_trailing_whitespace: bool|None = None
    convertible_to_number: bool|None = None
    numeric_representation: int|float|None = None
    convertible_to_date: bool|None = None
    date_format_string: str|None = None
    date_representation: str|None = None
    convertible_to_boolean: bool|None = None
    boolean_representation: bool|None = None

    # array attributes
    array_length: int|None = None
    sample_array_length: int|None = None

    # object attributes
    keys: list[str]|None = None
    depth: int|None = None

    def to_dict(self):
        d = dict()
        d["json_type"] = self.json_type.value
        d["source_value"] = self.source_value
        d["python_datatype"] = self.python_datatype
        d["path"] = self.path

        if self.json_type == JsonType.OBJECT:
            d["keys"] = self.keys
            d["depth"] = self.depth

        if self.json_type == JsonType.ARRAY:
            d["array_length"] = self.array_count
            d["sample_array_length"] = self.sample_count

        if self.json_type == JsonType.STRING:
            d["str_length"] = self.str_length
            d["is_whitespace_or_empty"] = self.is_whitespace_or_empty
            d["has_leading_whitespace"] = self.has_leading_whitespace
            d["has_trailing_whitespace"] = self.has_trailing_whitespace
            d["convertible_to_number"] = self.convertible_to_number
            d["numeric_representation"] = self.numeric_representation
            d["convertible_to_date"] = self.convertible_to_date
            d["date_format_string"] = self.date_format_string
            d["date_representation"] = self.date_representation
            d["convertible_to_boolean"] = self.convertible_to_boolean
            d["boolean_representation"] = self.boolean_representation

        for child in self.children:
            if child.json_type == JsonType.ARRAY:
                d[child.source_key] = [item.to_dict() for item in child.children]
            else:
                d[child.source_key] = child.to_dict()

        return d