from collections.abc import Sequence

from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.user import User
from gdformat.objects.user import UserPreview
from gdformat.objects.user import serialise_user
from gdformat.objects.user import serialise_user_preview


def serialise_profile(user: User) -> str:
    return serialise_user(user)


def serialise_user_search(users: Sequence[UserPreview], page: Page) -> str:
    return f"{'|'.join(map(serialise_user_preview, users))}#{serialise_page(page)}"


def serialise_leaderboard(
    users: Sequence[UserPreview],
    *,
    viewer_account_id: int | None = None,
) -> str:
    return "|".join(
        serialise_user_preview(user, highlight=user.account_id == viewer_account_id)
        for user in users
    )
