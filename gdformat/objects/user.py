from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat._wire import pairs
from gdformat.encoding import decode_text
from gdformat.encoding import encode_text
from gdformat.encoding import strip_separators
from gdformat.enums import CommentHistoryState
from gdformat.enums import FriendRequestState
from gdformat.enums import FriendState
from gdformat.enums import IconType
from gdformat.enums import MessageState
from gdformat.enums import ModLevel

_GLOW_ON = 2


@dataclass(frozen=True, slots=True, kw_only=True)
class DisplayIcon:
    icon_id: int
    icon_type: IconType
    colour1: int
    colour2: int
    colour3: int
    glow: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class UserRef:
    user_id: int
    account_id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Player:
    name: str
    user_id: int
    account_id: int
    icon: DisplayIcon


@dataclass(frozen=True, slots=True, kw_only=True)
class UserPreview:
    """A user as shown in search results and top leaderboards."""

    name: str
    user_id: int
    account_id: int
    icon: DisplayIcon
    stars: int
    moons: int
    demons: int
    diamonds: int
    secret_coins: int
    user_coins: int
    creator_points: int
    rank: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class IconSet:
    cube: int = 1
    ship: int = 1
    ball: int = 1
    ufo: int = 1
    wave: int = 1
    robot: int = 1
    spider: int = 1
    swing: int = 1
    jetpack: int = 1
    explosion: int = 1
    # NOTE: Keys 62 and 63 are undocumented. The official server sends 0 and 2 for
    # nearly every account; 62 is presumably the ship fire added in 2.2.
    ship_fire: int = 0
    extra: int = 2


@dataclass(frozen=True, slots=True, kw_only=True)
class Privacy:
    messages: MessageState = MessageState.ALL
    friend_requests: FriendRequestState = FriendRequestState.ALL
    comment_history: CommentHistoryState = CommentHistoryState.ALL


@dataclass(frozen=True, slots=True, kw_only=True)
class Socials:
    youtube: str = ""
    twitter: str = ""
    twitch: str = ""
    discord: str = ""
    instagram: str = ""
    tiktok: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class DemonStats:
    easy: int = 0
    medium: int = 0
    hard: int = 0
    insane: int = 0
    extreme: int = 0
    easy_platformer: int = 0
    medium_platformer: int = 0
    hard_platformer: int = 0
    insane_platformer: int = 0
    extreme_platformer: int = 0
    weekly: int = 0
    gauntlet: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class ClassicStats:
    auto: int = 0
    easy: int = 0
    normal: int = 0
    hard: int = 0
    harder: int = 0
    insane: int = 0
    daily: int = 0
    gauntlet: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class PlatformerStats:
    auto: int = 0
    easy: int = 0
    normal: int = 0
    hard: int = 0
    harder: int = 0
    insane: int = 0
    # NOTE: The documentation calls this "the map"; the client submits it as `sinfoe`.
    event: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class IncomingFriendRequest:
    id: int
    message: str
    age: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Notifications:
    messages: int
    friend_requests: int
    friends: int


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    """A full profile as returned by getGJUserInfo20."""

    name: str
    user_id: int
    account_id: int
    stars: int
    moons: int
    demons: int
    diamonds: int
    secret_coins: int
    user_coins: int
    creator_points: int
    colour1: int
    colour2: int
    colour3: int
    icons: IconSet
    glow: bool
    global_rank: int
    mod_level: ModLevel = ModLevel.NONE
    privacy: Privacy = Privacy()
    socials: Socials = Socials()
    custom: str = ""
    demon_stats: DemonStats = DemonStats()
    classic_stats: ClassicStats = ClassicStats()
    platformer_stats: PlatformerStats = PlatformerStats()
    friend_state: FriendState = FriendState.NONE
    incoming_request: IncomingFriendRequest | None = None
    notifications: Notifications | None = None
    is_registered: bool = True


def serialise_icon(icon: DisplayIcon, separator: str) -> str:
    glow = _GLOW_ON if icon.glow else 0

    return (
        f"9{separator}{icon.icon_id}{separator}10{separator}{icon.colour1}"
        f"{separator}11{separator}{icon.colour2}{separator}14{separator}"
        f"{icon.icon_type:d}{separator}15{separator}{glow}{separator}51{separator}"
        f"{icon.colour3}"
    )


def read_icon(reader: Reader) -> DisplayIcon:
    return DisplayIcon(
        icon_id=reader.integer("9", default=1),
        icon_type=reader.member("14", IconType, default=IconType.CUBE),
        colour1=reader.integer("10", default=0),
        colour2=reader.integer("11", default=0),
        colour3=reader.integer("51", default=0),
        glow=reader.integer("15", default=0) == _GLOW_ON,
    )


def serialise_player(
    player: Player,
    separator: str = ":",
    *,
    include_user_id: bool = True,
) -> str:
    icon = serialise_icon(player.icon, separator)
    user_id = f"2{separator}{player.user_id}{separator}" if include_user_id else ""

    return (
        f"1{separator}{strip_separators(player.name)}{separator}{user_id}"
        f"{icon}{separator}16{separator}{player.account_id}"
    )


