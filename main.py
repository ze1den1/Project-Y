import os.path
import sys

import pygame as pg
from data.scripts.sprites import Hero
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject
from data.scripts.UI import DefaultButton, ButtonGroup, Slider, Counter
from data.scripts.sounds import InterfaceSounds, Music

pg.init()
pg.mixer.init()


class Game:
    FPS = 240
    BACKGROUND = pg.Color('white')
    TILE_SIZE = 64
    MONITOR_W = pg.display.Info().current_w
    MONITOR_H = pg.display.Info().current_h
    HEART_IMG = pg.image.load(os.path.join('data', 'images', 'UI', 'heart.png'))
    HEART_IMG = pg.transform.scale(HEART_IMG, (48, 48))

    def __init__(self) -> None:
        self.to_quit = False

        self.interface_volume = 1.0

        self.music_sounds = Music()
        self.music_volume = 1.0

    def main_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        screen.fill('white')

        buttons_group = ButtonGroup()
        interface_sounds = InterfaceSounds()

        start_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) - 120), 300, 150,
                                     'button.png', text='Start', text_size=60,
                                     sound='click.wav', group=buttons_group)
        interface_sounds.add(start_button._sound)
        settings_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1)), 300, 150,
                                        'button.png', text='Settings', text_size=60,
                                        sound='click.wav', group=buttons_group)
        interface_sounds.add(settings_button._sound)
        quit_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) + 120), 300, 150,
                                    'button.png', text='Quit', text_size=60,
                                    sound='click.wav', group=buttons_group)
        interface_sounds.add(quit_button._sound)

        interface_sounds.set_volume(self.interface_volume)

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
                    run = False
                    self.settings_menu()
                buttons_group.handle(event)

            buttons_group.check_hover(pg.mouse.get_pos())
            buttons_group.draw(screen)

            pg.display.update()

        if self.to_quit:
            self.terminate()

    def settings_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        screen.fill('white')

        font = pg.font.Font(None, 60)
        font_surf = font.render('UI sounds', True, (0, 0, 0))

        states = []
        volume_surf = pg.Surface((self.MONITOR_W - 400, self.MONITOR_H - 200))
        volume_rect = volume_surf.get_rect(topleft=(400, 100))
        volume_surf.fill((98, 104, 115))
        states.append(volume_surf)
        video_surf = pg.Surface((self.MONITOR_W - 400, self.MONITOR_H - 200))
        video_rect = video_surf.get_rect(topleft=(400, 100))
        video_surf.fill((98, 104, 115))
        states.append(video_surf)
        settings_state = -1

        buttons_group = ButtonGroup()
        interface_sounds = InterfaceSounds()

        return_btn = DefaultButton((150, 100), 200, 100,
                                   'button.png', text='Return', text_size=60,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(return_btn._sound)
        volume_btn = DefaultButton((150, 250), 200, 100,
                                   'button.png', text='volume', text_size=60,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(volume_btn._sound)
        video_btn = DefaultButton((150, 400), 200, 100,
                                  'button.png', text='video', text_size=60,
                                  sound='click.wav', group=buttons_group)
        interface_sounds.add(video_btn._sound)

        volume_buttons = ButtonGroup()
        slider = Slider((volume_rect.topleft[0] + 400, volume_rect.topleft[1] + 100), 600, 60,
                        slider_color=(126, 134, 148))
        decrease_value = DefaultButton((volume_rect.topleft[0] + 300, volume_rect.topleft[1] + 130),
                                       100, 50,
                                       'left_arrow.png',
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(decrease_value._sound)
        increase_value = DefaultButton((volume_rect.topleft[0] + 1100, volume_rect.topleft[1] + 130),
                                       100, 50,
                                       'right_arrow.png',
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(increase_value._sound)

        interface_sounds.set_volume(self.interface_volume)

        value = int(self.interface_volume * 10)
        slider.change(value)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.USEREVENT and event.button == return_btn:
                    run = False
                    self.main_menu()
                elif event.type == pg.USEREVENT and event.button == volume_btn:
                    settings_state = 0
                elif event.type == pg.USEREVENT and event.button == video_btn:
                    settings_state = 1
                elif event.type == pg.USEREVENT and event.button == decrease_value and 0 < value <= 10:
                    value -= 1
                    slider.change(value)
                    self.interface_volume = value / 10
                    interface_sounds.set_volume(self.interface_volume)
                elif event.type == pg.USEREVENT and event.button == increase_value and 0 <= value < 10:
                    value += 1
                    slider.change(value)
                    self.interface_volume = value / 10
                    interface_sounds.set_volume(self.interface_volume)

                if settings_state == 0:
                    volume_buttons.handle(event)
                buttons_group.handle(event)

            if settings_state != -1:
                screen.blit(states[settings_state], (400, 100))
                if settings_state == 0:
                    slider.draw(screen)
                    volume_buttons.draw(screen)
                    volume_buttons.check_hover(pg.mouse.get_pos())
                    screen.blit(font_surf, (volume_rect.topleft[0] + 45, volume_rect.topleft[1] + 110))

            buttons_group.check_hover(pg.mouse.get_pos())
            buttons_group.draw(screen)
            pg.display.update()

    def pause_menu(self) -> None:
        pause_surf = pg.Surface((480, 720))
        pause_surf.fill((98, 104, 115, 150))
        pause_pos = (self.MONITOR_W >> 1, self.MONITOR_H >> 1)
        pause_rect = pause_surf.get_rect(center=pause_pos)

        pause_buttons = ButtonGroup()
        interface_sounds = InterfaceSounds()

        continue_button = DefaultButton((pause_rect.centerx, pause_rect.centery - 200), 200, 100,
                                        'button.png', text='continue', text_size=60,
                                        sound='click.wav', group=pause_buttons)
        interface_sounds.add(continue_button._sound)
        quit_to_menu = DefaultButton((pause_rect.centerx, pause_rect.centery + 200), 200, 100,
                                     'button.png', text='menu', text_size=60,
                                     sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_to_menu._sound)
        quit_from_the_game = DefaultButton((pause_rect.centerx, pause_rect.centery + 300), 200, 100,
                                           'button.png', text='exit', text_size=60,
                                           sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_from_the_game._sound)

        interface_sounds.set_volume(self.interface_volume)

        run = True
        while run:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                        or (event.type == pg.USEREVENT and event.button == continue_button):
                    run = False
                elif event.type == pg.USEREVENT and event.button == quit_to_menu:
                    run = False
                    self.restart_game()
                    self.main_menu()
                elif event.type == pg.USEREVENT and event.button == quit_from_the_game:
                    pg.time.delay(500)
                    self.terminate()
                pause_buttons.handle(event)

            self._main_screen.blit(pause_surf, pause_rect)
            pause_buttons.check_hover(pg.mouse.get_pos())
            pause_buttons.draw(self._main_screen)
            pg.display.update()

    def restart_game(self) -> None:
        if self.all_sprites:
            for sprite in self.all_sprites:
                sprite.kill()

        map_data = get_map_data('data/maps/lvl1.dat')
        player_pos = get_player_pos(map_data)
        self._field = self.get_map_surface(map_data)
        self._main_screen.blit(self._field, (0, 0))
        Hero(self, player_pos, self.FPS)

    def main(self) -> None:
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.main_menu()

        self._main_screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        self.restart_game()
        pg.display.set_caption('Caves of Siberia')

        ui = ButtonGroup()
        ui_sprites = pg.sprite.Group()
        hp_bar = Slider((75, 20), 300, 50, (5, 5, 5), (227, 25, 25), 100)
        heart = pg.sprite.Sprite()
        heart.image = self.HEART_IMG
        heart.rect = (20, 20, 64, 64)
        ui_sprites.add(heart)

        ui.add(hp_bar)

        counter = Counter((self.MONITOR_W - 250, 20), 300, 50,
                          number_color=(255, 255, 255), group=ui)

        clock = pg.time.Clock()

        run = True
        self.to_quit = False
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_menu()
            self._main_screen.blit(self._field, (0, 0))

            self.all_sprites.draw(self._main_screen)
            self.all_sprites.update()

            ui.draw(self._main_screen)
            ui_sprites.draw(self._main_screen)

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

    @staticmethod
    def terminate() -> None:
        pg.quit()
        sys.exit(1)


if __name__ == '__main__':
    game = Game()
    game.main()
