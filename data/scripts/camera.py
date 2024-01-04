import pygame as pg
from data.scripts.sprites import Hero
pg.init()


class CameraGroup(pg.sprite.Group):
    def __init__(self, game: 'main.Game'):
        super().__init__()
        self.game = game
        self.offset = pg.math.Vector2()
        self.half_w = self.game.MONITOR_W >> 1
        self.half_h = self.game.MONITOR_H >> 1

    def center_camera(self, target: Hero) -> None:
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player: Hero, screen: pg.Surface) -> None:
        self.center_camera(player)
        player.update(screen, self.offset)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)
