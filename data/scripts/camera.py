import pygame as pg
from data.scripts.sprites import Hero, Enemies

pg.init()


class CameraGroup(pg.sprite.Group):
    def __init__(self, game: 'main.Game'):
        super().__init__()
        self.game = game
        self.offset = pg.math.Vector2()
        self.half_w = self.game.MONITOR_W >> 1
        self.half_h = self.game.MONITOR_H >> 1

        self._ground_surf = pg.Surface((3000, 3000))
        self._ground_rect = self._ground_surf.get_rect(topleft=(0, 0))

    def set_bg(self, image: pg.Surface) -> None:
        self._ground_surf = image
        self._ground_rect = self._ground_surf.get_rect(topleft=(0, 0))

    def center_camera(self, target: Hero) -> None:
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def get_offset(self, target: Hero) -> pg.Vector2:
        self.center_camera(target)
        return self.offset

    def custom_draw(self, player: Hero, screen: pg.Surface, money_counter, store: tuple[pg.Surface, pg.Rect],
                    is_win: bool = False) -> None:
        self.center_camera(player)

        ground_offset = self._ground_rect.topleft - self.offset
        screen.blit(self._ground_surf, ground_offset)

        store_img, store_rect = store
        store_offset = store_rect.topleft - self.offset
        screen.blit(store_img, store_offset)

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            if not (is_win and isinstance(sprite, Enemies)):
                screen.blit(sprite.image, offset_pos)
        if is_win:
            player.draw(screen)
        else:
            player.update(screen, self.offset, money_counter)
