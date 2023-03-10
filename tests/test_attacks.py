# -*- coding: utf-8 -*-

"""
attack system:

each attack have its power/damage value (DONE)

it is also affected by some stats and by the nature of the attack: physical or magical (DONE)

the attack has a success rate, which is also affected by enemy's evasiveness

the attack may be special in the sense of using some character attributes
(height, weight, level) instead of stats (strenght, agility, knowledge) to calculate its damage

it may be a special effect that alters the enemy status

it may causes some condition that will affect the enemy recurrently (confusion, love, etc)

it may be a special condition that affects even outside battle (poison, burn, sleep, etc)
"""

from battlesys.action import cast_move
from battlesys.definitions import (Creature, Damage, Move, MovePos, Nature,
                                   StatsAlteration, StatsName)


def _pound_move() -> Move:
    return Move(name='pound',
                damage=Damage(power=40,
                              nature=Nature.PHYSICAL),
                hit_rate=100)


def _howl_move() -> Move:
    return Move(name='howl',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.ATK,
                                           factor=1.5),
                alteration_rate=100)


def _taunt_move() -> Move:
    return Move(name='taunt',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.DEF,
                                           factor=0.5),
                alteration_rate=100)


def _growl_move()-> Move:
    return Move(name='growl',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.ATK,
                                           factor=0.5),
                alteration_rate=100)


def _defense_curl_move() -> Move:
    return Move(name='defense curl',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.DEF,
                                           factor=1.5),
                alteration_rate=100)


def _tackle_move() -> Move:
    return Move(name='tackle',
                hit_rate=100,
                damage=Damage(power=35,
                              nature=Nature.PHYSICAL))



def _moves_map_A() -> dict[MovePos, Move]:
    return {MovePos.FIRST: _pound_move(),
            MovePos.SECOND: _taunt_move(),
            MovePos.THIRD: _howl_move()}


def _moves_map_B() -> dict[MovePos, Move]:
    return {MovePos.FIRST: _tackle_move(),
            MovePos.SECOND: _defense_curl_move(),
            MovePos.THIRD: _growl_move()}



def _stats_mapping_A():
    return {
        StatsName.ATK: 8,
        StatsName.DEF: 8,
        StatsName.SAT: 11,
        StatsName.SDF: 9,
        StatsName.SPD: 10,
        StatsName.EVA: 0,
        StatsName.ACC: 0,
    }


def _stats_mapping_B():
    return {
        StatsName.ATK: 11,
        StatsName.DEF: 9,
        StatsName.SAT: 8,
        StatsName.SDF: 8,
        StatsName.SPD: 10,
        StatsName.EVA: 0,
        StatsName.ACC: 0,
    }


def test_pound_inflict_damage_taunt_reduces_defense_howl_increases_attack():
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())

    cast_move(player, MovePos.FIRST, player)
    assert player.health < player.max_health, "Pound did not reduce health"
        
    cast_move(player, MovePos.SECOND, player)
    assert player.current_stats[StatsName.DEF] < player.stats[StatsName.DEF], "Taunting did not reduce defense"

    cast_move(player, MovePos.THIRD, player)
    assert player.current_stats[StatsName.ATK] > player.stats[StatsName.ATK], "Howling did not increased attack"


def test_physical_damage_is_greater_after_reducing_enemy_defense():
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())
    enemy = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())

    # Player wants to cast POUND on enemy
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_before_taunt = enemy.max_health - enemy.health

    # Then, player TAUNTs the enemy, to reduce defense    
    cast_move(player, MovePos.SECOND, enemy)

    # reset health for easy comparison
    enemy.health = enemy.max_health

    # The Player cast POUND on enemy again
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_after_taunt = enemy.max_health - enemy.health
    assert delta_health_after_taunt > delta_health_before_taunt, "Decreasing DEF made no difference on damage."


def test_physical_damage_is_greater_after_increasing_caster_attack():
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())
    enemy = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())

    # Player wants to cast POUND on enemy
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_before_boost = enemy.max_health - enemy.health

    # Then, player BOOSTs itself, to increase attack    
    cast_move(player, MovePos.THIRD, player)

    # reset health for easy comparison
    enemy.health = enemy.max_health

    # The Player cast POUND on enemy again
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_after_boost = enemy.max_health - enemy.health

    assert delta_health_after_boost > delta_health_before_boost, "Increasing ATK made no difference on damage"


def test_physical_damage_is_lower_after_increasing_enemy_defense():
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())
    enemy = Creature(moves=_moves_map_B(), stats=_stats_mapping_A())

    # Player wants to cast POUND on enemy
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_before_curl = enemy.max_health - enemy.health

    # Then, enemy CURLs itself to increase defense    
    cast_move(enemy, MovePos.SECOND, enemy)

    # reset health for easy comparison
    enemy.health = enemy.max_health

    # The Player cast POUND on enemy again
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_after_curl = enemy.max_health - enemy.health
    assert delta_health_after_curl < delta_health_before_curl, "Increasing DEF made no difference on damage."


def test_physical_damage_is_lower_after_reducing_player_attack():
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_A())
    enemy = Creature(moves=_moves_map_B(), stats=_stats_mapping_A())

    # Player wants to cast POUND on enemy
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_before_growl = enemy.max_health - enemy.health

    # Then, enemy GROWLs at player to reduce its attack    
    cast_move(enemy, MovePos.THIRD, player)

    # reset health for easy comparison
    enemy.health = enemy.max_health

    # The Player cast POUND on enemy again
    cast_move(player, MovePos.FIRST, enemy)

    # POUNDing the enemy reduces a certain amount of HP
    delta_health_after_growl = enemy.max_health - enemy.health
    assert delta_health_after_growl < delta_health_before_growl, "Increasing DEF made no difference on damage."
