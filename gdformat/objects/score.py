from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.objects.user import Player
from gdformat.objects.user import read_player
from gdformat.objects.user import serialise_player


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelScore:
    """A level leaderboard row. `value` is the percentage for classic levels and the
    time in milliseconds or the points for platformer levels."""

    player: Player
    value: int
    rank: int
    age: str
    coins: int = 0


def serialise_level_score(score: LevelScore) -> str:
    return (
        f"{serialise_player(score.player)}:3:{score.value}:6:{score.rank}"
        f":13:{score.coins}:42:{score.age}"
    )


def parse_level_score(text: str) -> ParseResult[LevelScore]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)

    return reader.done(
        LevelScore(
            player=read_player(reader),
            value=reader.integer("3", default=0),
            rank=reader.integer("6", default=0),
            age=reader.string("42", default=""),
            coins=reader.integer("13", default=0),
        )
    )
