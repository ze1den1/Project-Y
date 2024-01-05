from enum import IntEnum

import pygame as pg
from data.scripts.sprites import SpriteSheet, Hero
from data.scripts.UI import DefaultButton
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

    def __init__(self, game: 'main.Game', obst_type: int, pos_x: int, pos_y: int, *groups) -> None:
        super().__init__(game._camera_group, game._obstacles, game._all_sprites, *groups)
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
        self._hp = 3

    def check_position(self, player) -> bool:
        player_rect = player.rect
        if (self.rect.top - 80 < player_rect.centery < self.rect.bottom + 70
                and self.rect.left - 80 < player_rect.centerx < self.rect.right + 70):
            return True
        return False

    def hit(self):
        pass

    def check_brake(self) -> None:
        if self._hp <= 0:
            self.kill()


class Chest(SimpleObject):
    def __init__(self, game: 'main.Game', pos_x: int, pos_y: int, *groups):
        super().__init__(game, Objects.CHEST, pos_x, pos_y, *groups)

    @staticmethod
    def show_hint(coords: tuple[int, int], screen: pg.Surface) -> None:
        hint = DefaultButton(coords, 150, 100, 'hint_btn.png',
                             text='space', text_size=30)
        hint.draw(screen)

    def open_chest(self) -> None:
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            self.image = CHEST_OPEN
            
            
class Crate(SimpleObject):
    def __init__(self, game: 'main.Game', pos_x: int, pos_y: int, *groups) -> None:
        super().__init__(game, Objects.CRATE, pos_x, pos_y, *groups)


class Border(pg.sprite.Sprite):
    def __init__(self, game: 'main.Game', x1: int, x2: int, y1: int, y2: int) -> None:
        super().__init__(game._obstacles, game._all_sprites)
        if x1 == x2:
            self.image = pg.Surface((1, y2 - y1))
            self.rect = pg.Rect(x1, y1, 1, y2 - y1)
        else:
            self.image = pg.Surface((x2 - x1, 1))
            self.rect = pg.Rect(x1, y1, x2 - x1, 1)
