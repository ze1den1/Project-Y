from enum import Enum
from pprint import pprint

import pygame as pg
pg.init()

TILE_SIZE = 50
obj_dict = {
    0: 'white',
    1: 'black',
    2: 'orange',
    3: 'gray',
    4: 'yellow',
    5: 'blue',
    6: 'red',
    7: 'brown',
    8: 'pink',
    9: 'purple'
}


def read_map(file: str) -> pg.Surface:
    data = []

    with open(file, 'r', encoding='utf-8') as map_file:
        for line in map_file.readlines():
            data.append(list(map(int, line.rstrip('\n').split())))

    lvl_height = len(data) * TILE_SIZE
    lvl_width = len(data[0]) * TILE_SIZE
    lvl_map = pg.Surface((lvl_width, lvl_height))

    for y in range(len(data)):
        for x in range(len(data[0])):
            print(data[y][x])
            pg.draw.rect(lvl_map,
                         obj_dict[data[y][x]],
                         (x * TILE_SIZE, y * TILE_SIZE, x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE + TILE_SIZE))

    return lvl_map
