import pygame as pg

pg.init()


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
