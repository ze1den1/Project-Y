import pygame as pg

pg.init()


class SpriteSheet:
    def __init__(self, sheet: pg.Surface):
        self.sheet = sheet
        self.frames = []
        self._last_frame_time = 0.0
        self.cur_frame = 0

    def cut_image(self, pos: tuple[int, int], width: int, height: int,
                  new_size: tuple[int, int] or None = None, scale: int = 1) -> pg.Surface:
        """Scale parameter is optional. Add it if you want to increase your image by the scale
        (Also working with new_size)"""
        image = pg.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), area=(pos[0], pos[1], width, height))
        if new_size is not None:
            image = pg.transform.scale(image, (new_size[0] * scale, new_size[1] * scale))
        else:
            image = pg.transform.scale(image, (width * scale, height * scale))

        return image

    def get_frames(self, row: int, width: int, height: int, frames: int,
                   new_size: tuple[int, int] or None = None, scale: int = 1) -> list[pg.Surface]:
        self.frames = [self.cut_image((0 + width * i, height * row), width, height,
                                      new_size=new_size, scale=scale) for i in range(frames)]

        return self.frames


class Hero(pg.sprite.Sprite):
    image = pg.image.load('data/images/creatures/hero.png')
    MAX_SPEED = 400
    MIN_SPEED = 200

    def __init__(self, game: 'main.Game', position: tuple[int, int], fps: int) -> None:
        super().__init__(game._all_sprites)
        self.game = game
        self.rect = self.image.get_rect(center=position)
        self.pos = list(self.rect.center)
        self.fps = fps
        self.speed = 200
        self.direction = pg.math.Vector2()

        self._hp = 100

    def get_hp(self) -> int:
        return self._hp

    def update_direction(self) -> None:
        keys = pg.key.get_pressed()

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.direction.y = -1
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.direction.x = 1
        elif keys[pg.K_LEFT] or keys[pg.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self) -> None:
        self.update_direction()
        old_pos = self.pos.copy()

        self.pos += (self.speed * self.direction) / self.fps
        self.rect.center = self.pos

        if pg.sprite.spritecollideany(self, self.game._obstacles):
            self.pos = old_pos

        self.rect.center = self.pos
        if (self.speed < self.MAX_SPEED
                and (self.direction.x != 0 or self.direction.y != 0)):
            self.speed += 100 / self.fps
        elif self.direction.x == 0 and self.direction.y == 0 and self.speed > self.MIN_SPEED:
            self.speed -= 400 / self.fps


class Enemies:
    def __init__(self):
        pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - pg.display.Info().current_w // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - pg.display.Info().current_h // 2)