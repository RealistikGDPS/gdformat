from dataclasses import dataclass

from gdformat._common import Form
from gdformat._wire import Reader
from gdformat.enums import Platform


@dataclass(frozen=True, slots=True, kw_only=True)
class Auth:
    account_id: int
    gjp2: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Client:
    """Parameters every request carries about the sending game client."""

    game_version: int = 0
    binary_version: int = 0
    udid: str = ""
    user_id: int = 0
    platform: Platform = Platform.UNKNOWN
    secret: str = ""


def read_client(reader: Reader) -> Client:
    return Client(
        game_version=reader.integer("gameVersion", default=0),
        binary_version=reader.integer("binaryVersion", default=0),
        udid=reader.string("udid", default=""),
        user_id=reader.integer("uuid", default=0),
        platform=reader.member("dvs", Platform, default=Platform.UNKNOWN),
        secret=reader.string("secret", default=""),
    )


def read_auth(reader: Reader) -> Auth:
    return Auth(account_id=reader.integer("accountID"), gjp2=reader.string("gjp2"))


def read_optional_auth(reader: Reader) -> Auth | None:
    if not reader.has("accountID") or not reader.has("gjp2"):
        return None

    return read_auth(reader)


def create_reader(form: Form) -> Reader:
    return Reader(form)
