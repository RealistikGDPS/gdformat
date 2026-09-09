from collections.abc import Sequence

from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.song import Song
from gdformat.objects.song import TopArtist
from gdformat.objects.song import serialise_song
from gdformat.objects.song import serialise_top_artist

SONG_NOT_ALLOWED = "-2"
CUSTOM_CONTENT_URL = "https://geometrydashfiles.b-cdn.net"


def serialise_song_info(song: Song) -> str:
    return serialise_song(song)


def serialise_top_artists(artists: Sequence[TopArtist], page: Page) -> str:
    return f"{'|'.join(map(serialise_top_artist, artists))}#{serialise_page(page)}"
