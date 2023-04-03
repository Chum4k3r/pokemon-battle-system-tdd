# -*- coding: utf-8 -*-

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
    DEF = 'defense'
    SAT = 'special attack'
    SDF = 'special defense'
    SPD = 'speed'


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


@dataclass
class Damage:
    power: int
    nature: Nature

    def stats_by_nature(self) -> tuple[StatsName, StatsName]:
        if self.nature is Nature.PHYSICAL:
            return StatsName.ATK, StatsName.DEF
        if self.nature is Nature.MAGICAL:
            return StatsName.SAT, StatsName.SDF
        else:
            raise InvalidNatureError(self.nature)



@dataclass
class MoveEffect:
    damage: int = 0
    alteration: StatsAlteration | None = None
    condition: Condition | None = None


@dataclass
class Move:
    name: str = ""

    hit_rate: int = 0

    damage: Damage | None = None

    alteration: StatsAlteration | None = None
    alteration_rate: int = 0

    condition: Condition | None = None
    condition_rate: int = 0

    def effect(self, caster: 'Creature', target: 'Creature') -> MoveEffect:
        _effect = MoveEffect()

        is_a_hit = random.randint(1, 100) <= self.hit_rate

        alteration_hit = random.randint(1, 100) <= self.alteration_rate
        critical = 1 #+ (random.random() >= 0.8)

        if is_a_hit and (self.damage is not None):
            atk_stats, def_stats = self.damage.stats_by_nature()
            atk2def = (caster.current_stats(atk_stats) / target.current_stats(def_stats))
            basis = (2 * caster.level * critical / 5) + 2
            damage = (basis * self.damage.power * atk2def / 50) + 2
            _effect.damage = max(1, int(damage))
        if alteration_hit and (self.alteration is not None):
            _effect.alteration = self.alteration
        return _effect


@dataclass
class Creature:
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

    def apply(self, effect: MoveEffect):
        if effect.damage:
            self.health -= effect.damage
        if effect.alteration:
            self.stats_modifiers[effect.alteration.stats] += effect.alteration.count


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
