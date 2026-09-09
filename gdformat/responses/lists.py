from collections.abc import Sequence

from gdformat.crypto import LEVEL_LIST_HASH
from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.level_list import LevelList
from gdformat.objects.level_list import serialise_level_list
from gdformat.objects.user import UserRef
from gdformat.objects.user import serialise_user_ref


def serialise_list_search(
    lists: Sequence[LevelList],
    creators: Sequence[UserRef],
    page: Page,
) -> str:
    return (
        f"{'|'.join(map(serialise_level_list, lists))}"
        f"#{'|'.join(map(serialise_user_ref, creators))}#{serialise_page(page)}"
        f"#{LEVEL_LIST_HASH}"
    )
