from enum import IntEnum

import pygame as pg

pg.init()


class Animations(IntEnum):
    IDLE_ANIMATION = 0
    MOVE_ANIMATION = 1
    HIT_ANIMATION = 2


INVENTORY_SIZE = {'copper': 4,
                  'iron': 4,
                  'ruby': 1,
                  'sapphire': 2}


class SpriteSheet:
    def __init__(self, sheet: pg.Surface):
        self.sheet = sheet

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

    def get_frames(self, row: int, width: int, height: int, frames_count: int,
                   new_size: tuple[int, int] or None = None, scale: int = 1,
                   colorkey: tuple[int, int, int] or str = None) -> list[pg.Surface]:
        """Get the animation frames from a row of SpriteSheet"""
        frames = [self.cut_image((0 + width * i, height * row), width, height,
                                 new_size=new_size, scale=scale, colorkey=colorkey) for i in range(frames_count)]

        return frames

    @staticmethod
    def resize(images: pg.Surface or list[pg.Surface], scale: int = 1,
               new_size: tuple[int, int, int] or None = None,
               colorkey: tuple[int, int, int] or str = None) -> list[pg.Surface] or pg.Surface:
        upscaled_images = []
        if isinstance(images, pg.Surface):
            images = [images]
        for image in images:
            if new_size is not None:
                image = pg.transform.scale(image, new_size[0] * scale, new_size[1] * scale)
            else:
                image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
            if colorkey is not None:
                image.set_colorkey(colorkey)

            if len(images) == 1:
                return image
            else:
                upscaled_images.append(image)

        return upscaled_images


class Hero(pg.sprite.Sprite):
    image = pg.Surface((24, 24))
    SPEED = 6

    def __init__(self, game: 'main.Game', position: tuple[int, int], fps: int,
                 animation_speed: float, *animation) -> None:
        super().__init__(game._all_sprites, game._creatures)
        self.fps = fps
        self.game = game

        self.rect = self.image.get_rect(center=position)
        self.direction = pg.math.Vector2()
        self._is_move = False

        self._mouse_click = False
        self._is_animation_loop = False

        self._offset = None
        self._offset_pos = None

        self._last_frame_time = 0.0
        self._cur_frame = 0
        self._animation_speed = animation_speed
        self._last_direction = 1
        self._animations = animation
        self._current_animation = Animations.IDLE_ANIMATION

        self._hp = 100
        self._inventory = None

    def get_hp(self) -> int:
        return self._hp

    def input_check(self) -> None:
        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()

        if mouse[2]:
            self._mouse_click = True
        else:
            self._mouse_click = False

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

        if self.direction.x != 0 or self._mouse_click:
            if self._mouse_click and pg.mouse.get_pos()[0] > (self.rect.topleft - self._offset)[0]:
                self._last_direction = 1
            elif self._mouse_click and pg.mouse.get_pos()[0] < (self.rect.topleft - self._offset)[0]:
                self._last_direction = -1
            else:
                self._last_direction = int(self.direction.x)

    def check_hit(self, topleft: tuple[int, int], side: int, mouse_pos: tuple[int, int]) -> bool:
        mouse = pg.mouse.get_pressed()

        obj_rect = pg.Rect(*topleft, side, side)
        return self._mouse_click and obj_rect.collidepoint(mouse_pos) and mouse[2]

    def check_pickup(self, money_counter):
        collided = pg.sprite.spritecollideany(self, self.game._picked)
        if collided:
            if collided.loot_type == 4:
                money_counter.change(money_counter.get_value() + 1)
                collided.kill()
            else:
                for row in range(len(self._inventory.items)):
                    for col in range(len(self._inventory.items[0])):
                        cell = self._inventory.items[row][col]
                        if not cell:
                            cell.append(collided.name)
                            cell.append(collided)
                            collided.kill()
                            return
                        elif collided.name in cell and len(cell) <= INVENTORY_SIZE[collided.name]:
                            cell.append(collided)
                            collided.kill()
                            return

    def update(self, screen: pg.Surface, offset: pg.Vector2, money_counter) -> None:
        self._offset = offset

        if self._is_animation_loop:
            self.do_animation(self._animations[self._current_animation])
            self.draw(screen)
            return

        self.input_check()
        if not (any(self.direction)) or self._mouse_click:
            if self._mouse_click:
                self._current_animation = Animations.HIT_ANIMATION
                self._is_animation_loop = True
            else:
                self._current_animation = Animations.IDLE_ANIMATION

            self.draw(screen)
            return
        self.move(screen)
        self.check_pickup(money_counter)

    def move(self, screen: pg.Surface) -> None:
        old_pos = list(self.rect.center).copy()

        self.rect.center += (self.SPEED * self.direction.normalize())
        if pg.sprite.spritecollideany(self, self.game._obstacles):
            self.rect.center = old_pos

        self._current_animation = Animations.MOVE_ANIMATION
        self.draw(screen)

    def draw(self, screen: pg.Surface) -> None:
        self.do_animation(self._animations[self._current_animation])
        screen.blit(self.image, self._offset_pos)

    def flip_image(self) -> None:
        if int(self._last_direction) == -1:
            self.image = pg.transform.flip(self.image, 1, 0)
            self.image.set_colorkey((0, 0, 0))

    def do_animation(self, frames: list) -> None:
        frame_time = self._last_frame_time + self._animation_speed / self.fps
        diff_frames = int(frame_time) - int(self._last_frame_time)
        self._cur_frame = (self._cur_frame + diff_frames) % len(frames)
        self.image = frames[self._cur_frame]
        self._last_frame_time = frame_time

        if self._is_animation_loop and self._cur_frame % len(frames) == len(frames) - 1:
            self._is_animation_loop = False

        self.flip_image()
        self.rect = self.image.get_rect(center=self.rect.center)
        self._offset_pos = self.rect.topleft - self._offset


class Enemies:
    def __init__(self):
        pass
