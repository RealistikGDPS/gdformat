from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import list_seed
from gdformat.enums import DemonDifficulty
from gdformat.enums import Difficulty
from gdformat.enums import ListSearchType
from gdformat.enums import SearchDifficulty
from gdformat.enums import Visibility
from gdformat.objects._common import serialise_integers
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteListRequest:
    client: Client
    auth: Auth
    list_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ListSearchRequest:
    client: Client
    auth: Auth | None
    search_type: ListSearchType
    query: str = ""
    page: int = 0
    difficulty: SearchDifficulty | None = None
    demon_filter: DemonDifficulty | None = None
    rated: bool = False
    followed_account_ids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadListRequest:
    """`list_id` is 0 for a new list."""

    client: Client
    auth: Auth
    list_id: int
    name: str
    description: str
    level_ids: tuple[int, ...]
    difficulty: Difficulty
    seed: str
    seed2: str
    version: int = 0
    original_id: int = 0
    visibility: Visibility = Visibility.PUBLIC


def parse_delete_list(form: Form) -> ParseResult[DeleteListRequest]:
    reader = Reader(form)

    return reader.done(
        DeleteListRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            list_id=reader.integer("listID"),
        )
    )


def parse_list_search(form: Form) -> ParseResult[ListSearchRequest]:
    reader = Reader(form)
    difficulties = reader.members("diff", SearchDifficulty)

    return reader.done(
        ListSearchRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            search_type=reader.member(
                "type", ListSearchType, default=ListSearchType.MOST_LIKED
            ),
            query=reader.string("str", default=""),
            page=reader.integer("page", default=0),
            difficulty=difficulties[0] if difficulties else None,
            demon_filter=reader.optional_member("demonFilter", DemonDifficulty),
            rated=reader.boolean("star"),
            followed_account_ids=reader.integers("followed"),
        )
    )


def parse_upload_list(form: Form) -> ParseResult[UploadListRequest]:
    reader = Reader(form)

    return reader.done(
        UploadListRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            list_id=reader.integer("listID", default=0),
            name=reader.string("listName"),
            description=reader.text("listDesc", default=""),
            level_ids=reader.integers("listLevels"),
            difficulty=reader.member("difficulty", Difficulty, default=Difficulty.NA),
            seed=reader.string("seed", default=""),
            seed2=reader.string("seed2", default=""),
            version=reader.integer("listVersion", default=0),
            original_id=reader.integer("original", default=0),
            visibility=reader.member("unlisted", Visibility, default=Visibility.PUBLIC),
        )
    )


def verify_list_seed(request: UploadListRequest) -> bool:
    expected = list_seed(
        serialise_integers(request.level_ids), request.auth.account_id, request.seed2
    )

    return expected == request.seed
