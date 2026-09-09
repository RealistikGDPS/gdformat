from collections.abc import Sequence

from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.comment import AccountComment
from gdformat.objects.comment import Comment
from gdformat.objects.comment import serialise_account_comment
from gdformat.objects.comment import serialise_comment

PERMANENT_COMMENT_BAN = "-10"


def serialise_level_comments(comments: Sequence[Comment], page: Page) -> str:
    return f"{'|'.join(map(serialise_comment, comments))}#{serialise_page(page)}"


def serialise_account_comments(comments: Sequence[AccountComment], page: Page) -> str:
    return (
        f"{'|'.join(map(serialise_account_comment, comments))}#{serialise_page(page)}"
    )


def serialise_comment_ban(seconds_left: int, reason: str = "") -> str:
    if not reason:
        return f"temp_{seconds_left}"

    return f"temp_{seconds_left}_{reason.replace('_', ' ')}"
