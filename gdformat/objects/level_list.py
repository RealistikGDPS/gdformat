from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.encoding import decode_text
from gdformat.encoding import encode_text
from gdformat.encoding import strip_separators
from gdformat.enums import Difficulty
from gdformat.objects._common import serialise_integers


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelList:
    id: int
    name: str
    description: str
    version: int
    creator_account_id: int
    creator_name: str
    level_ids: tuple[int, ...]
    difficulty: Difficulty
    downloads: int
    likes: int
    uploaded_at: int
    updated_at: int
    rated: bool = False
    reward_diamonds: int = 0
    reward_requirement: int = 0


def serialise_level_list(level_list: LevelList) -> str:
    return (
        f"1:{level_list.id}:2:{strip_separators(level_list.name)}"
        f":3:{encode_text(level_list.description)}:5:{level_list.version}"
        f":49:{level_list.creator_account_id}:50:{strip_separators(level_list.creator_name)}"
        f":10:{level_list.downloads}:7:{level_list.difficulty:d}:14:{level_list.likes}"
        f":19:{'1' if level_list.rated else ''}"
        f":51:{serialise_integers(level_list.level_ids)}"
        f":55:{level_list.reward_diamonds}:56:{level_list.reward_requirement}"
        f":28:{level_list.uploaded_at}:29:{level_list.updated_at}"
    )


def parse_level_list(text: str) -> ParseResult[LevelList]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    description = decode_text(values.get("3", ""))

    if description is None:
        return ParseError.INVALID_BASE64

    reader = Reader(values)

    return reader.done(
        LevelList(
            id=reader.integer("1"),
            name=reader.string("2", default=""),
            description=description,
            version=reader.integer("5", default=1),
            creator_account_id=reader.integer("49", default=0),
            creator_name=reader.string("50", default=""),
            level_ids=reader.integers("51"),
            difficulty=reader.member("7", Difficulty, default=Difficulty.NA),
            downloads=reader.integer("10", default=0),
            likes=reader.integer("14", default=0),
            uploaded_at=reader.integer("28", default=0),
            updated_at=reader.integer("29", default=0),
            rated=reader.boolean("19"),
            reward_diamonds=reader.integer("55", default=0),
            reward_requirement=reader.integer("56", default=0),
        )
    )
