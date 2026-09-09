from collections.abc import Sequence

from gdformat.encoding import deflate_base64
from gdformat.encoding import random_string
from gdformat.objects._common import serialise_integers
from gdformat.objects.pack import MapPack

_PADDING_LENGTH = 20
ACCOUNT_URL = "https://www.robtopgames.org"


def _padded_blob(text: str) -> str:
    return (
        f"{random_string(_PADDING_LENGTH)}{deflate_base64(text)}"
        f"{random_string(_PADDING_LENGTH)}"
    )


def serialise_login(account_id: int, user_id: int) -> str:
    return f"{account_id},{user_id}"


def serialise_sync(
    game_manager: str,
    local_levels: str,
    game_version: int,
    binary_version: int,
    rated_levels: Sequence[tuple[int, int]],
    map_packs: Sequence[MapPack],
) -> str:
    """`rated_levels` yields `(level_id, stars)` pairs."""

    rated = ",".join(f"{level_id},{stars}" for level_id, stars in rated_levels)

    packs = "|".join(
        f"1:{pack.id}:3:{serialise_integers(pack.level_ids)}:4:{pack.stars}:5:{pack.coins}"
        for pack in map_packs
    )

    return (
        f"{game_manager};{local_levels};{game_version};{binary_version}"
        f";{_padded_blob(rated)};{_padded_blob(packs)}"
    )
