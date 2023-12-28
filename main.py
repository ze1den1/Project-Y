import pygame as pg
from data.scripts.sprites import Hero
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject
from data.scripts.buttons import DefaultButton
pg.init()


class Game:
    FPS = 240
    BACKGROUND = pg.Color('white')
    TILE_SIZE = 64
    MONITOR_W = pg.display.Info().current_w
    MONITOR_H = pg.display.Info().current_h

    def __init__(self) -> None:
        pass

    def main_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)

        button = DefaultButton((self.MONITOR_W >> 1, self.MONITOR_H >> 1), 300, 150,
                               'button.png', text='start', text_size=60, sound='click.wav')
        screen.fill('white')

        clock = pg.time.Clock()

        run = True
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.USEREVENT and event.button == button:
                    run = False
                button.handle_event(event)

            button.hover_check(pg.mouse.get_pos())
            button.draw(screen)
            pg.display.update()

    def pause_menu(self) -> None:
        pass  # TODO pause menu

    @staticmethod
    def terminate() -> None:
        pg.quit()

    def main(self) -> None:
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.main_menu()

        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)

        field = get_map_data('data/maps/lvl1.dat')
        player_pos = get_player_pos(field)
        field = self.get_map_surface(field)
        screen.blit(field, (0, 0))

        pg.display.set_caption('Caves of Siberia')

        Hero(self, player_pos, self.FPS)

        clock = pg.time.Clock()

        run = True
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    run = False
            screen.blit(field, (0, 0))

            self.all_sprites.draw(screen)
            self.all_sprites.update()

            pg.display.update()

        self.terminate()

    def get_map_surface(self, data: list) -> pg.Surface:
        lvl_height = len(data) * self.TILE_SIZE
        lvl_width = len(data[0]) * self.TILE_SIZE
        lvl_map = pg.Surface((lvl_width, lvl_height))
        lvl_map.fill(self.BACKGROUND)

        for y in range(len(data)):
            for x in range(len(data[0])):
                if data[y][x].isdigit():
                    SimpleObject(self, int(data[y][x]), x, y)
        return lvl_map


if __name__ == '__main__':
    game = Game()
    game.main()
