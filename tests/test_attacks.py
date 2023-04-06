# -*- coding: utf-8 -*-

"""
attack system:

each attack have its power/damage value (DONE)

it is also affected by some stats and by the nature of the attack: physical or magical (DONE)

it may be a special effect that alters the enemy stats (DONE)

Status alterations can be stacked up to 6 modificators (DONE)

    The current stats values are a product of the base stats and the stats modifier factor (DONE)

the attack has a success rate, which is also affected by enemy's evasiveness

the attack may be special in the sense of using some character attributes
(height, weight, level) instead of stats (strenght, agility, knowledge) to calculate its damage

it may causes some condition that will affect the enemy recurrently (confusion, love, etc)

it may be a special condition that affects even outside battle (poison, burn, sleep, etc)
"""

from battlesys.action import cast_move
from battlesys.definitions import (Creature, Damage, Move, MovePos, Nature, ResultType,
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
                                           count=1),
                alteration_rate=100)


def _taunt_move() -> Move:
    return Move(name='taunt',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.DEF,
                                           count=-1),
                alteration_rate=100)


def _growl_move()-> Move:
    return Move(name='growl',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.ATK,
                                           count=-1),
                alteration_rate=100)


def _defense_curl_move() -> Move:
    return Move(name='defense curl',
                hit_rate=100,
                alteration=StatsAlteration(stats=StatsName.DEF,
                                           count=1),
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
    assert player.current_stats(StatsName.DEF) < player.stats[StatsName.DEF], "Taunting did not reduce defense"

    cast_move(player, MovePos.THIRD, player)
    assert player.current_stats(StatsName.ATK) > player.stats[StatsName.ATK], "Howling did not increased attack"


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


def test_move_with_zero_rate_always_miss() -> None:
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_B())

    player.moves[MovePos.FIRST].hit_rate = 0
    cast_move(player, MovePos.FIRST, player)

    assert player.health == player.max_health


def test_stats_modifiers_cannot_be_applied_more_than_6_times():
    """Sometimes we may overuse some stats alteration move, and the battle system prevents
    from using it more than 6 times.

    This requires some sort of counter to keep track of how many alterations have been used for
    the same stats.

    Lets say, 7 or 8 attack boosts should give the maximum bonus of only 6 boosts.

    We will assume a starting value of 0, with -6 being the bottom count and +6 the top count

    A positive sign indicates a status increase, and a negative sign indicates a status decrease.

    ----
    Overall note: This feature will be key for the evasion/accuracy interface of hit probability
    on a further development.
    """
    player = Creature(moves=_moves_map_A(), stats=_stats_mapping_B())

    for _ in range(6):
        # player howls 6 times in a row:
        cast_move(player, MovePos.THIRD, player)

    atk_stats_after_6_howls = player.current_stats(StatsName.ATK)

    # howls a 7th time
    cast_move(player, MovePos.THIRD, player)

    atk_stats_after_7_howls = player.current_stats(StatsName.ATK)

    assert atk_stats_after_7_howls == atk_stats_after_6_howls

    # howls an 8th time
    cast_move(player, MovePos.THIRD, player)

    atk_stats_after_8_howls = player.current_stats(StatsName.ATK)

    assert atk_stats_after_8_howls == atk_stats_after_6_howls


def test_using_stats_alteration_alters_stats_modifiers_count_for_status():
    player = Creature(stats=_stats_mapping_A(), moves=_moves_map_A())
    enemy = Creature(stats=_stats_mapping_B(), moves=_moves_map_B())

    cast_move(player, MovePos.THIRD, player)
    assert player.stats_modifiers[StatsName.ATK] == 1
    assert player.current_stats(StatsName.ATK) > player.stats[StatsName.ATK]

    cast_move(player, MovePos.THIRD, player)
    cast_move(player, MovePos.THIRD, player)
    assert player.stats_modifiers[StatsName.ATK] == 3
    player_atk_3_mods = player.current_stats(StatsName.ATK)

    cast_move(enemy, MovePos.THIRD, player)
    assert player.stats_modifiers[StatsName.ATK] == 2
    player_atk_2_mods = player.current_stats(StatsName.ATK)

    assert player_atk_3_mods > player_atk_2_mods


def test_higher_evasion_avoids_more_hits():
    player = Creature(stats=_stats_mapping_A(),
                      moves={MovePos.FIRST: _pound_move(),
                             MovePos.SECOND: Move(name='sleek body',
                                                  hit_rate=100,
                                                  alteration=StatsAlteration(stats=StatsName.EVA, count=1),
                                                  alteration_rate=100)})
    enemy = Creature(stats=_stats_mapping_B(),
                     moves={MovePos.FIRST: Move(name='fake hit',
                                                hit_rate=100,
                                                damage=Damage(power=0, nature=Nature.PHYSICAL))})

    desired_results = [ResultType.MISS, ResultType.EVAD]
    total_casts_count = 100

    evasions_before_raising_evasiveness_ratio = _results_ratio(enemy, MovePos.FIRST, player, desired_results, total_casts_count)

    # RAISE EVASIVENESS
    ensure_cast_on_self(player, MovePos.SECOND)
    assert player.stats_modifiers[StatsName.EVA] == 1
    assert player.current_stats(StatsName.EVA) > player.stats[StatsName.EVA]

    evasions_after_raising_1_evasiveness_ratio = _results_ratio(enemy, MovePos.FIRST, player, desired_results, total_casts_count)

    assert evasions_after_raising_1_evasiveness_ratio > evasions_before_raising_evasiveness_ratio

    # SHARPLY RAISE EVASIVENESS
    ensure_cast_on_self(player, MovePos.SECOND)
    ensure_cast_on_self(player, MovePos.SECOND)
    assert player.stats_modifiers[StatsName.EVA] == 3
    assert player.current_stats(StatsName.EVA) > player.stats[StatsName.EVA]

    evasions_after_raising_3_evasiveness_ratio = _results_ratio(enemy, MovePos.FIRST, player, desired_results, total_casts_count)

    assert evasions_after_raising_3_evasiveness_ratio > evasions_before_raising_evasiveness_ratio
    assert evasions_after_raising_3_evasiveness_ratio > evasions_after_raising_1_evasiveness_ratio

def ensure_cast_on_self(caster: Creature, move_pos: MovePos) -> ResultType:
    result = ResultType.MISS
    while result is not ResultType.HIT:
        result = cast_move(caster, move_pos, caster)


def _results_ratio(caster: Creature, move_pos: MovePos, target: Creature, desired_results: list[ResultType], total_results: int) -> float:
    return sum(
        (cast_move(caster, move_pos, target) in desired_results)
        for _ in range(total_results)
    ) / total_results
