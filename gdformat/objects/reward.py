from dataclasses import dataclass

from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat.encoding import strip_separators
from gdformat.enums import QuestItem
from gdformat.enums import RewardItem
from gdformat.enums import Shard


@dataclass(frozen=True, slots=True, kw_only=True)
class Chest:
    orbs: int
    diamonds: int
    shard: Shard = Shard.NONE
    keys: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class Quest:
    id: int
    item: QuestItem
    amount: int
    diamonds: int
    name: str


@dataclass(frozen=True, slots=True)
class RewardStack:
    item: RewardItem
    amount: int


def serialise_chest(chest: Chest | None) -> str:
    """`None` is sent as `-`, which is what the official server returns for a
    chest the account has no data for yet."""

    if chest is None:
        return "-"

    return f"{chest.orbs},{chest.diamonds},{chest.shard:d},{chest.keys}"


def parse_chest(text: str) -> ParseResult[Chest | None]:
    if text in ("", "-"):
        return None

    parts = text.split(",")

    if len(parts) != 4:
        return ParseError.INVALID_LAYOUT

    try:
        orbs, diamonds, shard, keys = (int(part) for part in parts)

        return Chest(orbs=orbs, diamonds=diamonds, shard=Shard(shard), keys=keys)
    except ValueError:
        return ParseError.INVALID_VALUE


def serialise_quest(quest: Quest) -> str:
    name = strip_separators(quest.name).replace(",", "")

    return f"{quest.id},{quest.item:d},{quest.amount},{quest.diamonds},{name}"


def parse_quest(text: str) -> ParseResult[Quest]:
    parts = text.split(",", 4)

    if len(parts) != 5:
        return ParseError.INVALID_LAYOUT

    try:
        quest_id, item, amount, diamonds = (int(part) for part in parts[:4])

        return Quest(
            id=quest_id,
            item=QuestItem(item),
            amount=amount,
            diamonds=diamonds,
            name=parts[4],
        )
    except ValueError:
        return ParseError.INVALID_VALUE


def serialise_reward_stacks(stacks: tuple[RewardStack, ...]) -> str:
    return ",".join(f"{stack.item:d},{stack.amount}" for stack in stacks)


def parse_reward_stacks(text: str) -> ParseResult[tuple[RewardStack, ...]]:
    if not text:
        return ()

    parts = text.split(",")

    if len(parts) % 2:
        return ParseError.INVALID_LAYOUT

    try:
        return tuple(
            RewardStack(RewardItem(int(item)), int(amount))
            for item, amount in zip(parts[::2], parts[1::2], strict=True)
        )
    except ValueError:
        return ParseError.INVALID_VALUE
