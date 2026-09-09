from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import comment_chk
from gdformat.encoding import encode_text
from gdformat.enums import CommentMode
from gdformat.enums import CommentType
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth

_DEFAULT_COUNT = 10


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteAccountCommentRequest:
    client: Client
    auth: Auth
    comment_id: int
    target_account_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteCommentRequest:
    client: Client
    auth: Auth
    comment_id: int
    level_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountCommentsRequest:
    client: Client
    auth: Auth | None
    account_id: int
    page: int
    total: int = 0
    count: int = _DEFAULT_COUNT


@dataclass(frozen=True, slots=True, kw_only=True)
class CommentHistoryRequest:
    client: Client
    auth: Auth | None
    user_id: int
    page: int
    mode: CommentMode = CommentMode.RECENT
    total: int = 0
    count: int = _DEFAULT_COUNT


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelCommentsRequest:
    """`level_id` is negative when the comments belong to a list."""

    client: Client
    auth: Auth | None
    level_id: int
    page: int
    mode: CommentMode = CommentMode.RECENT
    total: int = 0
    count: int = _DEFAULT_COUNT


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadAccountCommentRequest:
    client: Client
    auth: Auth
    content: str
    name: str = ""
    chk: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadCommentRequest:
    """`level_id` is negative when commenting on a list."""

    client: Client
    auth: Auth
    name: str
    content: str
    level_id: int
    chk: str
    percent: int = 0


def parse_delete_account_comment(
    form: Form,
) -> ParseResult[DeleteAccountCommentRequest]:
    reader = Reader(form)

    return reader.done(
        DeleteAccountCommentRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            comment_id=reader.integer("commentID"),
            target_account_id=reader.integer("targetAccountID"),
        )
    )


def parse_delete_comment(form: Form) -> ParseResult[DeleteCommentRequest]:
    reader = Reader(form)

    return reader.done(
        DeleteCommentRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            comment_id=reader.integer("commentID"),
            level_id=reader.integer("levelID"),
        )
    )


def parse_account_comments(form: Form) -> ParseResult[AccountCommentsRequest]:
    reader = Reader(form)

    return reader.done(
        AccountCommentsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            account_id=reader.integer("accountID"),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
            count=reader.integer("count", default=_DEFAULT_COUNT),
        )
    )


def parse_comment_history(form: Form) -> ParseResult[CommentHistoryRequest]:
    reader = Reader(form)

    return reader.done(
        CommentHistoryRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            user_id=reader.integer("userID"),
            page=reader.integer("page", default=0),
            mode=reader.member("mode", CommentMode, default=CommentMode.RECENT),
            total=reader.integer("total", default=0),
            count=reader.integer("count", default=_DEFAULT_COUNT),
        )
    )


def parse_level_comments(form: Form) -> ParseResult[LevelCommentsRequest]:
    reader = Reader(form)

    return reader.done(
        LevelCommentsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            level_id=reader.integer("levelID"),
            page=reader.integer("page", default=0),
            mode=reader.member("mode", CommentMode, default=CommentMode.RECENT),
            total=reader.integer("total", default=0),
            count=reader.integer("count", default=_DEFAULT_COUNT),
        )
    )


def parse_upload_account_comment(
    form: Form,
) -> ParseResult[UploadAccountCommentRequest]:
    reader = Reader(form)

    return reader.done(
        UploadAccountCommentRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            content=reader.text("comment"),
            name=reader.string("userName", default=""),
            chk=reader.string("chk", default=""),
        )
    )


def parse_upload_comment(form: Form) -> ParseResult[UploadCommentRequest]:
    reader = Reader(form)

    return reader.done(
        UploadCommentRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            name=reader.string("userName"),
            content=reader.text("comment"),
            level_id=reader.integer("levelID"),
            chk=reader.string("chk"),
            percent=reader.integer("percent", default=0),
        )
    )


def verify_comment_chk(request: UploadCommentRequest) -> bool:
    expected = comment_chk(
        request.name,
        encode_text(request.content),
        request.level_id,
        request.percent,
        CommentType.LEVEL,
    )

    return expected == request.chk


def verify_account_comment_chk(request: UploadAccountCommentRequest) -> bool:
    expected = comment_chk(
        request.name, encode_text(request.content), 0, 0, CommentType.ACCOUNT
    )

    return expected == request.chk
