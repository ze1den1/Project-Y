import sys

import pygame as pg
from data.scripts.sprites import Hero
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject
from data.scripts.buttons import DefaultButton, ButtonGroup

pg.init()


class Game:
    FPS = 240
    BACKGROUND = pg.Color('white')
    TILE_SIZE = 64
    MONITOR_W = pg.display.Info().current_w
    MONITOR_H = pg.display.Info().current_h

    def __init__(self) -> None:
        self.to_quit = False

    def main_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        screen.fill('white')

        buttons_group = ButtonGroup()
        start_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) - 120), 300, 150,
                                     'button.png', text='Start', text_size=60,
                                     sound='click.wav', group=buttons_group)
        settings_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1)), 300, 150,
                                        'button.png', text='Settings', text_size=60,
                                        sound='click.wav', group=buttons_group)
        quit_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) + 120), 300, 150,
                                    'button.png', text='Quit', text_size=60,
                                    sound='click.wav', group=buttons_group)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.USEREVENT and event.button == start_button:
                    run = False
                elif event.type == pg.USEREVENT and event.button == quit_button:
                    run = False
                    pg.time.delay(500)
                    self.to_quit = True
                elif event.type == pg.USEREVENT and event.button == settings_button:
                    self.settings_menu()
                buttons_group.handle(event)

            buttons_group.check_hover(pg.mouse.get_pos())
            buttons_group.draw(screen)

            pg.display.update()

        if self.to_quit:
            self.terminate()

    def settings_menu(self) -> None:
        pass  # TODO settings

    def pause_menu(self) -> None:
        pause_surf = pg.Surface((480, 720))
        pause_surf.fill((98, 104, 115, 150))
        pause_pos = (self.MONITOR_W >> 1, self.MONITOR_H >> 1)
        pause_rect = pause_surf.get_rect(center=pause_pos)

        pause_buttons = ButtonGroup()
        continue_button = DefaultButton((pause_rect.centerx, pause_rect.centery - 200), 200, 100,
                                        'button.png', text='continue', text_size=60,
                                        sound='click.wav', group=pause_buttons)
        to_settings = DefaultButton((pause_rect.centerx, pause_rect.centery), 200, 100,
                                    'button.png', text='settings', text_size=60,
                                    sound='click.wav', group=pause_buttons)
        quit_to_menu = DefaultButton((pause_rect.centerx, pause_rect.centery + 200), 200, 100,
                                     'button.png', text='menu', text_size=60,
                                     sound='click.wav', group=pause_buttons)
        quit_from_the_game = DefaultButton((pause_rect.centerx, pause_rect.centery + 300), 200, 100,
                                           'button.png', text='exit', text_size=60,
                                           sound='click.wav', group=pause_buttons)

        run = True
        while run:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                        or (event.type == pg.USEREVENT and event.button == continue_button):
                    run = False
                elif event.type == pg.USEREVENT and event.button == to_settings:
                    self.settings_menu()
                elif event.type == pg.USEREVENT and event.button == quit_to_menu:
                    run = False
                    self.main_menu()
                elif event.type == pg.USEREVENT and event.button == quit_from_the_game:
                    self.terminate()
                pause_buttons.handle(event)

            self.main_screen.blit(pause_surf, pause_rect)
            pause_buttons.check_hover(pg.mouse.get_pos())
            pause_buttons.draw(self.main_screen)
            pg.display.update()

    @staticmethod
    def terminate() -> None:
        pg.quit()
        sys.exit(1)

    def main(self) -> None:
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.main_menu()

        self.main_screen = pg.display.set_mode((0, 0), pg.RESIZABLE)

        field = get_map_data('data/maps/lvl1.dat')
        player_pos = get_player_pos(field)
        field = self.get_map_surface(field)
        self.main_screen.blit(field, (0, 0))

        pg.display.set_caption('Caves of Siberia')

        Hero(self, player_pos, self.FPS)

        clock = pg.time.Clock()

        run = True
        self.to_quit = False
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_menu()
            self.main_screen.blit(field, (0, 0))

            self.all_sprites.draw(self.main_screen)
            self.all_sprites.update()

            pg.display.update()

        if self.to_quit:
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
