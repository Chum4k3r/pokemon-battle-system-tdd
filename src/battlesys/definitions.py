# -*- coding: utf-8 -*-

from functools import lru_cache
import random
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum, auto


class MovePos(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3


class Nature(StrEnum):
    PHYSICAL = auto()
    MAGICAL = auto()


class StatsName(StrEnum):
    HP  = 'health'
    STR = 'strength'
    AGI = 'agility'
    CON = 'constitution'
    INT = 'intelligence'
    CHA = 'charisma'
    LUK = 'luckiness'
    EVA = 'evasiveness'
    ACC = 'accuracy'
    ATK = 'attack'
    DFN = 'defense'
    SAT = 'special attack'
    SDF = 'special defense'
    SPD = 'speed'


class ResultType(StrEnum):
    MISS = 'missed'
    EVAD = 'evaded'
    HIT = 'hit'
    CRIT = 'critical'
    FAIL = 'failed'



class InvalidNatureError(Exception):
    def __init__(self, nature: Nature) -> None:
        self.nature = nature

    def __str__(self) -> str:
        return f"The nature {self.nature} is not valid. Only possible values are {list(Nature)}"

@dataclass
class StatsAlteration:
    stats: StatsName
    count: int


@dataclass
class Condition:
    name: str
    damage: int
    alteration: StatsAlteration


@lru_cache
def _stats_by_nature() -> dict[Nature, tuple[StatsName, StatsName]]:
    return {Nature.PHYSICAL : (StatsName.ATK, StatsName.DFN),
            Nature.MAGICAL: (StatsName.SAT, StatsName.SDF)}

@dataclass
class Damage:
    _stats: dict[Nature, tuple[StatsName, StatsName]] = field(default_factory=_stats_by_nature, init=False, repr=False, compare=False)
    power: int
    nature: Nature

    @property
    def stats(self) -> tuple[StatsName, StatsName]:
        return self._stats[self.nature]



@dataclass
class MoveEffect:
    damage: int = 0
    alteration: StatsAlteration | None = None
    condition: Condition | None = None
    result: ResultType = ResultType.FAIL


@dataclass
class Move:
    name: str = ""

    hit_rate: int = 0

    damage: Damage | None = None

    alteration: StatsAlteration | None = None
    alteration_rate: int = 0

    condition: Condition | None = None
    condition_rate: int = 0

    description: str = ''

    def effect(self, caster: 'Creature', target: 'Creature') -> MoveEffect:
        result = self.hit_or_miss(caster, target)

        if result is not ResultType.HIT:
            return MoveEffect(result=result)

        damage, critical = self.build_damage(caster, target)
        if critical:
            result = ResultType.CRIT

        alteration = self.alteration if is_a_hit(self.alteration_rate, 0, 0) else None

        _effect = MoveEffect(result=result,
                             damage=damage,
                             alteration=alteration)
        return _effect

    def hit_or_miss(self, caster: 'Creature', target: 'Creature') -> ResultType:
        hit_result = (
            ResultType.HIT
            if is_a_hit(self.hit_rate,
                        caster.current_stats(StatsName.ACC),
                        target.current_stats(StatsName.EVA))
                or (target is caster)
            else ResultType.MISS
        )
        return hit_result

    def build_damage(self, caster: 'Creature', target: 'Creature') -> tuple[int, bool]:
        is_critical = _calc_critical()
        if (self.damage is None) or ((damage_power := self.damage.power) == 0):
            return 0, is_critical

        critical_modifier = (1 + is_critical)
        atk_stats, def_stats = self.damage.stats

        atk2def = (caster.current_stats(atk_stats) / target.current_stats(def_stats))
        basis = (2 * caster.level * critical_modifier / 5) + 2
        damage_value = max(1, int(2 + (basis * damage_power * atk2def / 50)))
        return damage_value, is_critical


def _calc_critical() -> bool:
    return False


def is_a_hit(move_rate: int, caster_accuracy: int, target_evasiveness: int) -> bool:
    if not move_rate:
        return False
    evade_accuracy_mod_ratio = modifier_factor(caster_accuracy) / modifier_factor(target_evasiveness)
    adjusted_hit_rate = move_rate * evade_accuracy_mod_ratio
    return (random.randint(1, 100) <= adjusted_hit_rate)


@dataclass
class Creature:
    name: str = ''
    level: int = 5
    max_health: int = 50
    health: int = max_health

    stats_modifiers: dict[StatsName, int] = field(default_factory=dict, init=False)
    stats: dict[StatsName, int] = field(default_factory=dict)

    moves: dict[MovePos, Move] = field(default_factory=dict)

    def __post_init__(self):
        self.stats_modifiers = {stat_name: 0 for stat_name in self.stats}

    def current_stats(self, stat_name: StatsName) -> int:
        if stat_name == StatsName.HP:
            return self.health
        if stat_name in [StatsName.EVA, StatsName.ACC]:
            return self.stats_modifiers[stat_name]
        base = self.stats[stat_name]
        modifiers_count = self.stats_modifiers[stat_name]
        cs = base * modifier_factor(modifiers_count)
        return int(cs)

    def apply(self, effect: MoveEffect) -> ResultType:
        if (effect.result is ResultType.HIT):
            if effect.damage:
                self.health -= effect.damage
            if effect.alteration:
                self.stats_modifiers[effect.alteration.stats] += effect.alteration.count
        return effect.result


def sign(number: int | float) -> int:
    """Returns the sign of the number, or zero."""
    if number > 0:
        return +1
    if number < 0:
        return -1
    return 0


def modifier_factor(modifiers_count: int) -> float:
    """Produces the following pattern for :param:`modifiers_count`

    modifiers_count | modifier_factor
        -6          |       0.25
        -5          |       0.28
        -4          |       0.33
        -3          |       0.4
        -2          |       0.5
        -1          |       0.66
        0           |       1.0
        +1          |       1.5
        +2          |       2.0
        +3          |       2.5
        +4          |       3.0
        +5          |       3.5
        +6          |       4.0

    The modifier factor cannot consider `abs(modifier_count) > 6`, so a caping
    of `min(6, abs(modifiers_count))` exists within the factor computation.

    :param modifiers_count: total count of modifiers for any stat
    :type modifiers_count: int
    :return: The computed modifier factor for that stat
    :rtype: float
    """
    return (1 + 0.5 * min(6, abs(modifiers_count))) ** sign(modifiers_count)
