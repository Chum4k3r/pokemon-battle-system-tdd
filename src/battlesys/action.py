# -*- coding: utf-8 -*-


from battlesys.definitions import Creature, MovePos


def cast_move(caster: Creature, move_pos: MovePos, target: Creature):
    move = caster.moves[move_pos]
    move_effect = move.effect(caster, target)
    target.apply(move_effect)
