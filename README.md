# gdformat

Parser and builder for the Geometry Dash 2.2 server protocol. It covers the
`key:value` wire objects, the full endpoint response envelopes (page info,
integrity hashes, reward blobs) and typed parsing of every endpoint's form
parameters, so a server never handles the raw format itself.

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

## Verification

The library was checked against the official servers on `boomlings.com`, both
unauthenticated and with a throwaway account:

- Every response object parses, round-trips, and re-serialises to the same
  values the server sends (key order aside): levels, downloads, profiles, user
  search, all leaderboard types, comments, comment history, songs, top artists,
  map packs, gauntlets, lists, friend requests, messages, and user lists.
- The recomputed level search, download, map pack, gauntlet, weekly and event
  hashes equal the server's, and the reward, quest and event blobs rebuild
  exactly.
- The client integrity values were proven by the server rejecting a wrong value
  and accepting the library's: level upload `seed2`, list upload `seed`, level
  comment `chk`, like `chk`, and stats `seed2`. The account comment and level
  leaderboard `chk` values are not validated by the official server.

Not verified: the daily level (none was being served), the download `chk`
(download counters lag too much to observe), and account backup and sync.

## Notes on the format

- `Difficulty` is one enum; the five wire keys that encode it (8, 9, 17, 25, 43)
  are derived on serialisation and folded back on parsing.
- Level copy passwords are `None` (no copy), `""` (free copy) or the digit
  string. The wire form and XOR encoding are handled internally. The download
  hash uses the plain wire number; the normalisation the documentation describes
  does not match the official server.
- Text fields (descriptions, comments, messages, subjects) are plain `str`; base64
  and XOR happen at the boundary. Free-text names are stripped of the separator
  characters `:|#~` when serialised.
- `LevelScoresRequest` exposes the obfuscated `sN` parameters with their offsets
  removed.
- The download response has three segments unless the level carries song lists,
  in which case the official server appends an empty creator segment, the songs
  and the extra artist names. `serialise_level_download` mirrors this.
- Profile keys 62 and 63 are undocumented; they are exposed as
  `IconSet.ship_fire` and `IconSet.extra`.
- The `legendary` and `mythic` search parameters are swapped by the client; the
  request model names them by their meaning.
