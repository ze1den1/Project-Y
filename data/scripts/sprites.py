import pygame as pg

pg.init()


class Hero(pg.sprite.Sprite):
    image = pg.image.load('data/images/hero.png')

    def __init__(self, position: tuple[int, int], group: pg.sprite.Group) -> None:
        super().__init__(group)
        self.rect = self.image.get_rect(topleft=position)
        self.speed = 5
        self.direction = pg.math.Vector2()

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
        self.rect.center += self.speed * self.direction


class Enemies:
    def __init__(self):
        pass
