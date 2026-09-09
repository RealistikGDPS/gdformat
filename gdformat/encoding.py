import base64
import binascii
import gzip
import random
import string
import urllib.parse
import zlib

_ALPHABET = string.ascii_letters + string.digits
_SEPARATOR_TABLE = str.maketrans("", "", ":|#~")
_AGE_UNITS = (
    (31_536_000, "year"),
    (2_592_000, "month"),
    (604_800, "week"),
    (86_400, "day"),
    (3_600, "hour"),
    (60, "minute"),
    (1, "second"),
)


def cyclic_xor(data: bytes, key: bytes) -> bytes:
    length = len(data)

    if length == 0:
        return b""

    repeated = (key * (length // len(key) + 1))[:length]
    mixed = int.from_bytes(data, "big") ^ int.from_bytes(repeated, "big")

    return mixed.to_bytes(length, "big")


def encode_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def decode_base64(text: str) -> bytes | None:
    padded = text + "=" * (-len(text) % 4)

    try:
        return base64.urlsafe_b64decode(padded)
    except binascii.Error:
        return None


def encode_text(text: str) -> str:
    return encode_base64(text.encode())


def decode_text(text: str) -> str | None:
    raw = decode_base64(text)

    if raw is None:
        return None

    return raw.decode("utf-8", "replace")


def encode_xor_text(text: str, key: bytes) -> str:
    return encode_base64(cyclic_xor(text.encode(), key))


def decode_xor_text(text: str, key: bytes) -> str | None:
    raw = decode_base64(text)

    if raw is None:
        return None

    return cyclic_xor(raw, key).decode("utf-8", "replace")


def compress_level(level: str) -> str:
    return encode_base64(gzip.compress(level.encode(), mtime=0))


def decompress_level(data: str) -> str | None:
    raw = decode_base64(data)

    if raw is None:
        return None

    try:
        return zlib.decompress(raw, 15 | 32).decode("utf-8", "replace")
    except zlib.error:
        return None


def deflate_base64(text: str) -> str:
    return encode_base64(zlib.compress(text.encode()))


def quote_url(url: str) -> str:
    return urllib.parse.quote(url, safe="")


def unquote_url(url: str) -> str:
    return urllib.parse.unquote(url)


def random_string(length: int) -> str:
    return "".join(random.choices(_ALPHABET, k=length))


def strip_separators(text: str) -> str:
    return text.translate(_SEPARATOR_TABLE)


def describe_age(seconds: int) -> str:
    """Formats a duration the way the official servers do: `3 months`, `1 second`."""

    elapsed = max(seconds, 1)

    for unit, name in _AGE_UNITS:
        if elapsed < unit:
            continue

        count = elapsed // unit

        return f"{count} {name}" if count == 1 else f"{count} {name}s"

    return "1 second"
