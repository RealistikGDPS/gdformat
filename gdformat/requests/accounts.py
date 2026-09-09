from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.enums import CommentHistoryState
from gdformat.enums import FriendRequestState
from gdformat.enums import MessageState
from gdformat.objects.user import Privacy
from gdformat.objects.user import Socials
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRequest:
    client: Client
    name: str
    gjp2: str
    steam_id: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterRequest:
    client: Client
    name: str
    password: str
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BackupRequest:
    client: Client
    auth: Auth
    game_manager: str
    local_levels: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SyncRequest:
    client: Client
    auth: Auth


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateSettingsRequest:
    client: Client
    auth: Auth
    privacy: Privacy
    socials: Socials
    custom: str = ""


def parse_login(form: Form) -> ParseResult[LoginRequest]:
    reader = Reader(form)

    return reader.done(
        LoginRequest(
            client=read_client(reader),
            name=reader.string("userName"),
            gjp2=reader.string("gjp2"),
            steam_id=reader.string("sID", default=""),
        )
    )


def parse_register(form: Form) -> ParseResult[RegisterRequest]:
    reader = Reader(form)

    return reader.done(
        RegisterRequest(
            client=read_client(reader),
            name=reader.string("userName"),
            password=reader.string("password"),
            email=reader.string("email"),
        )
    )


def parse_backup(form: Form) -> ParseResult[BackupRequest]:
    reader = Reader(form)
    game_manager, separator, local_levels = reader.string("saveData").partition(";")

    if not separator:
        return ParseError.INVALID_LAYOUT

    return reader.done(
        BackupRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            game_manager=game_manager,
            local_levels=local_levels,
        )
    )


def parse_sync(form: Form) -> ParseResult[SyncRequest]:
    reader = Reader(form)

    return reader.done(SyncRequest(client=read_client(reader), auth=read_auth(reader)))


def parse_update_settings(form: Form) -> ParseResult[UpdateSettingsRequest]:
    reader = Reader(form)

    return reader.done(
        UpdateSettingsRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            privacy=Privacy(
                messages=reader.member("mS", MessageState, default=MessageState.ALL),
                friend_requests=reader.member(
                    "frS", FriendRequestState, default=FriendRequestState.ALL
                ),
                comment_history=reader.member(
                    "cS", CommentHistoryState, default=CommentHistoryState.ALL
                ),
            ),
            socials=Socials(
                youtube=reader.string("yt", default=""),
                twitter=reader.string("twitter", default=""),
                twitch=reader.string("twitch", default=""),
                discord=reader.string("discord", default=""),
                instagram=reader.string("instagram", default=""),
                tiktok=reader.string("tiktok", default=""),
            ),
            custom=reader.string("custom", default=""),
        )
    )
