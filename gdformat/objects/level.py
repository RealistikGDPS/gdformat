from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.crypto import decode_level_password
from gdformat.crypto import encode_level_password
from gdformat.encoding import decode_text
from gdformat.encoding import encode_text
from gdformat.encoding import strip_separators
from gdformat.enums import Difficulty
from gdformat.enums import Length
from gdformat.enums import Rating
from gdformat.objects._common import serialise_integers

_DIFFICULTY_STEP = 10
_DENOMINATOR = 10
_AUTO_NUMERATOR = -10
_DEMON_CODES = {
    Difficulty.EASY_DEMON: 3,
    Difficulty.MEDIUM_DEMON: 4,
    Difficulty.HARD_DEMON: 0,
    Difficulty.INSANE_DEMON: 5,
    Difficulty.EXTREME_DEMON: 6,
}
_DEMON_FROM_CODE = {code: difficulty for difficulty, code in _DEMON_CODES.items()}
# NOTE: The official server sets the numerator to 10 per demon tier as well.
_DEMON_NUMERATORS = {
    difficulty: (index + 1) * _DIFFICULTY_STEP
    for index, difficulty in enumerate(_DEMON_CODES)
}


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelPreview:
    """A level as listed by getGJLevels21."""

    id: int
    name: str
    description: str
    version: int
    creator_id: int
    difficulty: Difficulty
    downloads: int
    likes: int
    length: Length
    stars: int
    feature_score: int = 0
    rating: Rating = Rating.NONE
    official_song: int = 0
    custom_song_id: int = 0
    game_version: int = 22
    coins: int = 0
    verified_coins: bool = False
    requested_stars: int = 0
    objects: int = 0
    original_id: int = 0
    two_player: bool = False
    editor_time: int = 0
    editor_time_copies: int = 0
    gauntlet: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class Level(LevelPreview):
    """A level as returned by downloadGJLevel22."""

    level_string: str
    uploaded_ago: str
    updated_ago: str
    password: str | None = None
    extra_string: str = ""
    low_detail_mode: bool = False
    timely_id: int | None = None
    song_ids: tuple[int, ...] = ()
    sfx_ids: tuple[int, ...] = ()
    song_size: int = 0
    verification_time: int = 0
    uploaded_at: int = 0
    updated_at: int = 0


def _difficulty_wire(difficulty: Difficulty) -> str:
    # NOTE: The official server sends empty values for false on keys 17 and 25.
    match difficulty:
        case Difficulty.NA:
            return "8:0:9:0:17::25::43:0"
        case Difficulty.AUTO:
            return f"8:{_DENOMINATOR}:9:{_AUTO_NUMERATOR}:17::25:1:43:0"
        case _ if difficulty.is_demon:
            code = _DEMON_CODES[difficulty]
            numerator = _DEMON_NUMERATORS[difficulty]

            return f"8:{_DENOMINATOR}:9:{numerator}:17:1:25::43:{code}"
        case _:
            numerator = difficulty * _DIFFICULTY_STEP

            return f"8:{_DENOMINATOR}:9:{numerator}:17::25::43:0"


_DIFFICULTY_WIRE = {
    difficulty: _difficulty_wire(difficulty) for difficulty in Difficulty
}


