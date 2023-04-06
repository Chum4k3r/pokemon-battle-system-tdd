# -*- coding: utf-8 -*-

from functools import lru_cache
from logging import getLogger, StreamHandler, Formatter
import random
from battlesys.action import cast_move
from battlesys.definitions import Creature, Damage, Move, MovePos, Nature, StatsAlteration, StatsName


LOGGER = getLogger(__name__)
LOGGER.setLevel('DEBUG')
FMT = Formatter(fmt='{name} @ {asctime} :: {message}', style='{')
HANDLER = StreamHandler()
HANDLER.setFormatter(FMT)
HANDLER.setLevel('INFO')
LOGGER.addHandler(HANDLER)



def stats_map(**kwargs: int) -> dict[StatsName, int]:
    stats = {
        StatsName[arg.upper()]: value
        for arg, value in kwargs.items()
    }
    stats.update({StatsName.EVA: 0, StatsName.ACC: 0})
    return stats


def moves_map(**kwargs: Move) -> dict[MovePos, Move]:
    moves = {
        MovePos[pos.upper()]: move
        for pos, move in kwargs.items()
    }
    return moves


@lru_cache
def pepper_breath() -> Move:
    return Move(
        name='Pepper Breath',
        hit_rate=90,
        damage=Damage(power=45,
                      nature=Nature.MAGICAL),
        description="A small fire breath."
    )


@lru_cache
def claw_attack() -> Move:
    return Move(
        name='Claw Attack',
        hit_rate=100,
        damage=Damage(power=35,
                      nature=Nature.PHYSICAL),
        alteration_rate=30,
        alteration=StatsAlteration(StatsName.DFN, 1),
        description="Attacks with a cutting claw that may reduce the enemy's defense."
    )


@lru_cache
def blue_blaster() -> Move:
    return Move(
        name='Blue Blaster',
        hit_rate=100,
        damage=Damage(power=35,
                      nature=Nature.MAGICAL),
        alteration_rate=30,
        alteration=StatsAlteration(StatsName.ACC, 1),
        description="A small stream of blue flame. May reduce foe's accuracy."
    )


@lru_cache
def horn_attack() -> Move:
    return Move(
        name='Horn Attack',
        hit_rate=85,
        damage=Damage(power=50,
                      nature=Nature.PHYSICAL),
        description="Attacks with powerful horn."
    )


digimons = dict(
    agumon = Creature(name='Agumon',
                        max_health=26,
                        stats=stats_map(atk=10, dfn=8, sat=9, sdf=7, spd=8),
                        moves=moves_map(first=pepper_breath(), second=claw_attack())),
    gabumon = Creature(name='Gabumon',
                       max_health=22,
                       stats=stats_map(atk=8, dfn=8, sat=10, sdf=9, spd=7),
                       moves=moves_map(first=blue_blaster(), second=horn_attack()))
)


if __name__ == '__main__':
    try:
        LOGGER.info('Bem vindas e bem vindos ao Centro de Batalhas Digimon')
        LOGGER.info('Pressione `ENTER` para continuar...')
        LOGGER.info('Pressione `CTRL + C` para sair.')
        input()
        LOGGER.info('Atualmente dispomos dos seguintes Digimon:')
        input()
        LOGGER.info(f'{repr(digimons["agumon"])}')
        input()
        LOGGER.info(f'{repr(digimons["gabumon"])}')
        input()

        LOGGER.info('Digite o nome do digimon desejado e pressione `ENTER`:')
        player_digimon_name = ''
        while player_digimon_name.lower() not in digimons:
            player_digimon_name = input("Digite o nome e pressione `ENTER`: ")

        player = digimons.pop(player_digimon_name.lower())
        LOGGER.info(f'Selecionado digimon {player.name} para a/o jogadora/')

        enemy = random.choice(list(digimons.values()))
        LOGGER.info(f'Selecionado digimon {enemy.name} para a/o inimiga/')
        input()

        while True:

            LOGGER.info(f"Selecione qual movimento seu {player.name} deve utilizar e pressione `ENTER`")
            for pos, move in player.moves.items():
                print(f"{pos}: {move.name.upper()} -> {move.description}")

            move_pos = ''
            while move_pos not in player.moves:
                move_pos = input(f"Selecione qual movimento seu {player.name} deve utilizar e pressione `ENTER`: ")
                if not move_pos.isnumeric():
                    continue
                move_pos = MovePos(int(move_pos))

            LOGGER.info(f"Selecionado {player.moves.get(move_pos).name}")

            cast_move(player, move_pos, enemy)


    except KeyboardInterrupt:
        print()
        LOGGER.info("Encerrando aplicação")
