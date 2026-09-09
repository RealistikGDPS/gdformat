from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult


@dataclass(frozen=True, slots=True)
class Colour:
    red: int
    green: int
    blue: int


@dataclass(frozen=True, slots=True)
class Page:
    total: int
    offset: int
    size: int = 10


def serialise_colour(colour: Colour) -> str:
    return f"{colour.red},{colour.green},{colour.blue}"


def parse_colour(text: str) -> ParseResult[Colour]:
    parts = text.split(",")

    if len(parts) != 3:
        return ParseError.INVALID_LAYOUT

    try:
        red, green, blue = (int(part) for part in parts)
    except ValueError:
        return ParseError.INVALID_INTEGER

    return Colour(red, green, blue)


def serialise_page(page: Page) -> str:
    return f"{page.total}:{page.offset}:{page.size}"


def parse_page(text: str) -> ParseResult[Page]:
    parts = text.split(":")

    if len(parts) != 3:
        return ParseError.INVALID_LAYOUT

    try:
        total, offset, size = (int(part) for part in parts)
    except ValueError:
        return ParseError.INVALID_INTEGER

    return Page(total, offset, size)


def serialise_integers(values: tuple[int, ...], *, separator: str = ",") -> str:
    return separator.join(map(str, values))
