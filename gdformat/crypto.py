import hashlib
from collections.abc import Iterable

from gdformat.encoding import cyclic_xor
from gdformat.encoding import decode_base64
from gdformat.encoding import encode_base64
from gdformat.encoding import encode_xor_text

KEY_MESSAGE = b"14251"
KEY_VAULT = b"19283"
KEY_CHALLENGES = b"19847"
KEY_LEVEL_PASSWORD = b"26364"
KEY_COMMENT = b"29481"
KEY_ACCOUNT_PASSWORD = b"37526"
KEY_LEVEL_LEADERBOARD = b"39673"
KEY_LEVEL = b"41274"
KEY_LOAD = b"48291"
KEY_LIBRARY = b"57709"
KEY_RATING = b"58281"
KEY_CHESTS = b"59182"
KEY_STATS = b"85271"

SALT_LEVEL = "xI25fpAapCQg"
SALT_COMMENT = "xPT6iUrtws0J"
SALT_LIKE = "ysg6pUrtjn0J"
SALT_PROFILE = "xI35fsAapCRg"
SALT_LEVEL_LEADERBOARD = "yPg6pUrtWn0J"
SALT_VAULT = "ask2fpcaqCQ2"
SALT_CHALLENGES = "oC36fpYaPtdg"
SALT_REWARDS = "pC26fpYaQCtg"
SALT_GJP2 = "mI29fmAnxgTs"

_SEED_SAMPLE_SIZE = 50
_DOWNLOAD_SAMPLE_SIZE = 40


