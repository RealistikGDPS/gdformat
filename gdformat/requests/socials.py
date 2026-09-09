from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import KEY_MESSAGE
from gdformat.encoding import decode_xor_text
from gdformat.enums import UserListType
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client


@dataclass(frozen=True, slots=True, kw_only=True)
class AcceptFriendRequest:
    client: Client
    auth: Auth
    target_account_id: int
    request_id: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class BlockRequest:
    client: Client
    auth: Auth
    target_account_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteFriendRequestsRequest:
    """`target_account_ids` holds every account whose request is declined."""

    client: Client
    auth: Auth
    target_account_ids: tuple[int, ...]
    is_sender: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteMessagesRequest:
    client: Client
    auth: Auth
    message_ids: tuple[int, ...]
    is_sender: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadMessageRequest:
    client: Client
    auth: Auth
    message_id: int
    is_sender: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class FriendRequestsRequest:
    client: Client
    auth: Auth
    page: int = 0
    total: int = 0
    sent: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class MessagesRequest:
    client: Client
    auth: Auth
    page: int = 0
    total: int = 0
    sent: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class UserListRequest:
    client: Client
    auth: Auth
    list_type: UserListType = UserListType.FRIENDS


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadFriendRequestRequest:
    client: Client
    auth: Auth
    request_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SendFriendRequestRequest:
    client: Client
    auth: Auth
    target_account_id: int
    message: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class SendMessageRequest:
    client: Client
    auth: Auth
    target_account_id: int
    subject: str
    body: str


def _target(reader: Reader) -> int:
    return reader.integer("targetAccountID")


def parse_accept_friend_request(form: Form) -> ParseResult[AcceptFriendRequest]:
    reader = Reader(form)

    return reader.done(
        AcceptFriendRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            target_account_id=_target(reader),
            request_id=reader.integer("requestID", default=0),
        )
    )


def parse_block(form: Form) -> ParseResult[BlockRequest]:
    reader = Reader(form)

    return reader.done(
        BlockRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            target_account_id=_target(reader),
        )
    )


def parse_delete_friend_requests(
    form: Form,
) -> ParseResult[DeleteFriendRequestsRequest]:
    reader = Reader(form)
    target = reader.integer("targetAccountID", default=0)
    targets = reader.integers("accounts") if target == 0 else (target,)

    return reader.done(
        DeleteFriendRequestsRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            target_account_ids=targets,
            is_sender=reader.boolean("isSender"),
        )
    )


def parse_delete_messages(form: Form) -> ParseResult[DeleteMessagesRequest]:
    reader = Reader(form)
    single = reader.optional_integer("messageID")
    message_ids = reader.integers("messages") if single is None else (single,)

    if not message_ids:
        return reader.error or ParseError.MISSING

    return reader.done(
        DeleteMessagesRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            message_ids=message_ids,
            is_sender=reader.boolean("isSender"),
        )
    )


def parse_download_message(form: Form) -> ParseResult[DownloadMessageRequest]:
    reader = Reader(form)

    return reader.done(
        DownloadMessageRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            message_id=reader.integer("messageID"),
            is_sender=reader.boolean("isSender"),
        )
    )


def parse_friend_requests(form: Form) -> ParseResult[FriendRequestsRequest]:
    reader = Reader(form)

    return reader.done(
        FriendRequestsRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
            sent=reader.boolean("getSent"),
        )
    )


def parse_messages(form: Form) -> ParseResult[MessagesRequest]:
    reader = Reader(form)

    return reader.done(
        MessagesRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
            sent=reader.boolean("getSent"),
        )
    )


def parse_user_list(form: Form) -> ParseResult[UserListRequest]:
    reader = Reader(form)

    return reader.done(
        UserListRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            list_type=reader.member("type", UserListType, default=UserListType.FRIENDS),
        )
    )


def parse_read_friend_request(form: Form) -> ParseResult[ReadFriendRequestRequest]:
    reader = Reader(form)

    return reader.done(
        ReadFriendRequestRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            request_id=reader.integer("requestID"),
        )
    )


def parse_send_friend_request(form: Form) -> ParseResult[SendFriendRequestRequest]:
    reader = Reader(form)

    return reader.done(
        SendFriendRequestRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            target_account_id=reader.integer("toAccountID"),
            message=reader.text("comment", default=""),
        )
    )


def parse_send_message(form: Form) -> ParseResult[SendMessageRequest]:
    reader = Reader(form)
    body = decode_xor_text(reader.string("body"), KEY_MESSAGE)

    if body is None:
        return reader.error or ParseError.INVALID_BASE64

    return reader.done(
        SendMessageRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            target_account_id=reader.integer("toAccountID"),
            subject=reader.text("subject", default=""),
            body=body,
        )
    )
