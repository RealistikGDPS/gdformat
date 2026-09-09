from collections.abc import Sequence

from gdformat.crypto import KEY_CHESTS
from gdformat.crypto import encode_reward_blob
from gdformat.crypto import level_download_hash
from gdformat.crypto import level_metadata_hash
from gdformat.crypto import level_password_number
from gdformat.crypto import level_search_hash
from gdformat.crypto import rewards_hash
from gdformat.encoding import random_string
from gdformat.enums import ChestType
from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.level import Level
from gdformat.objects.level import LevelPreview
from gdformat.objects.level import serialise_level
from gdformat.objects.level import serialise_level_preview
from gdformat.objects.reward import RewardStack
from gdformat.objects.reward import serialise_reward_stacks
from gdformat.objects.score import LevelScore
from gdformat.objects.score import serialise_level_score
from gdformat.objects.song import SONG_LIST_SEPARATOR
from gdformat.objects.song import Artist
from gdformat.objects.song import Song
from gdformat.objects.song import serialise_artists
from gdformat.objects.song import serialise_song
from gdformat.objects.user import UserRef
from gdformat.objects.user import serialise_user_ref

_EVENT_SECONDS_LEFT = 10
_PREFIX_LENGTH = 5


def _extra_artists(songs: Sequence[Song]) -> tuple[Artist, ...]:
    seen: dict[int, Artist] = {}

    for song in songs:
        for artist in song.extra_artists:
            seen.setdefault(artist.id, artist)

    return tuple(seen.values())


def serialise_level_search(
    levels: Sequence[LevelPreview],
    creators: Sequence[UserRef],
    songs: Sequence[Song],
    page: Page,
) -> str:
    level_text = "|".join(map(serialise_level_preview, levels))
    creator_text = "|".join(map(serialise_user_ref, creators))
    song_text = SONG_LIST_SEPARATOR.join(map(serialise_song, songs))

    integrity = level_search_hash(
        (level.id, level.stars, level.verified_coins) for level in levels
    )

    return f"{level_text}#{creator_text}#{song_text}#{serialise_page(page)}#{integrity}"


def serialise_level_download(
    level: Level,
    songs: Sequence[Song] = (),
    *,
    creator: UserRef | None = None,
) -> str:
    """`creator` MUST be given for daily, weekly and event downloads. The official
    server appends the creator, song and artist segments only when the level
    carries song lists (or, for timely levels, a creator); this mirrors that."""

    metadata_hash = level_metadata_hash(
        level.creator_id,
        level.stars,
        level.difficulty.is_demon,
        level.id,
        level.verified_coins,
        level.feature_score,
        level_password_number(level.password),
        level.timely_id or 0,
    )

    text = (
        f"{serialise_level(level)}#{level_download_hash(level.level_string)}"
        f"#{metadata_hash}"
    )

    creator_text = "" if creator is None else serialise_user_ref(creator)

    if not songs:
        return text if creator is None else f"{text}#{creator_text}"

    song_text = SONG_LIST_SEPARATOR.join(
        serialise_song(song, include_artist_names=False) for song in songs
    )

    return (
        f"{text}#{creator_text}#{song_text}#{serialise_artists(_extra_artists(songs))}"
    )


def serialise_timely(timely_id: int, seconds_left: int) -> str:
    return f"{timely_id}|{seconds_left}"


def serialise_event(
    timely_id: int,
    chk: int,
    reward_id: int,
    chest_type: ChestType,
    rewards: tuple[RewardStack, ...],
    *,
    prefix: str | None = None,
) -> str:
    """Event level response; the reward segment mirrors getGJSecretReward."""

    prefix = random_string(_PREFIX_LENGTH) if prefix is None else prefix

    plaintext = (
        f"{prefix}:{chk}:{reward_id}:{chest_type:d}:{serialise_reward_stacks(rewards)}"
    )

    blob = encode_reward_blob(plaintext, KEY_CHESTS)

    return f"{timely_id}|{_EVENT_SECONDS_LEFT}|{prefix}{blob}|{rewards_hash(blob)}"


def serialise_level_scores(scores: Sequence[LevelScore]) -> str:
    return "|".join(map(serialise_level_score, scores))