def _read_difficulty(reader: Reader) -> Difficulty:
    if reader.boolean("25"):
        return Difficulty.AUTO

    if reader.boolean("17"):
        return _DEMON_FROM_CODE.get(
            reader.integer("43", default=0), Difficulty.HARD_DEMON
        )

    if reader.integer("8", default=0) == 0:
        return Difficulty.NA

    numerator = reader.integer("9", default=0)

    return Difficulty(min(max(numerator // _DIFFICULTY_STEP, 0), Difficulty.INSANE))


def _serialise_preview_body(level: LevelPreview) -> str:
    text = (
        f"1:{level.id}:2:{strip_separators(level.name)}:3:{encode_text(level.description)}"
        f":5:{level.version}:6:{level.creator_id}:{_DIFFICULTY_WIRE[level.difficulty]}"
        f":10:{level.downloads}:12:{level.official_song}:13:{level.game_version}"
        f":14:{level.likes}:15:{level.length:d}:18:{level.stars}:19:{level.feature_score}"
        f":42:{level.rating:d}:45:{level.objects}:30:{level.original_id}"
        f":31:{level.two_player:d}:35:{level.custom_song_id}:37:{level.coins}"
        f":38:{level.verified_coins:d}:39:{level.requested_stars}:46:{level.editor_time}"
        f":47:{level.editor_time_copies}"
    )

    if level.gauntlet:
        text += ":44:1"

    return text


def serialise_level_preview(level: LevelPreview) -> str:
    return _serialise_preview_body(level)


def serialise_level(level: Level) -> str:
    text = (
        f"{_serialise_preview_body(level)}:4:{level.level_string}"
        f":27:{encode_level_password(level.password)}:28:{level.uploaded_ago}"
        f":29:{level.updated_ago}:36:{level.extra_string}:40:{level.low_detail_mode:d}"
        f":57:{level.verification_time}:62:{level.uploaded_at}:63:{level.updated_at}"
    )

    if level.song_ids or level.sfx_ids:
        text += (
            f":52:{serialise_integers(level.song_ids)}"
            f":53:{serialise_integers(level.sfx_ids)}:54:{level.song_size}"
        )

    if level.timely_id is not None:
        text += f":41:{level.timely_id}"

    return text


def _read_preview(reader: Reader) -> ParseResult[LevelPreview]:
    description = decode_text(reader.string("3", default=""))

    if description is None:
        return ParseError.INVALID_BASE64

    return reader.done(
        LevelPreview(
            id=reader.integer("1"),
            name=reader.string("2", default=""),
            description=description,
            version=reader.integer("5", default=1),
            creator_id=reader.integer("6", default=0),
            difficulty=_read_difficulty(reader),
            downloads=reader.integer("10", default=0),
            likes=reader.integer("14", default=0),
            length=reader.member("15", Length, default=Length.TINY),
            stars=reader.integer("18", default=0),
            feature_score=reader.integer("19", default=0),
            rating=reader.member("42", Rating, default=Rating.NONE),
            official_song=reader.integer("12", default=0),
            custom_song_id=reader.integer("35", default=0),
            game_version=reader.integer("13", default=0),
            coins=reader.integer("37", default=0),
            verified_coins=reader.boolean("38"),
            requested_stars=reader.integer("39", default=0),
            objects=reader.integer("45", default=0),
            original_id=reader.integer("30", default=0),
            two_player=reader.boolean("31"),
            editor_time=reader.integer("46", default=0),
            editor_time_copies=reader.integer("47", default=0),
            gauntlet=reader.boolean("44"),
        )
    )


def parse_level_preview(text: str) -> ParseResult[LevelPreview]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    return _read_preview(Reader(values))


def parse_level(text: str) -> ParseResult[Level]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)
    preview = _read_preview(reader)

    if isinstance(preview, ParseError):
        return preview

    return reader.done(
        Level(
            id=preview.id,
            name=preview.name,
            description=preview.description,
            version=preview.version,
            creator_id=preview.creator_id,
            difficulty=preview.difficulty,
            downloads=preview.downloads,
            likes=preview.likes,
            length=preview.length,
            stars=preview.stars,
            feature_score=preview.feature_score,
            rating=preview.rating,
            official_song=preview.official_song,
            custom_song_id=preview.custom_song_id,
            game_version=preview.game_version,
            coins=preview.coins,
            verified_coins=preview.verified_coins,
            requested_stars=preview.requested_stars,
            objects=preview.objects,
            original_id=preview.original_id,
            two_player=preview.two_player,
            editor_time=preview.editor_time,
            editor_time_copies=preview.editor_time_copies,
            gauntlet=preview.gauntlet,
            level_string=reader.string("4", default=""),
            uploaded_ago=reader.string("28", default=""),
            updated_ago=reader.string("29", default=""),
            password=decode_level_password(reader.string("27", default="0")),
            extra_string=reader.string("36", default=""),
            low_detail_mode=reader.boolean("40"),
            timely_id=reader.optional_integer("41"),
            song_ids=reader.integers("52"),
            sfx_ids=reader.integers("53"),
            song_size=reader.integer("54", default=0),
            verification_time=reader.integer("57", default=0),
            uploaded_at=reader.integer("62", default=0),
            updated_at=reader.integer("63", default=0),
        )
    )
