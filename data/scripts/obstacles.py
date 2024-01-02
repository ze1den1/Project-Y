import pygame as pg
from data.scripts.sprites import SpriteSheet

screen = pg.display.set_mode((0, 0))
sheet = pg.image.load('data/images/objects/objects.png')
sheet = SpriteSheet(sheet)
IMAGES = []
for _ in range(7):
    image = sheet.cut_image((_ * 64, 0), 64, 64)
    IMAGES.append(image)


class SimpleObject(pg.sprite.Sprite):
    TILE_SIZE = 64

    def __init__(self, game: 'main.Game', obst_type: int, pos_x: int, pos_y: int) -> None:
        super().__init__(game._all_sprites, game._obstacles)
        self.image = IMAGES[obst_type]
        self.rect = self.image.get_rect().move(
            self.TILE_SIZE * pos_x, self.TILE_SIZE * pos_y
        )
