from enum import IntEnum
from enum import StrEnum


class Difficulty(IntEnum):
    """Level and list difficulty, using the list difficulty numbering."""

    NA = -1
    AUTO = 0
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    EASY_DEMON = 6
    MEDIUM_DEMON = 7
    HARD_DEMON = 8
    INSANE_DEMON = 9
    EXTREME_DEMON = 10

    @property
    def is_demon(self) -> bool:
        return self >= Difficulty.EASY_DEMON


class DemonDifficulty(IntEnum):
    """Demon difficulty as used by moderator ratings and the demon search filter."""

    EASY = 1
    MEDIUM = 2
    HARD = 3
    INSANE = 4
    EXTREME = 5


class SearchDifficulty(IntEnum):
    NA = -1
    DEMON = -2
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5


class MapPackDifficulty(IntEnum):
    AUTO = 0
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    HARD_DEMON = 6
    EASY_DEMON = 7
    MEDIUM_DEMON = 8
    INSANE_DEMON = 9
    EXTREME_DEMON = 10


class Length(IntEnum):
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4
    PLATFORMER = 5


class Rating(IntEnum):
    NONE = 0
    EPIC = 1
    LEGENDARY = 2
    MYTHIC = 3


class SendFeature(IntEnum):
    STAR = 0
    FEATURE = 1
    EPIC = 2
    LEGENDARY = 3
    MYTHIC = 4


class Visibility(IntEnum):
    PUBLIC = 0
    FRIENDS = 1
    UNLISTED = 2


class IconType(IntEnum):
    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    SWING = 7
    JETPACK = 8


class ModLevel(IntEnum):
    NONE = 0
    MOD = 1
    ELDER = 2
    LEADERBOARD = 3


class ModAccess(IntEnum):
    DENIED = -1
    MOD = 1
    ELDER = 2
    LEADERBOARD = 99


class MessageState(IntEnum):
    ALL = 0
    FRIENDS = 1
    NONE = 2


class FriendRequestState(IntEnum):
    ALL = 0
    NONE = 1


class CommentHistoryState(IntEnum):
    ALL = 0
    FRIENDS = 1
    NONE = 2


class FriendState(IntEnum):
    NONE = 0
    FRIENDS = 1
    REQUEST_SENT = 3
    REQUEST_RECEIVED = 4


class SearchType(IntEnum):
    QUERY = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_USER = 5
    FEATURED = 6
    MAGIC = 7
    SENT_LEGACY = 8
    LEVEL_IDS = 10
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    MOST_LIKED_WORLD = 15
    HALL_OF_FAME = 16
    FEATURED_WORLD = 17
    UNKNOWN_18 = 18
    LEVEL_IDS_PAGED = 19
    DAILY_HISTORY = 21
    WEEKLY_HISTORY = 22
    EVENT_HISTORY = 23
    REPORTED = 24
    LEVEL_LIST = 25
    LOCAL_LEVEL_LIST = 26
    SENT = 27
    LITE_WEEKLY = 28
    LITE_BONUS = 29


class ListSearchType(IntEnum):
    QUERY = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_ACCOUNT = 5
    TOP = 6
    MAGIC = 7
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    SENT = 27


class LeaderboardType(StrEnum):
    TOP = "top"
    RELATIVE = "relative"
    FRIENDS = "friends"
    CREATORS = "creators"


class LeaderboardStat(IntEnum):
    STARS = 0
    MOONS = 1
    DEMONS = 2
    USER_COINS = 3


class LevelScoreType(IntEnum):
    FRIENDS = 0
    TOP = 1
    WEEK = 2


class PlatformerMode(IntEnum):
    TIME = 0
    POINTS = 1


class LikeType(IntEnum):
    LEVEL = 1
    LEVEL_COMMENT = 2
    ACCOUNT_COMMENT = 3
    LIST = 4


class CommentType(IntEnum):
    LEVEL = 0
    ACCOUNT = 1


class CommentMode(IntEnum):
    RECENT = 0
    MOST_LIKED = 1


class TimelyType(IntEnum):
    DAILY = 0
    WEEKLY = 1
    EVENT = 2

    @property
    def id_offset(self) -> int:
        return self * 100_000


class RewardType(IntEnum):
    INFO = 0
    SMALL = 1
    LARGE = 2


class ChestType(IntEnum):
    SMALL = 1
    LARGE = 2
    EVENT = 3


class Shard(IntEnum):
    NONE = 0
    FIRE = 1
    ICE = 2
    POISON = 3
    SHADOW = 4
    LAVA = 5
    DEMON_KEY = 6
    EARTH = 10
    BLOOD = 11
    METAL = 12
    LIGHT = 13
    SOUL = 14


class RewardItem(IntEnum):
    FIRE_SHARD = 1
    ICE_SHARD = 2
    POISON_SHARD = 3
    SHADOW_SHARD = 4
    LAVA_SHARD = 5
    DEMON_KEY = 6
    ORBS = 7
    DIAMONDS = 8
    EARTH_SHARD = 10
    BLOOD_SHARD = 11
    METAL_SHARD = 12
    LIGHT_SHARD = 13
    SOUL_SHARD = 14
    GOLD_KEY = 15
    UNLOCK_CUBE = 1001
    UNLOCK_COLOUR_1 = 1002
    UNLOCK_COLOUR_2 = 1003
    UNLOCK_SHIP = 1004
    UNLOCK_BALL = 1005
    UNLOCK_UFO = 1006
    UNLOCK_WAVE = 1007
    UNLOCK_ROBOT = 1008
    UNLOCK_SPIDER = 1009
    UNLOCK_TRAIL = 1010
    UNLOCK_DEATH_EFFECT = 1011
    UNLOCK_ITEM = 1012
    UNLOCK_SWING = 1013
    UNLOCK_JETPACK = 1014
    UNLOCK_SHIP_FIRE = 1015


class QuestItem(IntEnum):
    ORBS = 1
    COINS = 2
    STARS = 3


class UserListType(IntEnum):
    FRIENDS = 0
    BLOCKED = 1


class AccountUrlType(IntEnum):
    BACKUP = 1
    SYNC = 2


class Platform(IntEnum):
    UNKNOWN = 0
    IOS = 1
    ANDROID = 2
    WINDOWS = 3
    MACOS = 8


class Nong(IntEnum):
    NONE = 0
    NCS = 1
    CHOMPO = 2


class NewBadge(IntEnum):
    YELLOW = 0
    BLUE = 1


class Secret(StrEnum):
    COMMON = "Wmfd2893gb7"
    ACCOUNT = "Wmfv3899gc9"
    LEVEL = "Wmfv2898gc9"
    MOD = "Wmfp3879gc3"
