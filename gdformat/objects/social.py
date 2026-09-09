from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.crypto import KEY_MESSAGE
from gdformat.encoding import decode_text
from gdformat.encoding import decode_xor_text
from gdformat.encoding import encode_text
from gdformat.encoding import encode_xor_text
from gdformat.encoding import strip_separators
from gdformat.enums import MessageState
from gdformat.objects.user import Player
from gdformat.objects.user import UserRef
from gdformat.objects.user import read_player
from gdformat.objects.user import serialise_player


@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerStats:
    stars: int = 0
    moons: int = 0
    demons: int = 0
    creator_points: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class FriendRequest:
    id: int
    player: Player
    message: str
    age: str
    is_new: bool = False
    stats: PlayerStats = PlayerStats()


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    id: int
    peer: UserRef
    subject: str
    age: str
    read: bool = False
    outgoing: bool = False
    body: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UserListEntry:
    player: Player
    is_new: bool = False
    stats: PlayerStats = PlayerStats()
    message_state: MessageState = MessageState.ALL
    # NOTE: Keys 62, 63 and 64 are undocumented; the official server sends 0, 2, 0.
    ship_fire: int = 0
    extra: int = 2
    extra2: int = 0


def _serialise_stats(stats: PlayerStats) -> str:
    return f"3:{stats.stars}:52:{stats.moons}:4:{stats.demons}:8:{stats.creator_points}"


def _read_stats(reader: Reader) -> PlayerStats:
    return PlayerStats(
        stars=reader.integer("3", default=0),
        moons=reader.integer("52", default=0),
        demons=reader.integer("4", default=0),
        creator_points=reader.integer("8", default=0),
    )


def _flag(value: bool) -> str:
    return "1" if value else ""


def serialise_friend_request(request: FriendRequest) -> str:
    return (
        f"{serialise_player(request.player)}:{_serialise_stats(request.stats)}"
        f":32:{request.id}:35:{encode_text(request.message)}"
        f":41:{_flag(request.is_new)}:37:{request.age}"
    )


def parse_friend_request(text: str) -> ParseResult[FriendRequest]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    message = decode_text(values.get("35", ""))

    if message is None:
        return ParseError.INVALID_BASE64

    reader = Reader(values)

    return reader.done(
        FriendRequest(
            id=reader.integer("32"),
            player=read_player(reader),
            message=message,
            age=reader.string("37", default=""),
            is_new=reader.boolean("41"),
            stats=_read_stats(reader),
        )
    )


def serialise_message(message: Message) -> str:
    peer = message.peer

    text = (
        f"6:{strip_separators(peer.name)}:3:{peer.user_id}:2:{peer.account_id}"
        f":1:{message.id}:4:{encode_text(message.subject)}:8:{message.read:d}"
        f":9:{message.outgoing:d}"
    )

    if message.body is not None:
        text += f":5:{encode_xor_text(message.body, KEY_MESSAGE)}"

    return f"{text}:7:{message.age}"


def parse_message(text: str) -> ParseResult[Message]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    subject = decode_text(values.get("4", ""))

    if subject is None:
        return ParseError.INVALID_BASE64

    body = None

    if "5" in values:
        body = decode_xor_text(values["5"], KEY_MESSAGE)

        if body is None:
            return ParseError.INVALID_BASE64

    reader = Reader(values)

    return reader.done(
        Message(
            id=reader.integer("1"),
            peer=UserRef(
                user_id=reader.integer("3", default=0),
                account_id=reader.integer("2", default=0),
                name=reader.string("6", default=""),
            ),
            subject=subject,
            age=reader.string("7", default=""),
            read=reader.boolean("8"),
            outgoing=reader.boolean("9"),
            body=body,
        )
    )


def serialise_user_list_entry(entry: UserListEntry) -> str:
    return (
        f"{serialise_player(entry.player)}:{_serialise_stats(entry.stats)}"
        f":18:{entry.message_state:d}:62:{entry.ship_fire}:63:{entry.extra}"
        f":41:{_flag(entry.is_new)}:64:{entry.extra2}"
    )


def parse_user_list_entry(text: str) -> ParseResult[UserListEntry]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)

    return reader.done(
        UserListEntry(
            player=read_player(reader),
            is_new=reader.boolean("41"),
            stats=_read_stats(reader),
            message_state=reader.member("18", MessageState, default=MessageState.ALL),
            ship_fire=reader.integer("62", default=0),
            extra=reader.integer("63", default=2),
            extra2=reader.integer("64", default=0),
        )
    )