def sha1_hex(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()


def gjp2(password: str) -> str:
    return sha1_hex(password + SALT_GJP2)


def chk(values: Iterable[object], key: bytes, salt: str) -> str:
    joined = "".join(map(str, values)) + salt

    return encode_base64(cyclic_xor(sha1_hex(joined).encode(), key))


def sample(data: str, count: int) -> str:
    if len(data) < count:
        return data

    return data[:: len(data) // count][:count]


def comment_chk(
    username: str,
    content: str,
    level_id: int,
    percent: int,
    comment_type: int,
) -> str:
    """`content` is the URL-safe base64 form of the comment, as sent on the wire."""

    return chk(
        (username, content, level_id, percent, comment_type), KEY_COMMENT, SALT_COMMENT
    )


def like_chk(
    special: int,
    item_id: int,
    like: bool,
    like_type: int,
    rs: str,
    account_id: int,
    udid: str,
    user_id: int,
) -> str:
    return chk(
        (special, item_id, int(like), like_type, rs, account_id, udid, user_id),
        KEY_RATING,
        SALT_LIKE,
    )


def rate_chk(
    level_id: int,
    stars: int,
    rs: str,
    account_id: int,
    udid: str,
    user_id: int,
) -> str:
    return chk((level_id, stars, rs, account_id, udid, user_id), KEY_RATING, SALT_LIKE)


def download_chk(
    level_id: int,
    increment: bool,
    rs: str,
    account_id: int,
    udid: str,
    user_id: int,
) -> str:
    # NOTE: The documentation lists no salt for this value; this follows it as written.
    return chk((level_id, int(increment), rs, account_id, udid, user_id), KEY_LEVEL, "")


def profile_chk(values: Iterable[object]) -> str:
    return chk(values, KEY_STATS, SALT_PROFILE)


def level_leaderboard_chk(values: Iterable[object], rs: str) -> str:
    return chk((*values, SALT_LEVEL_LEADERBOARD, rs), KEY_LEVEL_LEADERBOARD, "")


def level_seed(level_string: str) -> str:
    """The `seed2` parameter of a level upload."""

    sampled = sample(level_string, _SEED_SAMPLE_SIZE)

    return encode_base64(cyclic_xor(sha1_hex(sampled + SALT_LEVEL).encode(), KEY_LEVEL))


def list_seed(level_ids: str, account_id: int, seed2: str) -> str:
    """The `seed` parameter of a list upload; `seed2` is the random key it was
    encrypted with."""

    sampled = sample(level_ids, _SEED_SAMPLE_SIZE)
    digest = sha1_hex(f"{sampled}{account_id}")

    return encode_base64(cyclic_xor(digest.encode(), seed2.encode()))


def level_download_hash(level_string: str) -> str:
    if len(level_string) <= _DOWNLOAD_SAMPLE_SIZE:
        return sha1_hex(level_string + SALT_LEVEL)

    step = len(level_string) // _DOWNLOAD_SAMPLE_SIZE

    sampled = "".join(
        level_string[index * step] for index in range(_DOWNLOAD_SAMPLE_SIZE)
    )

    return sha1_hex(sampled + SALT_LEVEL)


def level_metadata_hash(
    creator_id: int,
    stars: int,
    is_demon: bool,
    level_id: int,
    verified_coins: bool,
    feature_score: int,
    password: int,
    timely_id: int,
) -> str:
    joined = (
        f"{creator_id},{stars},{is_demon:d},{level_id},{verified_coins:d},"
        f"{feature_score},{password},{timely_id}"
    )

    return sha1_hex(joined + SALT_LEVEL)


def level_search_hash(levels: Iterable[tuple[int, int, bool]]) -> str:
    """`levels` yields `(level_id, stars, verified_coins)` per level, in order."""

    parts = []

    for level_id, stars, verified_coins in levels:
        digits = str(level_id)
        parts.append(f"{digits[0]}{digits[-1]}{stars}{verified_coins:d}")

    return sha1_hex("".join(parts) + SALT_LEVEL)


def map_pack_hash(packs: Iterable[tuple[int, int, int]]) -> str:
    """`packs` yields `(pack_id, stars, coins)` per pack, in order."""

    parts = []

    for pack_id, stars, coins in packs:
        digits = str(pack_id)
        parts.append(f"{digits[0]}{digits[-1]}{stars}{coins}")

    return sha1_hex("".join(parts) + SALT_LEVEL)


def gauntlet_hash(gauntlets: Iterable[tuple[int, str]]) -> str:
    """`gauntlets` yields `(gauntlet_id, comma_separated_level_ids)`, in order."""

    joined = "".join(
        f"{gauntlet_id}{level_ids}" for gauntlet_id, level_ids in gauntlets
    )

    return sha1_hex(joined + SALT_LEVEL)


def challenges_hash(blob: str) -> str:
    return sha1_hex(blob + SALT_CHALLENGES)


def rewards_hash(blob: str) -> str:
    return sha1_hex(blob + SALT_REWARDS)


LEVEL_LIST_HASH = sha1_hex(SALT_LEVEL)


def level_password_wire(password: str | None) -> str:
    """The plain-text form of a copy password: `0` no copy, `1` free copy, else
    `1` followed by the digits."""

    if password is None:
        return "0"

    return f"1{password}"


def level_password_from_wire(wire: str) -> str | None:
    if wire in ("", "0"):
        return None

    return wire[1:]


def level_password_number(password: str | None) -> int:
    """The numeric form used by the download hash: the plain wire value as an
    integer. Verified against the official server for 4 and 6 digit passwords;
    the documented 1,000,000 normalisation is not applied there."""

    return int(level_password_wire(password))


def encode_level_password(password: str | None) -> str:
    if password is None:
        return "0"

    return encode_xor_text(level_password_wire(password), KEY_LEVEL_PASSWORD)


def decode_level_password(encoded: str) -> str | None:
    if encoded in ("", "0"):
        return None

    raw = decode_base64(encoded)

    if raw is None:
        return None

    return level_password_from_wire(
        cyclic_xor(raw, KEY_LEVEL_PASSWORD).decode("ascii", "replace")
    )


def decode_reward_chk(value: str, key: bytes) -> int | None:
    """Recovers the client's challenge number from a rewards `chk` parameter."""

    raw = decode_base64(value[5:])

    if raw is None:
        return None

    number = cyclic_xor(raw, key).decode("ascii", "replace")

    if not number.isdecimal():
        return None

    return int(number)


def encode_reward_blob(plaintext: str, key: bytes) -> str:
    return encode_base64(cyclic_xor(plaintext.encode(), key))


def classic_leaderboard_seed(clicks: int, percentage: int, seconds: int) -> int:
    return (
        1482 * 2
        + (clicks + 3991) * (percentage + 8354)
        + (seconds + 4085) ** 2
        - 50028039
    )


def platformer_leaderboard_hash(best_time: int, best_points: int) -> int:
    number = (
        ((best_time + 7890) % 34567) * 601
        + ((abs(best_points) + 3456) % 78901) * 967
        + 94819
    ) % 94433

    return ((number ^ (number >> 16)) * 829) % 77849
