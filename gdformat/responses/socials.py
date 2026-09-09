from collections.abc import Sequence

from gdformat.objects._common import Page
from gdformat.objects._common import serialise_page
from gdformat.objects.social import FriendRequest
from gdformat.objects.social import Message
from gdformat.objects.social import UserListEntry
from gdformat.objects.social import serialise_friend_request
from gdformat.objects.social import serialise_message
from gdformat.objects.social import serialise_user_list_entry

NO_ENTRIES = "-2"


def serialise_friend_requests(requests: Sequence[FriendRequest], page: Page) -> str:
    return f"{'|'.join(map(serialise_friend_request, requests))}#{serialise_page(page)}"


def serialise_messages(messages: Sequence[Message], page: Page) -> str:
    return f"{'|'.join(map(serialise_message, messages))}#{serialise_page(page)}"


def serialise_message_download(message: Message) -> str:
    return serialise_message(message)


def serialise_user_list(entries: Sequence[UserListEntry]) -> str:
    return "|".join(map(serialise_user_list_entry, entries))
