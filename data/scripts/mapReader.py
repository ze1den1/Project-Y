from enum import Enum
import pygame as pg

pg.init()
TILE_SIZE = 64


class Objects(Enum):
    ROCK = 0
    COPPER = 1
    IRON = 2
    RUBY = 3
    SAPPHIRE = 4
    CRATE = 5
    BARREL = 6

    PLAYER = '@'


obj_dict = {
    0: 'black',
    1: 'orange',
    2: 'gray',
    3: 'red',
    4: 'blue',
    5: 'brown',
    6: 'brown'
}


def get_map_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as map_file:
        data = [line.strip() for line in map_file]

    max_width = max(map(len, data))
    data = list(map(lambda x: list(x.ljust(max_width, '.')), data))
    return data


def get_player_pos(data: list[list]) -> tuple[int, int] or None:
    for line in range(len(data)):
        if '@' in data[line]:
            x = data[line].index('@') * TILE_SIZE + (TILE_SIZE >> 1)
            y = line * TILE_SIZE + (TILE_SIZE >> 1)
            return x, y
