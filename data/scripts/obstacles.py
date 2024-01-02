import pygame as pg
import os

FILENAMES = ('stone.png', 'copper.png', 'iron.png', 'ruby.png', 'sapphire.png', 'crate.png', 'barrel.png')


class SimpleObject(pg.sprite.Sprite):
    IMAGES = [pg.image.load(os.path.join('data', 'images', 'objects', FILENAMES[i])) for i in range(7)]
    TILE_SIZE = 64

    def __init__(self, game: 'main.Game', obst_type: int, pos_x: int, pos_y: int) -> None:
        super().__init__(game._all_sprites, game._obstacles)
        self.image = self.IMAGES[obst_type]
        self.rect = self.image.get_rect().move(
            self.TILE_SIZE * pos_x, self.TILE_SIZE * pos_y
        )
