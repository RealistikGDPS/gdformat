from collections.abc import Mapping
from enum import StrEnum
from typing import TypeIs

type Form = Mapping[str, str]


class ParseError(StrEnum):
    MISSING = "missing"
    INVALID_INTEGER = "invalid_integer"
    INVALID_VALUE = "invalid_value"
    INVALID_BASE64 = "invalid_base64"
    INVALID_LAYOUT = "invalid_layout"


type ParseResult[T] = T | ParseError


def is_error[T](value: ParseResult[T]) -> TypeIs[ParseError]:
    return isinstance(value, ParseError)


def is_success[T](value: ParseResult[T]) -> TypeIs[T]:
    return not isinstance(value, ParseError)
