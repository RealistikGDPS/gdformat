from collections.abc import Sequence

from gdformat.crypto import gauntlet_hash
from gdformat.crypto import map_pack_hash
from gdformat.objects._common import Page
from gdformat.objects._common import serialise_integers
from gdformat.objects._common import serialise_page
from gdformat.objects.pack import Gauntlet
from gdformat.objects.pack import MapPack
from gdformat.objects.pack import serialise_gauntlet
from gdformat.objects.pack import serialise_map_pack


def serialise_map_packs(packs: Sequence[MapPack], page: Page) -> str:
    integrity = map_pack_hash((pack.id, pack.stars, pack.coins) for pack in packs)

    return (
        f"{'|'.join(map(serialise_map_pack, packs))}#{serialise_page(page)}#{integrity}"
    )


def serialise_gauntlets(gauntlets: Sequence[Gauntlet]) -> str:
    integrity = gauntlet_hash(
        (gauntlet.id, serialise_integers(gauntlet.level_ids)) for gauntlet in gauntlets
    )

    return f"{'|'.join(map(serialise_gauntlet, gauntlets))}#{integrity}"
