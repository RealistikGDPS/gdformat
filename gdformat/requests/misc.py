from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import like_chk
from gdformat.enums import AccountUrlType
from gdformat.enums import LikeType
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountUrlRequest:
    client: Client
    account_id: int
    url_type: AccountUrlType


@dataclass(frozen=True, slots=True, kw_only=True)
class LikeRequest:
    """`special` is 0 for levels and lists, the (negative for lists) level ID for
    level comments and the account ID for account comments."""

    client: Client
    auth: Auth | None
    item_id: int
    item_type: LikeType
    like: bool = True
    special: int = 0
    rs: str = ""
    chk: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ModAccessRequest:
    client: Client
    auth: Auth


def parse_account_url(form: Form) -> ParseResult[AccountUrlRequest]:
    reader = Reader(form)

    return reader.done(
        AccountUrlRequest(
            client=read_client(reader),
            account_id=reader.integer("accountID", default=0),
            url_type=reader.member("type", AccountUrlType),
        )
    )


def parse_like(form: Form) -> ParseResult[LikeRequest]:
    reader = Reader(form)

    return reader.done(
        LikeRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            item_id=reader.integer("itemID"),
            item_type=reader.member("type", LikeType),
            like=reader.boolean("like", default=True),
            special=reader.integer("special", default=0),
            rs=reader.string("rs", default=""),
            chk=reader.string("chk", default=""),
        )
    )


def verify_like_chk(request: LikeRequest) -> bool:
    if request.auth is None:
        return False

    expected = like_chk(
        request.special,
        request.item_id,
        request.like,
        request.item_type,
        request.rs,
        request.auth.account_id,
        request.client.udid,
        request.client.user_id,
    )

    return expected == request.chk


def parse_mod_access(form: Form) -> ParseResult[ModAccessRequest]:
    reader = Reader(form)

    return reader.done(
        ModAccessRequest(client=read_client(reader), auth=read_auth(reader))
    )
