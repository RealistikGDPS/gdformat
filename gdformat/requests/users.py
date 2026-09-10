from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import profile_chk
from gdformat.enums import IconType
from gdformat.enums import LeaderboardStat
from gdformat.enums import LeaderboardType
from gdformat.objects._common import serialise_integers
from gdformat.objects.user import ClassicStats
from gdformat.objects.user import IconSet
from gdformat.objects.user import PlatformerStats
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_auth
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth

_DEFAULT_COUNT = 100
_GLOW_ON = 2
_COMPLETION_COUNTS = 12


@dataclass(frozen=True, slots=True, kw_only=True)
class LeaderboardRequest:
    client: Client
    auth: Auth | None
    leaderboard_type: LeaderboardType = LeaderboardType.TOP
    count: int = _DEFAULT_COUNT
    stat: LeaderboardStat = LeaderboardStat.STARS


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileRequest:
    client: Client
    auth: Auth | None
    target_account_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class UserSearchRequest:
    client: Client
    auth: Auth | None
    query: str
    page: int = 0
    total: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateStatsRequest:
    """`demon_level_ids` lists completed online demons; the server derives the
    per-difficulty breakdown. `seed2` is the integrity value checked by
    `verify_stats_chk`."""

    client: Client
    auth: Auth
    stars: int
    moons: int
    demons: int
    diamonds: int
    icon_id: int
    icon_type: IconType
    secret_coins: int
    user_coins: int
    icons: IconSet
    glow: bool
    seed2: str
    classic: ClassicStats
    platformer: PlatformerStats
    name: str = ""
    colour1: int = 0
    colour2: int = 0
    colour3: int = 0
    demon_level_ids: tuple[int, ...] = ()
    weekly_demons: int = 0
    gauntlet_demons: int = 0
    event_demons: int = 0
    seed: str = ""


def parse_leaderboard(form: Form) -> ParseResult[LeaderboardRequest]:
    reader = Reader(form)

    return reader.done(
        LeaderboardRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            leaderboard_type=reader.choice(
                "type", LeaderboardType, default=LeaderboardType.TOP
            ),
            count=reader.integer("count", default=_DEFAULT_COUNT),
            stat=reader.member("stat", LeaderboardStat, default=LeaderboardStat.STARS),
        )
    )


def parse_profile(form: Form) -> ParseResult[ProfileRequest]:
    reader = Reader(form)

    return reader.done(
        ProfileRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            target_account_id=reader.integer("targetAccountID"),
        )
    )


def parse_user_search(form: Form) -> ParseResult[UserSearchRequest]:
    reader = Reader(form)

    return reader.done(
        UserSearchRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            query=reader.string("str", default=""),
            page=reader.integer("page", default=0),
            total=reader.integer("total", default=0),
        )
    )


def parse_update_stats(form: Form) -> ParseResult[UpdateStatsRequest]:
    reader = Reader(form)
    counts = reader.integers("sinfo")

    if len(counts) != _COMPLETION_COUNTS:
        return reader.error or ParseError.INVALID_LAYOUT

    return reader.done(
        UpdateStatsRequest(
            client=read_client(reader),
            auth=read_auth(reader),
            stars=reader.integer("stars"),
            moons=reader.integer("moons", default=0),
            demons=reader.integer("demons"),
            diamonds=reader.integer("diamonds"),
            icon_id=reader.integer("icon"),
            icon_type=reader.member("iconType", IconType),
            secret_coins=reader.integer("coins"),
            user_coins=reader.integer("userCoins"),
            icons=IconSet(
                cube=reader.integer("accIcon"),
                ship=reader.integer("accShip"),
                ball=reader.integer("accBall"),
                ufo=reader.integer("accBird"),
                wave=reader.integer("accDart"),
                robot=reader.integer("accRobot"),
                spider=reader.integer("accSpider"),
                swing=reader.integer("accSwing", default=1),
                jetpack=reader.integer("accJetpack", default=1),
                explosion=reader.integer("accExplosion"),
            ),
            glow=reader.boolean("accGlow"),
            seed2=reader.string("seed2"),
            classic=ClassicStats(
                auto=counts[0],
                easy=counts[1],
                normal=counts[2],
                hard=counts[3],
                harder=counts[4],
                insane=counts[5],
                daily=reader.integer("sinfod", default=0),
                gauntlet=reader.integer("sinfog", default=0),
            ),
            platformer=PlatformerStats(
                auto=counts[6],
                easy=counts[7],
                normal=counts[8],
                hard=counts[9],
                harder=counts[10],
                insane=counts[11],
                event=reader.integer("sinfoe", default=0),
            ),
            name=reader.string("userName", default=""),
            colour1=reader.integer("color1", default=0),
            colour2=reader.integer("color2", default=0),
            colour3=reader.integer("color3", default=0),
            demon_level_ids=reader.integers("dinfo"),
            weekly_demons=reader.integer("dinfow", default=0),
            gauntlet_demons=reader.integer("dinfog", default=0),
            event_demons=reader.integer("dinfoe", default=0),
            seed=reader.string("seed", default=""),
        )
    )


def verify_stats_chk(request: UpdateStatsRequest) -> bool:
    """The value list is the 2.1 list, then the length of `dinfo`, `dinfow` and
    `dinfog`, then `sinfo`, `sinfod` and `sinfog`. The client only sends the
    demon values when it has completed a demon, and it only hashes them then
    too (observed on 2.2081); the event counters are never part of it."""

    icons = request.icons
    classic = request.classic
    platformer = request.platformer

    sinfo = (
        f"{classic.auto},{classic.easy},{classic.normal},{classic.hard},"
        f"{classic.harder},{classic.insane},{platformer.auto},{platformer.easy},"
        f"{platformer.normal},{platformer.hard},{platformer.harder},{platformer.insane}"
    )
    demons: tuple[object, ...] = ()

    if request.demon_level_ids:
        demons = (
            len(serialise_integers(request.demon_level_ids)),
            request.weekly_demons,
            request.gauntlet_demons,
        )

    expected = profile_chk(
        (
            request.auth.account_id,
            request.user_coins,
            request.demons,
            request.stars,
            request.secret_coins,
            request.icon_type,
            request.icon_id,
            request.diamonds,
            icons.cube,
            icons.ship,
            icons.ball,
            icons.ufo,
            icons.wave,
            icons.robot,
            int(request.glow),
            icons.spider,
            icons.explosion,
            *demons,
            sinfo,
            classic.daily,
            classic.gauntlet,
        )
    )

    return expected == request.seed2
