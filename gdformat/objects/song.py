from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.encoding import quote_url
from gdformat.encoding import strip_separators
from gdformat.encoding import unquote_url
from gdformat.enums import NewBadge
from gdformat.enums import Nong

SONG_SEPARATOR = "~|~"
SONG_LIST_SEPARATOR = "~:~"


@dataclass(frozen=True, slots=True)
class Artist:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Song:
    id: int
    name: str
    artist_id: int
    artist_name: str
    size_mb: float
    url: str
    video_id: str = ""
    youtube_channel: str = ""
    scouted: bool = False
    priority: int = 0
    nong: Nong = Nong.NONE
    extra_artists: tuple[Artist, ...] = ()
    is_new: bool = False
    new_badge: NewBadge = NewBadge.YELLOW
    soundtrack_url: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class TopArtist:
    name: str
    youtube_channel: str = ""


def serialise_artists(artists: tuple[Artist, ...]) -> str:
    return ",".join(
        f"{artist.id},{strip_separators(artist.name)}" for artist in artists
    )


def parse_artists(text: str) -> ParseResult[tuple[Artist, ...]]:
    if not text:
        return ()

    parts = text.split(",")

    if len(parts) % 2:
        return ParseError.INVALID_LAYOUT

    try:
        return tuple(
            Artist(int(artist_id), name)
            for artist_id, name in zip(parts[::2], parts[1::2], strict=True)
        )
    except ValueError:
        return ParseError.INVALID_INTEGER


def serialise_song(song: Song, *, include_artist_names: bool = True) -> str:
    separator = SONG_SEPARATOR
    artist_ids = ".".join(str(artist.id) for artist in song.extra_artists)
    size = f"{round(song.size_mb, 2):g}"

    text = (
        f"1{separator}{song.id}{separator}2{separator}{strip_separators(song.name)}"
        f"{separator}3{separator}{song.artist_id}{separator}4{separator}"
        f"{strip_separators(song.artist_name)}{separator}5{separator}{size}"
        f"{separator}6{separator}{song.video_id}{separator}7{separator}"
        f"{song.youtube_channel}{separator}8{separator}{song.scouted:d}{separator}9"
        f"{separator}{song.priority}{separator}10{separator}{quote_url(song.url)}"
        f"{separator}11{separator}{song.nong:d}{separator}12{separator}{artist_ids}"
        f"{separator}13{separator}{song.is_new:d}{separator}14{separator}"
        f"{song.new_badge:d}{separator}16{separator}{song.soundtrack_url}"
    )

    if include_artist_names:
        text += f"{separator}15{separator}{serialise_artists(song.extra_artists)}"

    return text


def parse_song(text: str) -> ParseResult[Song]:
    values = pairs(text, SONG_SEPARATOR)

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)
    extra_artists = parse_artists(reader.string("15", default=""))

    if isinstance(extra_artists, ParseError):
        return extra_artists

    if not extra_artists:
        extra_artists = tuple(
            Artist(artist_id, "") for artist_id in reader.integers("12", separator=".")
        )

    size = reader.string("5", default="0")

    try:
        size_mb = float(size)
    except ValueError:
        return ParseError.INVALID_VALUE

    return reader.done(
        Song(
            id=reader.integer("1"),
            name=reader.string("2", default=""),
            artist_id=reader.integer("3", default=0),
            artist_name=reader.string("4", default=""),
            size_mb=size_mb,
            url=unquote_url(reader.string("10", default="")),
            video_id=reader.string("6", default=""),
            youtube_channel=reader.string("7", default=""),
            scouted=reader.boolean("8"),
            priority=reader.integer("9", default=0),
            nong=reader.member("11", Nong, default=Nong.NONE),
            extra_artists=extra_artists,
            is_new=reader.boolean("13"),
            new_badge=reader.member("14", NewBadge, default=NewBadge.YELLOW),
            soundtrack_url=reader.string("16", default=""),
        )
    )


def serialise_top_artist(artist: TopArtist) -> str:
    text = f"4:{strip_separators(artist.name)}"

    if artist.youtube_channel:
        text += f":7:{artist.youtube_channel}"

    return text


def parse_top_artist(text: str) -> ParseResult[TopArtist]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)

    return reader.done(
        TopArtist(
            name=reader.string("4"),
            youtube_channel=reader.string("7", default=""),
        )
    )
