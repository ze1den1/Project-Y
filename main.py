import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
FPS = 15
MAPS_DIR = 'maps'
TITLE_SIZE = 32


class Hero:

    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = self.x * TITLE_SIZE + TITLE_SIZE // 2, self.y * TITLE_SIZE + TITLE_SIZE // 2
        pygame.draw.circle(screen, 'blue', center, TITLE_SIZE // 2)


class Enemies:

    def __init__(self):
        pass


class Game:

    def __init__(self, hero):
        self.hero = hero
        self.points = 0

    def render(self, screen):
        self.hero.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        self.hero.set_position((next_x, next_y))
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.points += 1


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    hero = Hero((12, 12))
    game = Game(hero)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game.update_hero()
        screen.fill((0, 0, 0))
        game.render(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
