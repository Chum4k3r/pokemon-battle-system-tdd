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
    STR = 'strength'
    AGI = 'agility'
    CON = 'constitution'
    INT = 'intelligence'
    CHA = 'charisma'
    LUK = 'luckiness'
    EVA = 'evasiveness'
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
    factor: float


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
    alteration: StatsAlteration = None
    condition: Condition = None


@dataclass
class Move:
    name: str = ""
    
    damage: Damage = None
    damage_rate: int = 0

    alteration: StatsAlteration = None
    alteration_rate: int = 0

    condition: Condition = None
    condition_rate: int = 0
    
    def effect(self, caster: 'Creature', target: 'Creature') -> MoveEffect:
        _effect = MoveEffect()
        critical = 1 #+ (random.random() >= 0.8)
        if self.damage:
            atk2def = self.atk_2_def_ratio(caster, target)
            basis = (2 * caster.level * critical / 5) + 2
            damage = (basis * self.damage.power * atk2def / 50) + 2
            _effect.damage = max(1, damage)
        if self.alteration:
            _effect.alteration=self.alteration
        return _effect

    def atk_2_def_ratio(self, caster: 'Creature', target: 'Creature'):
        atk_stats, def_stats = self.damage.stats_by_nature()
        atk2def_ratio = (caster.current_stats[atk_stats] / target.current_stats[def_stats])
        return atk2def_ratio


def _stats_mapping():
    return {
        "attack": 8,
        "defense": 8
    }


@dataclass
class Creature:
    level: int = 5
    max_health: int = 50
    health: int = max_health
    
    current_stats: dict = field(default_factory=_stats_mapping)
    stats: dict[StatsName, int] = field(default_factory=_stats_mapping)
    
    moves: dict[MovePos, Move] = field(default_factory=dict)

    def apply(self, effect: MoveEffect):
        if effect.damage:
            self.health -= effect.damage
        if effect.alteration:
            self.current_stats[effect.alteration.stats] *= effect.alteration.factor