def read_player(reader: Reader) -> Player:
    return Player(
        name=reader.string("1"),
        user_id=reader.integer("2", default=0),
        account_id=reader.integer("16", default=0),
        icon=read_icon(reader),
    )


def serialise_user_ref(user: UserRef) -> str:
    return f"{user.user_id}:{strip_separators(user.name)}:{user.account_id}"


def parse_user_ref(text: str) -> ParseResult[UserRef]:
    parts = text.split(":")

    if len(parts) != 3:
        return ParseError.INVALID_LAYOUT

    try:
        user_id = int(parts[0])
        account_id = int(parts[2])
    except ValueError:
        return ParseError.INVALID_INTEGER

    return UserRef(user_id=user_id, account_id=account_id, name=parts[1])


def serialise_user_preview(user: UserPreview, *, highlight: bool = False) -> str:
    """`highlight` adds key 7, which the official server sends on the requesting
    account's own leaderboard row."""

    icon = user.icon
    glow = _GLOW_ON if icon.glow else 0

    text = (
        f"1:{strip_separators(user.name)}:2:{user.user_id}:13:{user.secret_coins}"
        f":17:{user.user_coins}:6:{user.rank}:9:{icon.icon_id}:10:{icon.colour1}"
        f":11:{icon.colour2}:51:{icon.colour3}:14:{icon.icon_type:d}:15:{glow}"
        f":16:{user.account_id}:3:{user.stars}:8:{user.creator_points}"
        f":4:{user.demons}:46:{user.diamonds}:52:{user.moons}"
    )

    if highlight:
        text += f":7:{user.account_id}"

    return text


def parse_user_preview(text: str) -> ParseResult[UserPreview]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)

    return reader.done(
        UserPreview(
            name=reader.string("1"),
            user_id=reader.integer("2"),
            account_id=reader.integer("16", default=0),
            icon=read_icon(reader),
            stars=reader.integer("3", default=0),
            moons=reader.integer("52", default=0),
            demons=reader.integer("4", default=0),
            diamonds=reader.integer("46", default=0),
            secret_coins=reader.integer("13", default=0),
            user_coins=reader.integer("17", default=0),
            creator_points=reader.integer("8", default=0),
            rank=reader.integer("6", default=0),
        )
    )


def serialise_demon_stats(stats: DemonStats) -> str:
    return (
        f"{stats.easy},{stats.medium},{stats.hard},{stats.insane},{stats.extreme},"
        f"{stats.easy_platformer},{stats.medium_platformer},{stats.hard_platformer},"
        f"{stats.insane_platformer},{stats.extreme_platformer},{stats.weekly},"
        f"{stats.gauntlet}"
    )


def serialise_classic_stats(stats: ClassicStats) -> str:
    return (
        f"{stats.auto},{stats.easy},{stats.normal},{stats.hard},{stats.harder},"
        f"{stats.insane},{stats.daily},{stats.gauntlet}"
    )


def serialise_platformer_stats(stats: PlatformerStats) -> str:
    return (
        f"{stats.auto},{stats.easy},{stats.normal},{stats.hard},{stats.harder},"
        f"{stats.insane},{stats.event}"
    )


def _counts(text: str, size: int) -> tuple[int, ...] | None:
    if not text:
        return (0,) * size

    parts = text.split(",")

    if len(parts) != size:
        return None

    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return None


def parse_demon_stats(text: str) -> ParseResult[DemonStats]:
    counts = _counts(text, 12)

    if counts is None:
        return ParseError.INVALID_VALUE

    return DemonStats(
        easy=counts[0],
        medium=counts[1],
        hard=counts[2],
        insane=counts[3],
        extreme=counts[4],
        easy_platformer=counts[5],
        medium_platformer=counts[6],
        hard_platformer=counts[7],
        insane_platformer=counts[8],
        extreme_platformer=counts[9],
        weekly=counts[10],
        gauntlet=counts[11],
    )


def parse_classic_stats(text: str) -> ParseResult[ClassicStats]:
    counts = _counts(text, 8)

    if counts is None:
        return ParseError.INVALID_VALUE

    return ClassicStats(
        auto=counts[0],
        easy=counts[1],
        normal=counts[2],
        hard=counts[3],
        harder=counts[4],
        insane=counts[5],
        daily=counts[6],
        gauntlet=counts[7],
    )


def parse_platformer_stats(text: str) -> ParseResult[PlatformerStats]:
    counts = _counts(text, 7)

    if counts is None:
        return ParseError.INVALID_VALUE

    return PlatformerStats(
        auto=counts[0],
        easy=counts[1],
        normal=counts[2],
        hard=counts[3],
        harder=counts[4],
        insane=counts[5],
        event=counts[6],
    )


