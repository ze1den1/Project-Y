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


loot_items = SpriteSheet(pg.image.load('data/images/objects/inventory_items.png'))


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

    def check_position(self, player) -> bool:
        player_rect = player.rect
        if (self.rect.top - 80 < player_rect.centery < self.rect.bottom + 70
                and self.rect.left - 80 < player_rect.centerx < self.rect.right + 70):
            return True
        return False

    def hit(self, game: 'main.Game', pos: tuple[int, int]):
        create_sparks(game, pos, 600, self.MATERIAL)
        self._hp -= 1
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

    @staticmethod
    def show_hint(game: 'main.Game', coords: tuple[int, int], screen: pg.Surface) -> None:
        hint = DefaultButton(coords, 150, 100, game.HINT_BUTTON,
                             text='space', text_size=30)
        hint.draw(screen)

    def open_chest(self) -> None:
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            self.is_open = True
            self.image = self.game.CHEST_OPEN
            for i in range(random.randrange(1, 5)):
                direction = random.randrange(1, 5)
                if direction == 1:
                    Loot(self.game, 4, (self.rect.centerx + random.randrange(-30, 30),
                                        self.rect.centery + random.randrange(-80, -50)))
                elif direction == 2:
                    Loot(self.game, 4, (self.rect.centerx + random.randrange(50, 80),
                                        self.rect.centery + random.randrange(-30, 30)))
                elif direction == 3:
                    Loot(self.game, 4, (self.rect.centerx + random.randrange(-30, 30),
                                        self.rect.centery + random.randrange(50, 80)))
                else:
                    Loot(self.game, 4, (self.rect.centerx + random.randrange(-80, -50),
                                        self.rect.centery + random.randrange(-30, 30)))


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
             loot_items.cut_image((0, 16), 16, 16, new_size=(24, 24), colorkey=(0, 0, 0))]

    def __init__(self, game: 'main.Game', loot_type: int, pos: tuple[int, int]):
        super().__init__(game._picked, game._camera_group, game._all_sprites)
        self.image = self.ITEMS[loot_type]
        self.rect = self.image.get_rect(center=pos)
        self.loot_type = loot_type
