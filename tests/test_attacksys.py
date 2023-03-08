# -*- coding: utf-8 -*-

"""
attack system:

each attack have its power/damage value

it is also affected by some stats and by the nature of the attack: physical or magical

the attack has a success rate, which is also affected by enemy's evasiveness

the attack may be special in the sense of using some character attributes
(height, weight, level) instead of stats (strenght, agility, knowledge) to calculate its damage

it may be a special effect that alters the enemy status

it may causes some condition that will affect the enemy recurrently (confusion, love, etc)

it may be a special condition that affects even outside battle (poison, burn, sleep, etc)
"""

from attacksys.action import cast_move
from attacksys.definitions import (Creature, Damage, Move, MovePos, Nature,
                                   StatsAlteration, StatsName)


def _moves_map_A():
    return {MovePos.FIRST: Move(name='pound',
                                damage=Damage(power=40,
                                              nature=Nature.PHYSICAL)),
            MovePos.SECOND: Move(name='taunt',
                                 alteration=StatsAlteration(stats=StatsName.DEF,
                                                            factor=0.5)),
            MovePos.THIRD: Move(name='howl',
                                alteration=StatsAlteration(stats=StatsName.ATK,
                                                           factor=1.5))}


def _moves_map_B():
    return {MovePos.FIRST: Move(name='tackle',
                                damage=Damage(power=35,
                                              nature=Nature.PHYSICAL)),
            MovePos.SECOND: Move(name='defense curl',
                                 alteration=StatsAlteration(stats=StatsName.DEF,
                                                            factor=1.5)),
            MovePos.THIRD: Move(name='growl',
                                alteration=StatsAlteration(stats=StatsName.ATK,
                                                           factor=0.5))}



def test_pound_inflict_damage_taunt_reduces_defense_howl_increases_attack():
    player = Creature(moves=_moves_map_A())

    cast_move(player, MovePos.FIRST, player)
    assert player.health < player.max_health, "Pound did not reduce health"
        
    cast_move(player, MovePos.SECOND, player)
    assert player.current_stats[StatsName.DEF] < player.stats[StatsName.DEF], "Taunting did not reduce defense"

    cast_move(player, MovePos.THIRD, player)
    assert player.current_stats[StatsName.ATK] > player.stats[StatsName.ATK], "Howling did not increased attack"


def test_physical_damage_is_greater_after_reducing_enemy_defense():
    player = Creature(moves=_moves_map_A())
    enemy = Creature(moves=_moves_map_A())

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
    player = Creature(moves=_moves_map_A())
    enemy = Creature(moves=_moves_map_A())

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
    player = Creature(moves=_moves_map_A())
    enemy = Creature(moves=_moves_map_B())

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
    player = Creature(moves=_moves_map_A())
    enemy = Creature(moves=_moves_map_B())

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
