from enum import IntEnum

import pygame as pg
from data.scripts.sprites import SpriteSheet
from data.scripts.particles import create_sparks, Materials
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


LOOT_NAMES = {0: 'copper', 1: 'iron', 2: 'ruby', 3: 'sapphire'}
loot_items = SpriteSheet(pg.image.load('data/images/objects/inventory_items.png'))
sheet = SpriteSheet(pg.image.load('data/images/UI/UI-perks.png'))


class SimpleObject(pg.sprite.Sprite):
    TILE_SIZE = 72
    MATERIAL = Materials.ROCK

    def __init__(self, game: 'main.Game', obst_type: int, pos_x: int, pos_y: int, *groups) -> None:
        super().__init__(game._camera_group, game._obstacles, game._all_sprites, *groups)
        if obst_type == Objects.ROCK:
            self.image = random.choice(game.ROCKS)
        elif Objects.COPPER <= obst_type <= Objects.SAPPHIRE:
            self.image = game.ORES[obst_type - 1]
        elif obst_type == Objects.CHEST:
            self.image = game.CHEST_CLOSED
        elif obst_type == Objects.CRATE:
            self.image = game.CRATE
        self.rect = self.image.get_rect().move(
            self.TILE_SIZE * pos_x, self.TILE_SIZE * pos_y
        )
        self._obst_type = obst_type
        self._hp = 3
        self.game = game

    def hit(self, game: 'main.Game', pos: tuple[int, int], hit: int):
        create_sparks(game, pos, 600, self.MATERIAL)
        self._hp -= hit
        self.check_brake()

    def check_brake(self) -> None:
        if self._hp <= 0:
            self.kill()
            self.drop_loot()

    def drop_loot(self) -> None:
        if Objects.COPPER <= self._obst_type <= Objects.SAPPHIRE:
            Loot(self.game, self._obst_type - 1, self.rect.center)


class Chest(SimpleObject):
    def __init__(self, game: 'main.Game', pos_x: int, pos_y: int, *groups):
        super().__init__(game, Objects.CHEST, pos_x, pos_y, *groups)
        self.is_open = False
        self.game = game

    def open_chest(self) -> None:
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            rand_num = random.randrange(1, 101)
            if 1 <= rand_num <= 25:
                self._spawn_loot(5, 1)
            else:
                self._spawn_loot(4, 5)
            self.is_open = True
            self.image = self.game.CHEST_OPEN

    def _spawn_loot(self, loot_type: int, max_count: int) -> None:
        for i in range(random.randrange(1, max_count + 1)):
            direction = random.randrange(1, 5)
            if direction == 1:
                x1, x2 = -30, 30
                y1, y2 = -80, -50
            elif direction == 2:
                x1, x2 = 50, 80
                y1, y2 = -30, 30
            elif direction == 3:
                x1, x2 = -30, 30
                y1, y2 = 50, 80
            else:
                x1, x2 = -80, -50
                y1, y2 = -30, 30
            loot = Loot(self.game, loot_type, (self.rect.centerx + random.randrange(x1, x2),
                                               self.rect.centery + random.randrange(y1, y2)))
            while True:
                if pg.sprite.spritecollideany(loot, self.game._obstacles):
                    x1 -= 5
                    x2 += 5
                    y1 -= 5
                    x2 += 5
                    loot.rect.topleft = (self.rect.centerx + random.randrange(x1, x2),
                                         self.rect.centery + random.randrange(y1, y2))
                else:
                    break


class Crate(SimpleObject):
    MATERIAL = Materials.WOOD

    def __init__(self, game: 'main.Game', pos_x: int, pos_y: int, *groups) -> None:
        super().__init__(game, Objects.CRATE, pos_x, pos_y, *groups)
        self._hp = 2
        self.game = game

    def drop_loot(self) -> None:
        for i in range(random.randrange(1, 3)):
            Loot(self.game, 4, (self.rect.centerx + random.randrange(-10, 10),
                                self.rect.centery + random.randrange(-10, 10)))


class Border(pg.sprite.Sprite):
    def __init__(self, game: 'main.Game', x1: int, x2: int, y1: int, y2: int) -> None:
        super().__init__(game._obstacles, game._all_sprites)
        if x1 == x2:
            self.image = pg.Surface((1, y2 - y1))
            self.rect = pg.Rect(x1, y1, 1, y2 - y1)
        else:
            self.image = pg.Surface((x2 - x1, 1))
            self.rect = pg.Rect(x1, y1, x2 - x1, 1)


class Loot(pg.sprite.Sprite):
    ITEMS = [loot_items.cut_image((0, 0), 15, 16, new_size=(24, 24), colorkey=(0, 0, 0)),
             loot_items.cut_image((16, 0), 16, 16, new_size=(24, 24), colorkey=(0, 0, 0)),
             loot_items.cut_image((32, 0), 16, 16, new_size=(24, 24), colorkey=(0, 0, 0)),
             loot_items.cut_image((48, 0), 16, 16, new_size=(24, 24), colorkey=(0, 0, 0)),
             loot_items.cut_image((0, 16), 16, 16, new_size=(24, 24), colorkey=(0, 0, 0)),
             sheet.cut_image((160, 0), 32, 32, new_size=(24, 24), colorkey=(0, 0, 0))]

    def __init__(self, game: 'main.Game', loot_type: int, pos: tuple[int, int]):
        super().__init__(game._picked, game._camera_group, game._all_sprites)
        self.image = self.ITEMS[loot_type]
        self.rect = self.image.get_rect(center=pos)
        self.loot_type = loot_type
        if loot_type != 4 and loot_type != 5:
            self.name = LOOT_NAMES[loot_type]
