from enum import IntEnum

SUCCESS = "1"
FAILURE = "-1"


class LoginError(IntEnum):
    GENERIC = -1
    PASSWORD_TOO_SHORT = -8
    NAME_TOO_SHORT = -9
    LINKED_TO_OTHER_ACCOUNT = -10
    WRONG_CREDENTIALS = -11
    ACCOUNT_DISABLED = -12
    LINKED_TO_OTHER_STEAM = -13


class RegisterError(IntEnum):
    GENERIC = -1
    NAME_TAKEN = -2
    EMAIL_TAKEN = -3
    NAME_INVALID = -4
    PASSWORD_INVALID = -5
    EMAIL_INVALID = -6
    PASSWORD_TOO_SHORT = -8
    NAME_TOO_SHORT = -9


class SaveError(IntEnum):
    GENERIC = -1
    LOGIN_FAILED = -2
    GENERIC_VISIBLE = -3
    TOO_LARGE = -4
    BAD_LOGIN = -5
    SERVER_ERROR = -6


class SongError(IntEnum):
    NOT_FOUND = -1
    NOT_ALLOWED = -2


class CommentError(IntEnum):
    REJECTED = -1
    NONE_FOUND = -2
    PERMANENT_BAN = -10


class ListUploadError(IntEnum):
    REJECTED = -1
    BAD_SEED = -10


class ModeratorError(IntEnum):
    REJECTED = -1
    NOT_MODERATOR = -2


def serialise_code(code: int) -> str:
    return str(int(code))
