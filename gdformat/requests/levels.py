from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import KEY_CHESTS
from gdformat.crypto import KEY_LEVEL
from gdformat.crypto import decode_reward_chk
from gdformat.crypto import level_password_from_wire
from gdformat.crypto import level_seed
from gdformat.crypto import rate_chk
from gdformat.encoding import decode_xor_text
from gdformat.enums import DemonDifficulty
from gdformat.enums import Length
from gdformat.enums import LevelScoreType
from gdformat.enums import PlatformerMode
from gdformat.enums import SearchDifficulty
from gdformat.enums import SearchType
from gdformat.enums import SendFeature
from gdformat.enums import TimelyType
from gdformat.enums import Visibility
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth

_ATTEMPTS_OFFSET = 8354
_CLICKS_OFFSET = 3991
_SECONDS_OFFSET = 4085
_COINS_OFFSET = 5819
_BEST_TICKS_OFFSET = 46533
_BEST_CLICKS_OFFSET = 7684
_BEST_COINS_OFFSET = 6433
_BEST_POINTS_TICKS_OFFSET = 25645
_BEST_POINTS_CLICKS_OFFSET = 3453
_BEST_POINTS_COINS_OFFSET = 6323


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteLevelRequest:
    client: Client
    auth: Auth
    level_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadLevelRequest:
    """`level_id` is -1, -2 or -3 for the daily, weekly and event level."""

    client: Client
    auth: Auth | None
    level_id: int
    increment_downloads: bool = False
    extras: bool = False
    rs: str = ""
    chk: str = ""

    @property
    def timely(self) -> TimelyType | None:
        if self.level_id >= 0:
            return None

        return TimelyType(-self.level_id - 1)


@dataclass(frozen=True, slots=True, kw_only=True)
class TimelyRequest:
    """`chk` is the decoded challenge number, present only for event levels."""

    client: Client
    auth: Auth | None
    timely_type: TimelyType
    chk: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GauntletsRequest:
    client: Client
    auth: Auth | None
    special: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelSearchRequest:
    """`gauntlet_id` is set when the client lists a gauntlet's levels; the
    search type and filters are then irrelevant."""

    client: Client
    auth: Auth | None
    search_type: SearchType
    query: str = ""
    page: int = 0
    total: int = 0
    difficulties: tuple[SearchDifficulty, ...] = ()
    demon_filter: DemonDifficulty | None = None
    lengths: tuple[Length, ...] = ()
    uncompleted: bool = False
    only_completed: bool = False
    completed_level_ids: tuple[int, ...] = ()
    featured: bool = False
    original: bool = False
    two_player: bool = False
    coins: bool = False
    epic: bool = False
    legendary: bool = False
    mythic: bool = False
    rated: bool = False
    unrated: bool = False
    song_id: int | None = None
    custom_song: bool = False
    followed_account_ids: tuple[int, ...] = ()
    local: bool = False
    gauntlet_id: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LevelScoresRequest:
    """Shared by getGJLevelScores211 and getGJLevelScoresPlat; the obfuscated
    `sN` fields are exposed with their offsets removed."""

    client: Client
    auth: Auth
    level_id: int
    score_type: LevelScoreType = LevelScoreType.FRIENDS
    platformer: bool = False
    mode: PlatformerMode = PlatformerMode.TIME
    percent: int | None = None
    time_ms: int = 0
    points: int = 0
    attempts: int = 0
    clicks: int = 0
    seconds: int = 0
    seed: int = 0
    progress: tuple[int, ...] = ()
    rs: str = ""
    attempt_count: int = 0
    coins: int = 0
    timely_id: int = 0
    best_ticks: int = 0
    best_clicks: int = 0
    best_coins: int = 0
    best_points_ticks: int = 0
    best_points_clicks: int = 0
    best_points_coins: int = 0
    level_version: int = 0
    chk: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class MapPacksRequest:
    client: Client
    auth: Auth | None
    page: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class RateDemonRequest:
    client: Client
    auth: Auth
    level_id: int
    rating: DemonDifficulty


