from typing import List, Any
from enum import Enum


def _convert_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_convert_value(item) for item in value]
    return value


def custom_dict_factory(data: List[tuple[str, Any]]) -> dict:
    return {key: _convert_value(value) for key, value in data}
