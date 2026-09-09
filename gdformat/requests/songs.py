from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth


@dataclass(frozen=True, slots=True, kw_only=True)
class SongInfoRequest:
    client: Client
    auth: Auth | None
    song_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TopArtistsRequest:
    client: Client
    auth: Auth | None
    page: int = 0
    total: int = 0


def parse_song_info(form: Form) -> ParseResult[SongInfoRequest]:
    reader = Reader(form)

    return reader.done(
        SongInfoRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            song_id=reader.integer("songID"),
        )
    )


def parse_top_artists(form: Form) -> ParseResult[TopArtistsRequest]:
    reader = Reader(form)

    return reader.done(
        TopArtistsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
        )
    )