@dataclass(frozen=True, slots=True, kw_only=True)
class RateStarsRequest:
    client: Client
    auth: Auth | None
    level_id: int
    stars: int
    rs: str = ""
    chk: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ReportLevelRequest:
    client: Client
    level_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SuggestStarsRequest:
    client: Client
    auth: Auth
    level_id: int
    stars: int
    feature: SendFeature


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateDescriptionRequest:
    client: Client
    auth: Auth
    level_id: int
    description: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadLevelRequest:
    """`level_id` is 0 for a new level. `level_string` stays in its compressed
    wire form; decode it with `encoding.decompress_level` when needed."""

    client: Client
    auth: Auth
    creator_name: str
    level_id: int
    name: str
    description: str
    version: int
    length: Length
    official_song: int
    custom_song_id: int
    level_string: str
    seed2: str
    password: str | None = None
    auto: bool = False
    original_id: int = 0
    two_player: bool = False
    objects: int = 0
    coins: int = 0
    requested_stars: int = 0
    visibility: Visibility = Visibility.PUBLIC
    low_detail_mode: bool = False
    editor_time: int = 0
    editor_time_copies: int = 0
    seed: str = ""
    extra_string: str = ""
    level_info: str = ""
    verification_time: int = 0
    replay: str = ""
    song_ids: tuple[int, ...] = ()
    sfx_ids: tuple[int, ...] = ()


def parse_delete_level(form: Form) -> ParseResult[DeleteLevelRequest]:
    reader = Reader(form)

    return reader.done(
        DeleteLevelRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            level_id=reader.integer("levelID"),
        )
    )


def parse_download_level(form: Form) -> ParseResult[DownloadLevelRequest]:
    reader = Reader(form)

    return reader.done(
        DownloadLevelRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            level_id=reader.integer("levelID"),
            increment_downloads=reader.boolean("inc"),
            extras=reader.boolean("extras"),
            rs=reader.string("rs", default=""),
            chk=reader.string("chk", default=""),
        )
    )


def parse_timely(form: Form) -> ParseResult[TimelyRequest]:
    reader = Reader(form)
    timely_type = reader.member("type", TimelyType, default=TimelyType.DAILY)
    chk = None

    if reader.has("chk"):
        chk = decode_reward_chk(reader.string("chk"), KEY_CHESTS)

    return reader.done(
        TimelyRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            timely_type=timely_type,
            chk=chk,
        )
    )


def parse_gauntlets(form: Form) -> ParseResult[GauntletsRequest]:
    reader = Reader(form)

    return reader.done(
        GauntletsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            special=reader.boolean("special"),
        )
    )


def parse_level_search(form: Form) -> ParseResult[LevelSearchRequest]:
    reader = Reader(form)
    # The client sends 0 when it is not browsing a gauntlet.
    gauntlet_id = reader.integer("gauntlet", default=0) or None

    return reader.done(
        LevelSearchRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            search_type=reader.member(
                "type", SearchType, default=SearchType.MOST_LIKED
            ),
            query=reader.string("str", default=""),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
            difficulties=reader.members("diff", SearchDifficulty),
            demon_filter=reader.optional_member("demonFilter", DemonDifficulty),
            lengths=reader.members("len", Length),
            uncompleted=reader.boolean("uncompleted"),
            only_completed=reader.boolean("onlyCompleted"),
            completed_level_ids=reader.integers("completedLevels"),
            featured=reader.boolean("featured"),
            original=reader.boolean("original"),
            two_player=reader.boolean("twoPlayer"),
            coins=reader.boolean("coins"),
            epic=reader.boolean("epic"),
            # NOTE: The client swaps these two parameter names.
            legendary=reader.boolean("mythic"),
            mythic=reader.boolean("legendary"),
            rated=reader.boolean("star"),
            unrated=reader.boolean("noStar"),
            song_id=reader.optional_integer("song"),
            custom_song=reader.boolean("customSong"),
            followed_account_ids=reader.integers("followed"),
            local=reader.boolean("local"),
            gauntlet_id=gauntlet_id,
        )
    )


def _offset(reader: Reader, key: str, offset: int) -> int:
    value = reader.integer(key, default=0)

    return value - offset if value else 0


def parse_level_scores(form: Form) -> ParseResult[LevelScoresRequest]:
    reader = Reader(form)
    progress: tuple[int, ...] = ()

    if reader.has("s6"):
        decoded = decode_xor_text(reader.string("s6"), KEY_LEVEL)

        if decoded is not None:
            progress = tuple(
                int(part) for part in decoded.split(",") if part.isdecimal()
            )

    return reader.done(
        LevelScoresRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            level_id=reader.integer("levelID"),
            score_type=reader.member(
                "type", LevelScoreType, default=LevelScoreType.FRIENDS
            ),
            platformer=reader.boolean("plat"),
            mode=reader.member("mode", PlatformerMode, default=PlatformerMode.TIME),
            percent=reader.optional_integer("percent"),
            time_ms=reader.integer("time", default=0),
            points=reader.integer("points", default=0),
            attempts=_offset(reader, "s1", _ATTEMPTS_OFFSET),
            clicks=_offset(reader, "s2", _CLICKS_OFFSET),
            seconds=_offset(reader, "s3", _SECONDS_OFFSET),
            seed=reader.integer("s4", default=0),
            progress=progress,
            rs=reader.string("s7", default=""),
            attempt_count=reader.integer("s8", default=0),
            coins=_offset(reader, "s9", _COINS_OFFSET),
            timely_id=reader.integer("s10", default=0),
            best_ticks=_offset(reader, "s11", _BEST_TICKS_OFFSET),
            best_clicks=_offset(reader, "s14", _BEST_CLICKS_OFFSET),
            best_coins=_offset(reader, "s18", _BEST_COINS_OFFSET),
            best_points_ticks=_offset(reader, "s12", _BEST_POINTS_TICKS_OFFSET),
            best_points_clicks=_offset(reader, "s15", _BEST_POINTS_CLICKS_OFFSET),
            best_points_coins=_offset(reader, "s19", _BEST_POINTS_COINS_OFFSET),
            level_version=reader.integer("s20", default=0),
            chk=reader.string("chk", default=""),
        )
    )


