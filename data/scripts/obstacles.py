from enum import IntEnum

import pygame as pg
from data.scripts.sprites import SpriteSheet
import random


class Objects(IntEnum):
    ROCK = 0
    COPPER = 1
    IRON = 2
    RUBY = 3
    SAPPHIRE = 4
    CHEST = 5
    CRATE = 6


screen = pg.display.set_mode((0, 0))
sheet = pg.image.load('data/images/objects/obstacles.png')
sheet = SpriteSheet(sheet)
ROCKS = [sheet.cut_image((0, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
         sheet.cut_image((16, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
         sheet.cut_image((32, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))]
ORES = [sheet.cut_image((0, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
        sheet.cut_image((16, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
        sheet.cut_image((32, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
        sheet.cut_image((48, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))]
CRATE = sheet.cut_image((0, 32), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))
CHEST_CLOSED = sheet.cut_image((0, 48), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))
CHEST_OPEN = sheet.cut_image((16, 48), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))


class SimpleObject(pg.sprite.Sprite):
    TILE_SIZE = 72

    def __init__(self, game: 'main.Game', obst_type: int, pos_x: int, pos_y: int) -> None:
        super().__init__(game._all_sprites, game._obstacles)
        if obst_type == Objects.ROCK:
            self.image = random.choice(ROCKS)
        elif Objects.COPPER <= obst_type <= Objects.SAPPHIRE:
            self.image = ORES[obst_type - 1]
        elif obst_type == Objects.CHEST:
            self.image = CHEST_CLOSED
        elif obst_type == Objects.CRATE:
            self.image = CRATE
        self.rect = self.image.get_rect().move(
            self.TILE_SIZE * pos_x, self.TILE_SIZE * pos_y
        )
