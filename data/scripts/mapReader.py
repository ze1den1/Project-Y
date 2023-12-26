from enum import Enum

import pygame as pg

pg.init()
BACKGROUND = (255, 255, 255)


class Objects(Enum):
    ROCK = 0
    COPPER = 1
    IRON = 2
    RUBY = 3
    SAPPHIRE = 4
    CRATE = 5
    BARREL = 6

    PLAYER = '@'


TILE_SIZE = 50
obj_dict = {
    0: 'black',
    1: 'orange',
    2: 'gray',
    3: 'red',
    4: 'blue',
    5: 'brown',
    6: 'brown'
}


def read_map(file: str) -> pg.Surface:
    with open(file, 'r', encoding='utf-8') as map_file:
        data = [line.strip() for line in map_file]

    max_width = max(map(len, data))
    data = list(map(lambda x: list(x.ljust(max_width, '.')), data))

    lvl_height = len(data) * TILE_SIZE
    lvl_width = len(data[0]) * TILE_SIZE
    lvl_map = pg.Surface((lvl_width, lvl_height))
    lvl_map.fill(BACKGROUND)

    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x].isdigit():
                pg.draw.rect(lvl_map,
                             obj_dict[int(data[y][x])],
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif data[y][x] == Objects.PLAYER:
                pass  # TODO set player position
    return lvl_map