def parse_map_packs(form: Form) -> ParseResult[MapPacksRequest]:
    reader = Reader(form)

    return reader.done(
        MapPacksRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            page=reader.integer("page", default=0),
        )
    )


def parse_rate_demon(form: Form) -> ParseResult[RateDemonRequest]:
    reader = Reader(form)

    return reader.done(
        RateDemonRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            level_id=reader.integer("levelID"),
            rating=reader.member("rating", DemonDifficulty),
        )
    )


def parse_rate_stars(form: Form) -> ParseResult[RateStarsRequest]:
    reader = Reader(form)

    return reader.done(
        RateStarsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            level_id=reader.integer("levelID"),
            stars=reader.integer("stars"),
            rs=reader.string("rs", default=""),
            chk=reader.string("chk", default=""),
        )
    )


def verify_rate_chk(request: RateStarsRequest) -> bool:
    if request.auth is None:
        return False

    expected = rate_chk(
        request.level_id,
        request.stars,
        request.rs,
        request.auth.account_id,
        request.client.udid,
        request.client.user_id,
    )

    return expected == request.chk


def parse_report_level(form: Form) -> ParseResult[ReportLevelRequest]:
    reader = Reader(form)

    return reader.done(
        ReportLevelRequest(
            client=read_client(reader), level_id=reader.integer("levelID")
        )
    )


def parse_suggest_stars(form: Form) -> ParseResult[SuggestStarsRequest]:
    reader = Reader(form)

    return reader.done(
        SuggestStarsRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            level_id=reader.integer("levelID"),
            stars=reader.integer("stars"),
            feature=reader.member("feature", SendFeature, default=SendFeature.STAR),
        )
    )


def parse_update_description(form: Form) -> ParseResult[UpdateDescriptionRequest]:
    reader = Reader(form)

    return reader.done(
        UpdateDescriptionRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            level_id=reader.integer("levelID"),
            description=reader.text("levelDesc"),
        )
    )


def parse_upload_level(form: Form) -> ParseResult[UploadLevelRequest]:
    reader = Reader(form)

    return reader.done(
        UploadLevelRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            creator_name=reader.string("userName"),
            level_id=reader.integer("levelID", default=0),
            name=reader.string("levelName"),
            description=reader.text("levelDesc", default=""),
            version=reader.integer("levelVersion", default=1),
            length=reader.member("levelLength", Length, default=Length.TINY),
            official_song=reader.integer("audioTrack", default=0),
            custom_song_id=reader.integer("songID", default=0),
            level_string=reader.string("levelString"),
            seed2=reader.string("seed2", default=""),
            password=level_password_from_wire(reader.string("password", default="0")),
            auto=reader.boolean("auto"),
            original_id=reader.integer("original", default=0),
            two_player=reader.boolean("twoPlayer"),
            objects=reader.integer("objects", default=0),
            coins=reader.integer("coins", default=0),
            requested_stars=reader.integer("requestedStars", default=0),
            visibility=reader.member("unlisted", Visibility, default=Visibility.PUBLIC),
            low_detail_mode=reader.boolean("ldm"),
            editor_time=reader.integer("wt", default=0),
            editor_time_copies=reader.integer("wt2", default=0),
            seed=reader.string("seed", default=""),
            extra_string=reader.string("extraString", default=""),
            level_info=reader.string("levelInfo", default=""),
            verification_time=reader.integer("ts", default=0),
            replay=reader.string("lrs", default=""),
            song_ids=reader.integers("songIDs"),
            sfx_ids=reader.integers("sfxIDs"),
        )
    )


def verify_level_seed(request: UploadLevelRequest) -> bool:
    return level_seed(request.level_string) == request.seed2
