from gdformat.crypto import KEY_CHALLENGES
from gdformat.crypto import KEY_CHESTS
from gdformat.crypto import challenges_hash
from gdformat.crypto import encode_reward_blob
from gdformat.crypto import rewards_hash
from gdformat.encoding import random_string
from gdformat.enums import ChestType
from gdformat.enums import RewardType
from gdformat.objects.reward import Chest
from gdformat.objects.reward import Quest
from gdformat.objects.reward import RewardStack
from gdformat.objects.reward import serialise_chest
from gdformat.objects.reward import serialise_quest
from gdformat.objects.reward import serialise_reward_stacks

_PREFIX_LENGTH = 5


def _prefix(prefix: str | None) -> str:
    return random_string(_PREFIX_LENGTH) if prefix is None else prefix


def serialise_rewards(
    user_id: int,
    chk: int,
    udid: str,
    account_id: int,
    small_seconds_left: int,
    small_chest: Chest | None,
    small_count: int,
    large_seconds_left: int,
    large_chest: Chest | None,
    large_count: int,
    reward_type: RewardType,
    *,
    prefix: str | None = None,
) -> str:
    prefix = _prefix(prefix)

    plaintext = (
        f"{prefix}:{user_id}:{chk}:{udid}:{account_id}:{small_seconds_left}"
        f":{serialise_chest(small_chest)}:{small_count}:{large_seconds_left}"
        f":{serialise_chest(large_chest)}:{large_count}:{reward_type:d}"
    )

    blob = encode_reward_blob(plaintext, KEY_CHESTS)

    return f"{prefix}{blob}|{rewards_hash(blob)}"


def serialise_challenges(
    user_id: int,
    chk: int,
    udid: str,
    account_id: int,
    seconds_left: int,
    quests: tuple[Quest, Quest, Quest],
    *,
    prefix: str | None = None,
) -> str:
    prefix = _prefix(prefix)
    quest_text = ":".join(map(serialise_quest, quests))

    plaintext = (
        f"{prefix}:{user_id}:{chk}:{udid}:{account_id}:{seconds_left}:{quest_text}"
    )

    blob = encode_reward_blob(plaintext, KEY_CHALLENGES)

    return f"{prefix}{blob}|{challenges_hash(blob)}"


def serialise_secret_reward(
    chk: int,
    reward_id: int,
    chest_type: ChestType,
    rewards: tuple[RewardStack, ...],
    *,
    prefix: str | None = None,
) -> str:
    prefix = _prefix(prefix)

    plaintext = (
        f"{prefix}:{chk}:{reward_id}:{chest_type:d}:{serialise_reward_stacks(rewards)}"
    )

    blob = encode_reward_blob(plaintext, KEY_CHESTS)

    return f"{prefix}{blob}|{rewards_hash(blob)}"
