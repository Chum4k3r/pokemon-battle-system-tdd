# -*- coding: utf-8 -*-


from battlesys.definitions import Creature, MovePos, ResultType


def cast_move(caster: Creature, move_pos: MovePos, target: Creature) -> ResultType:
    move = caster.moves[move_pos]
    move_effect = move.effect(caster, target)
    result = target.apply(move_effect)
    return result
