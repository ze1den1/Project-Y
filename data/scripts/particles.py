import random
from enum import StrEnum, IntEnum

import pygame as pg


class Materials(IntEnum):
    WOOD = 0
    ROCK = 1


class Particles(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()

    def update(self, screen: pg.Surface, **kwargs) -> None:
        for sprite in self.sprites():
            sprite.update(screen)


class Sparks(pg.sprite.Sprite):
    sparks = [pg.image.load('data/images/objects/spark.png')]
    for scale in (12, 16, 24):
        sparks.append(pg.transform.scale(sparks[0], (scale, scale)))

    chips = [pg.image.load('data/images/objects/chips.png')]
    for scale in (12, 16, 24):
        sparks.append(pg.transform.scale(sparks[0], (scale, scale)))

    def __init__(self, game: 'main.Game', pos: tuple[int, int], dx: int, dy: int, fps: int, lifetime: int,
                 material: int) -> None:
        super().__init__(game._particles)

        if material == Materials.ROCK:
            self.image = random.choice(self.sparks)
        elif material == Materials.WOOD:
            self.image = random.choice(self.chips)
        self.rect = self.image.get_rect(center=pos)
        self.pos = list(pos)

        self.velocity = [dx, dy]
        self.gravity = 50

        self.fps = fps
        self.lifetime = lifetime
        self.start_tick = pg.time.get_ticks()
        self.last_tick = None

    def update(self, screen: pg.Surface) -> None:
        self.velocity[1] += self.gravity / self.fps
        self.pos[0] += self.velocity[0] / self.fps
        self.pos[1] += self.velocity[1] / self.fps
        self.rect.center = self.pos

        self.draw(screen)

        self.last_tick = pg.time.get_ticks()
        if self.last_tick - self.start_tick >= self.lifetime:
            self.kill()

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.image, self.rect)


def create_sparks(game: 'main.Game', position: tuple[int, int], milliseconds: int, material: int) -> None:
    particle_count = 20
    numbers = range(-50, 51)
    for _ in range(particle_count):
        Sparks(game, position, random.choice(numbers), random.choice(numbers), game.FPS, milliseconds, material)
