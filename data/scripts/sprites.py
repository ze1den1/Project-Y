import pygame as pg

pg.init()


class SpriteSheet:
    def __init__(self, sheet: pg.Surface):
        self.sheet = sheet
        self.frames = []
        self._last_frame_time = 0.0
        self.cur_frame = 0

    def cut_image(self, pos: tuple[int, int], width: int, height: int,
                  new_size: tuple[int, int] or None = None, scale: int = 1,
                  colorkey: tuple[int, int, int] or str = None) -> pg.Surface:
        """Scale parameter is optional. Add it if you want to increase your image by the scale
        (Also working with new_size)"""
        image = pg.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), area=(pos[0], pos[1], width, height))
        if new_size is not None:
            image = pg.transform.scale(image, (new_size[0] * scale, new_size[1] * scale))
        else:
            image = pg.transform.scale(image, (width * scale, height * scale))

        if colorkey is not None:
            image.set_colorkey(colorkey)

        return image

    def get_frames(self, row: int, width: int, height: int, frames: int,
                   new_size: tuple[int, int] or None = None, scale: int = 1,
                   colorkey: tuple[int, int, int] or str = None) -> list[pg.Surface]:
        self.frames = [self.cut_image((0 + width * i, height * row), width, height,
                                      new_size=new_size, scale=scale, colorkey=colorkey) for i in range(frames)]

        return self.frames


class Hero(pg.sprite.Sprite):
    image = pg.Surface((24, 24))
    MAX_SPEED = 400
    MIN_SPEED = 200

    def __init__(self, game: 'main.Game', position: tuple[int, int], fps: int,
                 animation_speed: float, idle_animation: list[pg.Surface], move_animation: list[pg.Surface]) -> None:
        super().__init__(game._all_sprites, game._creatures)
        self.fps = fps
        self.game = game

        self.rect = self.image.get_rect(center=position)
        self.pos = list(self.rect.center)
        self.speed = 200
        self.direction = pg.math.Vector2()
        self._is_move = False

        self._last_frame_time = 0.0
        self._cur_frame = 0
        self._animation_speed = animation_speed
        self._last_direction = 1
        self._idle_animation = idle_animation
        self._move_animation = move_animation

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

        if self.direction.x != 0:
            self._last_direction = int(self.direction.x)

    def update(self, screen: pg.Surface) -> None:
        self.update_direction()
        if not (any(self.direction)):
            self.do_animation(self._idle_animation)
            self.draw(screen)
            return
        self.move(screen)

    def move(self, screen: pg.Surface) -> None:
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
        self.do_animation(self._move_animation)
        self.draw(screen)

    def draw(self, screen: pg.Surface) -> None:
        self.change_image()
        self.rect = self.image.get_rect(center=self.pos)
        screen.blit(self.image, self.rect)

    def change_image(self) -> None:
        if int(self._last_direction) == -1:
            self.image = pg.transform.flip(self.image, 1, 0)
            self.image.set_colorkey((0, 0, 0))

    def do_animation(self, frames: list) -> None:
        frame_time = self._last_frame_time + self._animation_speed / self.fps
        diff_frames = int(frame_time) - int(self._last_frame_time)
        self._cur_frame = (self._cur_frame + diff_frames) % len(frames)
        self.image = frames[self._cur_frame]
        self._last_frame_time = frame_time


class Enemies:
    def __init__(self):
        pass
