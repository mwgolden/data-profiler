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
    instance_parent_path: int|None = None
    instance_path: int|None = None
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
            d["array_length"] = self.array_length
            d["sample_array_length"] = self.sample_array_length

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

    def explode(self) -> list[dict]:
        exploded_tree = []

        def visit_node(node: JsonNode):           
            d = dict()
            d["json_type"] = node.json_type.value
            d["source_value"] = node.source_value
            d["python_datatype"] = node.python_datatype
            d["parent_path"] = node.parent_path
            d["path"] = node.path
            d["instance_path"] = node.instance_path
            d["instance_parent_path"] = node.instance_parent_path
            d["keys"] = node.keys
            d["depth"] = node.depth
            d["array_length"] = node.array_length
            d["sample_array_length"] = node.sample_array_length
            d["str_length"] = node.str_length
            d["is_whitespace_or_empty"] = node.is_whitespace_or_empty
            d["has_leading_whitespace"] = node.has_leading_whitespace
            d["has_trailing_whitespace"] = node.has_trailing_whitespace
            d["convertible_to_number"] = node.convertible_to_number
            d["numeric_representation"] = node.numeric_representation
            d["convertible_to_date"] = node.convertible_to_date
            d["date_format_string"] = node.date_format_string
            d["date_representation"] = node.date_representation
            d["convertible_to_boolean"] = node.convertible_to_boolean
            d["boolean_representation"] = node.boolean_representation
            
            exploded_tree.append(d)
            for child in node.children:
                visit_node(child)

        visit_node(self)
        return  exploded_tree