def serialise_user(user: User) -> str:
    icons = user.icons
    privacy = user.privacy
    socials = user.socials

    text = (
        f"1:{strip_separators(user.name)}:2:{user.user_id}:13:{user.secret_coins}"
        f":17:{user.user_coins}:10:{user.colour1}:11:{user.colour2}:51:{user.colour3}"
        f":3:{user.stars}:46:{user.diamonds}:52:{user.moons}:4:{user.demons}"
        f":8:{user.creator_points}:18:{privacy.messages:d}"
        f":19:{privacy.friend_requests:d}:50:{privacy.comment_history:d}"
        f":20:{socials.youtube}:21:{icons.cube}:22:{icons.ship}:23:{icons.ball}"
        f":24:{icons.ufo}:25:{icons.wave}:26:{icons.robot}:28:{user.glow:d}"
        f":43:{icons.spider}:48:{icons.explosion}:53:{icons.swing}:54:{icons.jetpack}"
        f":62:{icons.ship_fire}:63:{icons.extra}"
        f":30:{user.global_rank}:16:{user.account_id}:31:{user.friend_state:d}"
        f":44:{socials.twitter}:45:{socials.twitch}:59:{socials.instagram}"
        f":60:{socials.tiktok}:58:{socials.discord}:61:{user.custom}"
        f":49:{user.mod_level:d}:55:{serialise_demon_stats(user.demon_stats)}"
        f":56:{serialise_classic_stats(user.classic_stats)}"
        f":57:{serialise_platformer_stats(user.platformer_stats)}"
    )

    request = user.incoming_request

    if request is not None:
        text += f":32:{request.id}:35:{encode_text(request.message)}:37:{request.age}"

    notifications = user.notifications

    if notifications is not None:
        text += (
            f":38:{notifications.messages}:39:{notifications.friend_requests}"
            f":40:{notifications.friends}"
        )

    return f"{text}:29:{user.is_registered:d}"


def parse_user(text: str) -> ParseResult[User]:
    values = pairs(text, ":")

    if values is None:
        return ParseError.INVALID_LAYOUT

    reader = Reader(values)
    demon_stats = parse_demon_stats(reader.string("55", default=""))
    classic_stats = parse_classic_stats(reader.string("56", default=""))
    platformer_stats = parse_platformer_stats(reader.string("57", default=""))

    if isinstance(demon_stats, ParseError):
        return demon_stats

    if isinstance(classic_stats, ParseError):
        return classic_stats

    if isinstance(platformer_stats, ParseError):
        return platformer_stats

    incoming_request = None
    request_id = reader.optional_integer("32")

    if request_id is not None:
        message = decode_text(reader.string("35", default=""))

        if message is None:
            return ParseError.INVALID_BASE64

        incoming_request = IncomingFriendRequest(
            id=request_id, message=message, age=reader.string("37", default="")
        )

    notifications = None

    if reader.has("38") or reader.has("39") or reader.has("40"):
        notifications = Notifications(
            messages=reader.integer("38", default=0),
            friend_requests=reader.integer("39", default=0),
            friends=reader.integer("40", default=0),
        )

    return reader.done(
        User(
            name=reader.string("1"),
            user_id=reader.integer("2"),
            account_id=reader.integer("16"),
            stars=reader.integer("3", default=0),
            moons=reader.integer("52", default=0),
            demons=reader.integer("4", default=0),
            diamonds=reader.integer("46", default=0),
            secret_coins=reader.integer("13", default=0),
            user_coins=reader.integer("17", default=0),
            creator_points=reader.integer("8", default=0),
            colour1=reader.integer("10", default=0),
            colour2=reader.integer("11", default=0),
            colour3=reader.integer("51", default=0),
            icons=IconSet(
                cube=reader.integer("21", default=1),
                ship=reader.integer("22", default=1),
                ball=reader.integer("23", default=1),
                ufo=reader.integer("24", default=1),
                wave=reader.integer("25", default=1),
                robot=reader.integer("26", default=1),
                spider=reader.integer("43", default=1),
                swing=reader.integer("53", default=1),
                jetpack=reader.integer("54", default=1),
                explosion=reader.integer("48", default=1),
                ship_fire=reader.integer("62", default=0),
                extra=reader.integer("63", default=2),
            ),
            glow=reader.boolean("28"),
            global_rank=reader.integer("30", default=0),
            mod_level=reader.member("49", ModLevel, default=ModLevel.NONE),
            privacy=Privacy(
                messages=reader.member("18", MessageState, default=MessageState.ALL),
                friend_requests=reader.member(
                    "19", FriendRequestState, default=FriendRequestState.ALL
                ),
                comment_history=reader.member(
                    "50", CommentHistoryState, default=CommentHistoryState.ALL
                ),
            ),
            socials=Socials(
                youtube=reader.string("20", default=""),
                twitter=reader.string("44", default=""),
                twitch=reader.string("45", default=""),
                discord=reader.string("58", default=""),
                instagram=reader.string("59", default=""),
                tiktok=reader.string("60", default=""),
            ),
            custom=reader.string("61", default=""),
            demon_stats=demon_stats,
            classic_stats=classic_stats,
            platformer_stats=platformer_stats,
            friend_state=reader.member("31", FriendState, default=FriendState.NONE),
            incoming_request=incoming_request,
            notifications=notifications,
            is_registered=reader.boolean("29", default=True),
        )
    )
