from dataclasses import dataclass

from gdformat._common import Form
from gdformat._common import ParseError
from gdformat._common import ParseResult
from gdformat._wire import Reader
from gdformat.crypto import KEY_CHALLENGES
from gdformat.crypto import KEY_CHESTS
from gdformat.crypto import decode_reward_chk
from gdformat.enums import RewardType
from gdformat.requests._common import Auth
from gdformat.requests._common import Client
from gdformat.requests._common import read_client
from gdformat.requests._common import read_optional_auth


@dataclass(frozen=True, slots=True, kw_only=True)
class ChallengesRequest:
    """`chk` is the client's decoded challenge number, to be echoed back."""

    client: Client
    auth: Auth | None
    chk: int
    world: bool = False
    lite: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class RewardsRequest:
    client: Client
    auth: Auth | None
    chk: int
    reward_type: RewardType = RewardType.INFO
    r1: int = 0
    r2: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class SecretRewardRequest:
    client: Client
    auth: Auth | None
    chk: int
    reward_key: str


def _read_chk(reader: Reader, key: bytes) -> int | None:
    return decode_reward_chk(reader.string("chk"), key)


def parse_challenges(form: Form) -> ParseResult[ChallengesRequest]:
    reader = Reader(form)
    chk = _read_chk(reader, KEY_CHALLENGES)

    if chk is None:
        return reader.error or ParseError.INVALID_VALUE

    return reader.done(
        ChallengesRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            chk=chk,
            world=reader.boolean("world"),
            lite=reader.boolean("gdl"),
        )
    )


def parse_rewards(form: Form) -> ParseResult[RewardsRequest]:
    reader = Reader(form)
    chk = _read_chk(reader, KEY_CHESTS)

    if chk is None:
        return reader.error or ParseError.INVALID_VALUE

    return reader.done(
        RewardsRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            chk=chk,
            reward_type=reader.member(
                "rewardType", RewardType, default=RewardType.INFO
            ),
            r1=reader.integer("r1", default=0),
            r2=reader.integer("r2", default=0),
        )
    )


def parse_secret_reward(form: Form) -> ParseResult[SecretRewardRequest]:
    reader = Reader(form)
    chk = _read_chk(reader, KEY_CHESTS)

    if chk is None:
        return reader.error or ParseError.INVALID_VALUE

    return reader.done(
        SecretRewardRequest(
            client=read_client(reader),
            auth=read_optional_auth(reader),
            chk=chk,
            reward_key=reader.string("rewardKey", default=""),
        )
    )
