import pygame as pg

pg.init()
TILE_SIZE = 72


def get_map_data(file: str) -> tuple[list, dict]:
    with open(file, 'r', encoding='utf-8') as map_file:
        data = [line.strip() for line in map_file]

    conditions = data[data.index('') + 1:]
    conditions_dict = {}
    data = data[:data.index('')]

    for condition in conditions:
        condition = condition.split()
        conditions_dict[condition[0]] = int(condition[1])

    max_width = max(map(len, data))
    data = list(map(lambda x: list(x.ljust(max_width, '.')), data))
    return data, conditions_dict


def get_player_pos(data: list[list]) -> tuple[int, int] or None:
    for line in range(len(data)):
        if '@' in data[line]:
            x = data[line].index('@') * TILE_SIZE + (TILE_SIZE >> 1)
            y = line * TILE_SIZE + (TILE_SIZE >> 1)
            return x, y
