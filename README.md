# gdformat

Parser and builder for the Geometry Dash 2.2 server protocol. It covers the
wire objects, the full endpoint response envelopes and typed parsing of every
endpoint's form parameters, so a server never handles the raw format itself.

Only the latest game version is supported. Python 3.14, managed with uv, no
runtime dependencies.

## Layout

| Module | Contents |
|--------|----------|
| `gdformat.objects` | Frozen dataclasses for each wire object (`Level`, `User`, `Comment`, `Song`, ...) with `serialise_*` / `parse_*` functions. |
| `gdformat.responses` | One `serialise_*` per endpoint response, producing the exact string to send. |
| `gdformat.requests` | One `*Request` dataclass and `parse_*` per endpoint, taking the POST form. `verify_*` helpers check the client integrity values. |
| `gdformat.crypto` | XOR keys and salts, `gjp2`, `chk` generation, response hashes, level passwords, leaderboard seeds. |
| `gdformat.encoding` | Base64, XOR, level string compression, URL quoting, relative age strings. |
| `gdformat.enums` | Every discriminant the protocol uses. |
| `gdformat.codes` | Documented numeric response codes. |

## Usage

```python
from gdformat import is_error, objects, requests, responses

def download_level(form: dict[str, str]) -> str:
    request = requests.parse_download_level(form)
    if is_error(request):
        return "-1"

    level = objects.Level(...)  # Built from your storage.
    return responses.serialise_level_download(level, songs)
```

Failures are values: every parser returns `T | ParseError`, narrowed with
`is_error` / `is_success`. Nothing in the library raises.
