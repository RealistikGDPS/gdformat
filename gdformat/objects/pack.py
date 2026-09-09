from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.encoding import strip_separators
from gdformat.enums import MapPackDifficulty
from gdformat.objects._common import Colour
from gdformat.objects._common import parse_colour
from gdformat.objects._common import serialise_colour
from gdformat.objects._common import serialise_integers


@dataclass(frozen=True, slots=True, kw_only=True)
class MapPack:
    id: int
    name: str
    level_ids: tuple[int, ...]
    stars: int
    coins: int
    difficulty: MapPackDifficulty
    text_colour: Colour
    bar_colour: Colour


@dataclass(frozen=True, slots=True, kw_only=True)
class Gauntlet:
    id: int
    level_ids: tuple[int, ...]


def serialise_map_pack(pack: MapPack) -> str:
    return (
        f"1:{pack.id}:2:{strip_separators(pack.name)}:3:{serialise_integers(pack.level_ids)}"
        f":4:{pack.stars}:5:{pack.coins}:6:{pack.difficulty:d}"
        f":7:{serialise_colour(pack.text_colour)}:8:{serialise_colour(pack.bar_colour)}"
    )


def parse_map_pack(text: str) -> ParseResult[MapPack]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    text_colour = parse_colour(values.get("7", "255,255,255"))
    bar_colour = parse_colour(values.get("8", "255,255,255"))

    if isinstance(text_colour, ParseError):
        return text_colour

    if isinstance(bar_colour, ParseError):
        return bar_colour

    reader = Reader(values)

    return reader.done(
        MapPack(
            id=reader.integer("1"),
            name=reader.string("2", default=""),
            level_ids=reader.integers("3"),
            stars=reader.integer("4", default=0),
            coins=reader.integer("5", default=0),
            difficulty=reader.member(
                "6", MapPackDifficulty, default=MapPackDifficulty.AUTO
            ),
            text_colour=text_colour,
            bar_colour=bar_colour,
        )
    )


def serialise_gauntlet(gauntlet: Gauntlet) -> str:
    return f"1:{gauntlet.id}:3:{serialise_integers(gauntlet.level_ids)}"


def parse_gauntlet(text: str) -> ParseResult[Gauntlet]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)

    return reader.done(Gauntlet(id=reader.integer("1"), level_ids=reader.integers("3")))
