import pygame as pg
from data.scripts.sprites import Hero
from data.scripts.mapReader import get_map_surface, get_map_data, get_player_pos
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
        field = get_map_data('data/maps/lvl1.dat')
        player_pos = get_player_pos(field)
        field = get_map_surface(field)

        screen.blit(field, (0, 0))

        pg.display.set_caption('Caves of Siberia')

        all_sprites = pg.sprite.Group()
        Hero(player_pos, all_sprites)

        clock = pg.time.Clock()

        run = True
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
            screen.blit(field, (0, 0))

            all_sprites.draw(screen)
            all_sprites.update()

            pg.display.update()

        self.terminate()


if __name__ == '__main__':
    game = Game()
    game.main()
