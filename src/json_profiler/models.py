from dataclasses import dataclass, field
from .enums import JsonType
from typing import Any

@dataclass
class ProfileOptions:
    pct_sample: float = 1.0


@dataclass
class JsonNode:
    # common attributes
    json_type: JsonType
    source_value: Any|None = None
    python_datatype: str|None = None
    path: str|None = None
    parent_path: str|None = None
    children: list["JsonNode"] = field(default_factory=list["JsonNode"])

    # string attributes
    length: str|None = None
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
    array_count: int|None = None
    sample_count: int|None = None

    # object attributes
    keys: list[str]|None = None
    depth: int|None = None