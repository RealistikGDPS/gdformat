from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.encoding import decode_text
from gdformat.encoding import encode_text
from gdformat.enums import ModLevel
from gdformat.objects._common import Colour
from gdformat.objects._common import parse_colour
from gdformat.objects._common import serialise_colour
from gdformat.objects.user import Player
from gdformat.objects.user import read_player
from gdformat.objects.user import serialise_player

COMMENT_SEPARATOR = "~"


@dataclass(frozen=True, slots=True, kw_only=True)
class Comment:
    id: int
    content: str
    author: Player
    likes: int
    age: str
    percent: int = 0
    is_spam: bool = False
    level_id: int | None = None
    mod_level: ModLevel = ModLevel.NONE
    chat_colour: Colour | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountComment:
    id: int
    content: str
    likes: int
    age: str


def serialise_comment(comment: Comment) -> str:
    text = (
        f"2~{encode_text(comment.content)}~3~{comment.author.user_id}~4~{comment.likes}"
        f"~7~{comment.is_spam:d}~9~{comment.age}~6~{comment.id}~10~{comment.percent}"
    )

    if comment.level_id is not None:
        text = f"1~{comment.level_id}~{text}"

    if comment.mod_level is not ModLevel.NONE:
        text += f"~11~{comment.mod_level:d}"

        if comment.chat_colour is not None:
            text += f"~12~{serialise_colour(comment.chat_colour)}"

    author = serialise_player(comment.author, COMMENT_SEPARATOR, include_user_id=False)

    return f"{text}:{author}"


def parse_comment(text: str) -> ParseResult[Comment]:
    body, separator, author_text = text.partition(":")

    if not separator:
        return ParseError.INVALID_LAYOUT

    values = pairs(body, COMMENT_SEPARATOR)
    author_values = pairs(author_text, COMMENT_SEPARATOR)

    if values is None or author_values is None:
        return ParseError.INVALID_LAYOUT

    content = decode_text(values.get("2", ""))

    if content is None:
        return ParseError.INVALID_BASE64

    chat_colour = None

    if "12" in values:
        parsed = parse_colour(values["12"])

        if isinstance(parsed, ParseError):
            return parsed

        chat_colour = parsed

    author_reader = Reader(author_values)
    author = read_player(author_reader)
    reader = Reader(values)

    author = Player(
        name=author.name,
        user_id=reader.integer("3", default=author.user_id),
        account_id=author.account_id,
        icon=author.icon,
    )

    comment = Comment(
        id=reader.integer("6"),
        content=content,
        author=author,
        likes=reader.integer("4", default=0),
        age=reader.string("9", default=""),
        percent=reader.integer("10", default=0),
        is_spam=reader.boolean("7"),
        level_id=reader.optional_integer("1"),
        mod_level=reader.member("11", ModLevel, default=ModLevel.NONE),
        chat_colour=chat_colour,
    )

    if author_reader.error is not None:
        return author_reader.error

    return reader.done(comment)


def serialise_account_comment(comment: AccountComment) -> str:
    content = encode_text(comment.content)

    return f"2~{content}~4~{comment.likes}~9~{comment.age}~6~{comment.id}"


def parse_account_comment(text: str) -> ParseResult[AccountComment]:
    values = pairs(text, COMMENT_SEPARATOR)

    if values is None:
        return ParseError.INVALID_LAYOUT

    content = decode_text(values.get("2", ""))

    if content is None:
        return ParseError.INVALID_BASE64

    reader = Reader(values)

    return reader.done(
        AccountComment(
            id=reader.integer("6"),
            content=content,
            likes=reader.integer("4", default=0),
            age=reader.string("9", default=""),
        )
    )
