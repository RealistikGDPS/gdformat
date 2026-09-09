from collections.abc import Mapping
from enum import IntEnum
from enum import StrEnum

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat.encoding import decode_text


def pairs(text: str, separator: str) -> dict[str, str] | None:
    parts = text.split(separator)

    if len(parts) % 2:
        return None

    return dict(zip(parts[::2], parts[1::2], strict=True))


def split_nonempty(text: str, separator: str) -> list[str]:
    return [part for part in text.split(separator) if part]


class Reader:
    """Reads typed values out of a string mapping, remembering the first failure.
    Failed reads return a placeholder so callers can build the whole model in one
    expression and then check `done`."""

    __slots__ = ("_values", "error")  # One instance per parsed request or object.

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = values
        self.error: ParseError | None = None

    def _fail(self, error: ParseError) -> None:
        if self.error is None:
            self.error = error

    def _to_int(self, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            self._fail(ParseError.INVALID_INTEGER)

            return 0

    def has(self, key: str) -> bool:
        return bool(self._values.get(key))

    def string(self, key: str, *, default: str | None = None) -> str:
        value = self._values.get(key)

        if value is not None:
            return value

        if default is None:
            self._fail(ParseError.MISSING)

            return ""

        return default

    def integer(self, key: str, *, default: int | None = None) -> int:
        value = self._values.get(key)

        if not value:
            if default is None:
                self._fail(ParseError.MISSING)
                return 0

            return default

        return self._to_int(value)

    def optional_integer(self, key: str) -> int | None:
        value = self._values.get(key)

        if not value:
            return None

        return self._to_int(value)

    def boolean(self, key: str, *, default: bool = False) -> bool:
        value = self._values.get(key)

        if not value:
            return default

        return value == "1"

    def member[E: IntEnum](
        self, key: str, kind: type[E], *, default: E | None = None
    ) -> E:
        value = self._values.get(key)

        if not value:
            if default is None:
                self._fail(ParseError.MISSING)
                return next(iter(kind))

            return default

        return self._to_member(value, kind)

    def optional_member[E: IntEnum](self, key: str, kind: type[E]) -> E | None:
        value = self._values.get(key)

        if not value:
            return None

        return self._to_member(value, kind)

    def _to_member[E: IntEnum](self, value: str, kind: type[E]) -> E:
        number = self._to_int(value)

        try:
            return kind(number)
        except ValueError:
            self._fail(ParseError.INVALID_VALUE)

            return next(iter(kind))

    def choice[E: StrEnum](
        self, key: str, kind: type[E], *, default: E | None = None
    ) -> E:
        value = self._values.get(key)

        if not value:
            if default is None:
                self._fail(ParseError.MISSING)
                return next(iter(kind))

            return default

        try:
            return kind(value)
        except ValueError:
            self._fail(ParseError.INVALID_VALUE)

            return next(iter(kind))

    def text(self, key: str, *, default: str | None = None) -> str:
        value = self._values.get(key)

        if not value:
            if default is None:
                self._fail(ParseError.MISSING)
                return ""

            return default

        decoded = decode_text(value)

        if decoded is None:
            self._fail(ParseError.INVALID_BASE64)

            return ""

        return decoded

    def integers(self, key: str, *, separator: str = ",") -> tuple[int, ...]:
        value = self._values.get(key)

        if not value or value == "-":
            return ()

        return tuple(
            self._to_int(part) for part in value.strip("()").split(separator) if part
        )

    def members[E: IntEnum](
        self,
        key: str,
        kind: type[E],
        *,
        separator: str = ",",
    ) -> tuple[E, ...]:
        value = self._values.get(key)

        if not value or value == "-":
            return ()

        return tuple(
            self._to_member(part, kind) for part in value.split(separator) if part
        )

    def done[T](self, value: T) -> ParseResult[T]:
        if self.error is not None:
            return self.error

        return value
