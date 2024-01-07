import random
from enum import IntEnum
from data.scripts.sprites import SpriteSheet
import pygame as pg

sheet = pg.image.load('data/images/particles/particles.png')
sheet = SpriteSheet(sheet)


class Materials(IntEnum):
    WOOD = 0
    ROCK = 1


def scale_with_colorkey(image: pg.Surface, scale: tuple[int, int],
                        colorkey: tuple[int, int, int] or str) -> pg.Surface:
    image = pg.transform.scale(image, scale)
    image.set_colorkey(colorkey)

    return image


class Particles(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()

    def update(self, screen: pg.Surface, **kwargs) -> None:
        for sprite in self.sprites():
            sprite.update(screen)


class Particle(pg.sprite.Sprite):
    image = pg.Surface((10, 10))

    def __init__(self, game: 'main.Game', pos: tuple[int, int], dx: int, dy: int, fps: int, *groups) -> None:
        super().__init__(*groups)
        self.rect = self.image.get_rect(center=pos)
        self.pos = list(pos)

        self.velocity = [dx, dy]
        self.gravity = 50

        self.fps = fps

    def update(self, screen: pg.Surface) -> None:
        self.velocity[1] += self.gravity / self.fps
        self.pos[0] += self.velocity[0] / self.fps
        self.pos[1] += self.velocity[1] / self.fps
        self.rect.center = self.pos

        self.draw(screen)

        if self.check_kill():
            self.kill()

    def check_kill(self) -> bool:
        pass

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.image, self.rect)


class Sparks(Particle):
    sparks = [sheet.cut_image((16, 0), 8, 8, colorkey=(0, 0, 0))]
    for scale in (8, 12, 16):
        sparks.append(scale_with_colorkey(sparks[0], (scale, scale), (0, 0, 0)))

    chips = [sheet.cut_image((8, 0), 8, 8, colorkey=(0, 0, 0))]
    for scale in (8, 12, 16):
        chips.append(scale_with_colorkey(chips[0], (scale, scale), (0, 0, 0)))

    def __init__(self, game: 'main.Game', pos: tuple[int, int], dx: int, dy: int, fps: int, lifetime: int,
                 material: int) -> None:
        super().__init__(game, pos, dx, dy, fps, game._particles)

        if material == Materials.ROCK:
            self.image = random.choice(self.sparks)
        elif material == Materials.WOOD:
            self.image = random.choice(self.chips)

        self.lifetime = lifetime
        self.start_tick = pg.time.get_ticks()
        self.last_tick = None

    def check_kill(self) -> bool:
        self.last_tick = pg.time.get_ticks()
        return self.last_tick - self.start_tick >= self.lifetime


class Snowflake(Particle):
    snowflakes = [sheet.cut_image((0, 0), 8, 8, colorkey=(0, 0, 0))]
    for scale in (12, 16, 24):
        snowflakes.append(scale_with_colorkey(snowflakes[0], (scale, scale), (0, 0, 0)))

    def __init__(self, game: 'main.Game', pos: tuple[int, int], fps: int):
        super().__init__(game, pos, 0, 80, fps)
        self.gravity = 0
        self.game = game
        self.i = 0

        self.image = random.choice(self.snowflakes)

    def update(self, screen: pg.Surface) -> None:
        self.velocity[1] += self.gravity / self.fps
        if self.i % 120 < 60:
            self.pos[0] += -100 / self.fps
        else:
            self.pos[0] += 100 / self.fps
        self.pos[1] += self.velocity[1] / self.fps
        self.rect.center = self.pos
        self.i += 1

        self.draw(screen)

        if self.check_kill():
            self.kill()

    def check_kill(self) -> bool:
        return self.rect.colliderect(pg.Rect(0, self.game.MONITOR_H, self.game.MONITOR_W, 10))


def create_sparks(game: 'main.Game', position: tuple[int, int], milliseconds: int, material: int) -> None:
    particle_count = 20
    numbers = range(-50, 51)
    for _ in range(particle_count):
        Sparks(game, position, random.choice(numbers), random.choice(numbers), game.FPS, milliseconds, material)
