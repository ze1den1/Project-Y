import pygame as pg
from data.scripts.sprites import Hero
pg.init()


class Game:
    FPS = 60
    BACKGROUND = pg.Color('black')

    def __init__(self) -> None:
        pass

    def menu(self) -> None:
        pass  # TODO main menu

    @staticmethod
    def terminate() -> None:
        pg.quit()

    def main(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        screen.fill(self.BACKGROUND)
        pg.display.set_caption('Caves of Siberia')

        all_sprites = pg.sprite.Group()
        Hero((50, 50), all_sprites)

        clock = pg.time.Clock()

        run = True
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
            screen.fill(self.BACKGROUND)

            all_sprites.draw(screen)
            all_sprites.update()

            pg.display.update()

        self.terminate()


if __name__ == '__main__':
    game = Game()
    game.main()
