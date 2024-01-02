import os.path
import sys

import pygame as pg
from data.scripts.sprites import Hero, SpriteSheet
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject
from data.scripts.UI import DefaultButton, ButtonGroup, Slider, Counter
from data.scripts.sounds import InterfaceSounds, Music

pg.init()
pg.mixer.init()


class Game:
    FPS = 60
    BACKGROUND = pg.Color('white')
    TILE_SIZE = 64
    MONITOR_W = pg.display.Info().current_w
    MONITOR_H = pg.display.Info().current_h
    HEART_IMG = pg.image.load(os.path.join('data', 'images', 'UI', 'heart.png'))
    HEART_IMG = pg.transform.scale(HEART_IMG, (48, 48))

    IDLE_ANIM = SpriteSheet(pg.image.load('data/doux.png'))
    IDLE_ANIM = IDLE_ANIM.get_frames(0, 24, 24, 4, new_size=(48, 48), colorkey=(0, 0, 0))
    MOVE_ANIM = SpriteSheet(pg.image.load('data/move.png'))
    MOVE_ANIM = MOVE_ANIM.get_frames(0, 24, 24, 6, new_size=(48, 48), colorkey=(0, 0, 0))

    MAPS_DICT = {}
    for number, image in enumerate(os.listdir('data/maps/map_previews')):
        MAPS_DICT[number] = (pg.image.load(f'data/maps/map_previews/{image}'), image)

    def __init__(self) -> None:
        self._to_quit = False
        self._main_run = False

        self._interface_volume = 1.0

        self._music_sounds = Music()
        self._music_volume = 1.0

        self._all_sprites = pg.sprite.Group()
        self._obstacles = pg.sprite.Group()
        self._creatures = pg.sprite.Group()
        self._hero = None

        self.current_map = 0

        font_scale = round(self.MONITOR_W // 16) >> 1
        self._font_size = round(0.8 * font_scale)
        self._font = pg.font.Font(None, self._font_size)

    def main(self) -> None:
        self.main_menu()

    def main_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        buttons_group = ButtonGroup()
        interface_sounds = InterfaceSounds()

        start_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) - 120), 300, 150,
                                     'button.png', text='Select Map', text_size=self._font_size,
                                     sound='click.wav', group=buttons_group)
        interface_sounds.add(start_button._sound)
        settings_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1)), 300, 150,
                                        'button.png', text='Settings', text_size=self._font_size,
                                        sound='click.wav', group=buttons_group)
        interface_sounds.add(settings_button._sound)
        quit_button = DefaultButton((self.MONITOR_W >> 1, (self.MONITOR_H >> 1) + 120), 300, 150,
                                    'button.png', text='Quit', text_size=self._font_size,
                                    sound='click.wav', group=buttons_group)
        interface_sounds.add(quit_button._sound)

        interface_sounds.set_volume(self._interface_volume)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.USEREVENT and event.button == start_button:
                    run = False
                    self.select_level()
                elif (event.type == pg.USEREVENT and event.button == quit_button) or event.type == pg.QUIT:
                    run = False
                    pg.time.delay(500)
                    self._to_quit = True
                elif event.type == pg.USEREVENT and event.button == settings_button:
                    run = False
                    self.settings_menu()
                buttons_group.handle(event)

            buttons_group.check_hover(pg.mouse.get_pos())

            screen.fill((255, 255, 255))
            buttons_group.draw(screen)

            pg.display.update()

        if self._to_quit:
            self.terminate()

    def select_level(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        preview_img, preview_rect, name_rect, name, name_surf = self.get_preview_values(
            *self.MAPS_DICT[self.current_map % len(self.MAPS_DICT)])

        buttons_group = ButtonGroup()
        return_btn = DefaultButton((150, 100), 200, 100,
                                   'button.png', text='Return', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        next_map = DefaultButton(((self.MONITOR_W >> 1) + (preview_rect.width >> 1) + 30, self.MONITOR_H >> 1),
                                 self.MONITOR_W * 0.02, 50, 'right_arrow.png', sound='click.wav',
                                 group=buttons_group)
        previous_map = DefaultButton(((self.MONITOR_W >> 1) - (preview_rect.width >> 1) - 30, self.MONITOR_H >> 1),
                                     self.MONITOR_W * 0.02, 50, 'left_arrow.png', sound='click.wav',
                                     group=buttons_group)
        start = DefaultButton((self.MONITOR_W >> 1, self.MONITOR_H * 0.7),
                              self.MONITOR_W * 0.1, self.MONITOR_H * 0.1, 'button.png', sound='click.wav',
                              group=buttons_group, text='Start', text_size=self._font_size)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.USEREVENT and event.button == return_btn:
                    run = False
                    self.main_menu()
                elif event.type == pg.USEREVENT and event.button == next_map:
                    self.current_map += 1
                    preview_img, preview_rect, name_rect, name, name_surf = self.get_preview_values(
                        *self.MAPS_DICT[self.current_map % len(self.MAPS_DICT)])
                elif event.type == pg.USEREVENT and event.button == previous_map:
                    self.current_map -= 1
                    preview_img, preview_rect, name_rect, name, name_surf = self.get_preview_values(
                        *self.MAPS_DICT[self.current_map % len(self.MAPS_DICT)])
                elif event.type == pg.USEREVENT and event.button == start:
                    run = False
                    self.game(name)

                if event.type == pg.QUIT:
                    run = False
                    self.terminate()
                buttons_group.handle(event)

            buttons_group.check_hover(pg.mouse.get_pos())

            screen.fill((255, 255, 255))
            screen.blit(name_surf, name_rect)
            screen.blit(preview_img, preview_rect)
            buttons_group.draw(screen)
            pg.display.update()

    def get_preview_values(self, image: pg.Surface, name: str):
        preview_img = pg.transform.scale(image, (self.MONITOR_W * 0.3, self.MONITOR_H * 0.25))
        name = name[:name.find('.')]
        name_surf = self._font.render(name, True, (0, 0, 0))
        preview_rect = preview_img.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        name_rect = name_surf.get_rect(center=(preview_rect.midtop[0], preview_rect.midtop[1] - 100))

        return preview_img, preview_rect, name_rect, name, name_surf

    def settings_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        font_surf = self._font.render('UI sounds', True, (0, 0, 0))

        states = []
        volume_surf = pg.Surface((self.MONITOR_W * 0.75, self.MONITOR_H * 0.85))
        volume_rect = volume_surf.get_rect(topleft=(self.MONITOR_W * 0.22, self.MONITOR_H * 0.07))
        volume_surf.fill((98, 104, 115))
        states.append(volume_surf)

        video_surf = pg.Surface((self.MONITOR_W * 0.75, self.MONITOR_H * 0.85))
        video_rect = video_surf.get_rect(topleft=(self.MONITOR_W * 0.22, self.MONITOR_H * 0.07))
        video_surf.fill((98, 104, 115))
        states.append(video_surf)

        settings_state = -1

        buttons_group = ButtonGroup()
        interface_sounds = InterfaceSounds()

        return_btn = DefaultButton((150, 100), 200, 100,
                                   'button.png', text='Return', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(return_btn._sound)
        volume_btn = DefaultButton((150, 250), 200, 100,
                                   'button.png', text='volume', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(volume_btn._sound)
        video_btn = DefaultButton((150, 400), 200, 100,
                                  'button.png', text='video', text_size=self._font_size,
                                  sound='click.wav', group=buttons_group)
        interface_sounds.add(video_btn._sound)

        volume_buttons = ButtonGroup()
        slider = Slider((volume_rect.w * 0.4 + volume_rect.topleft[0],
                         volume_rect.h * 0.1 + volume_rect.topleft[1]),
                        volume_rect.w * 0.4, 60,
                        slider_color=(126, 134, 148))
        decrease_value = DefaultButton((volume_rect.w * 0.35 + volume_rect.topleft[0],
                                        volume_rect.h * 0.12 + volume_rect.topleft[1]),
                                       volume_rect.w * 0.05, 50,
                                       'left_arrow.png',
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(decrease_value._sound)
        increase_value = DefaultButton((volume_rect.w * 0.85 + volume_rect.topleft[0],
                                        volume_rect.h * 0.12 + volume_rect.topleft[1]),
                                       volume_rect.w * 0.05, 50,
                                       'right_arrow.png',
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(increase_value._sound)

        interface_sounds.set_volume(self._interface_volume)

        value = int(self._interface_volume * 10)
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
                    self._interface_volume = value / 10
                    interface_sounds.set_volume(self._interface_volume)
                elif event.type == pg.USEREVENT and event.button == increase_value and 0 <= value < 10:
                    value += 1
                    slider.change(value)
                    self._interface_volume = value / 10
                    interface_sounds.set_volume(self._interface_volume)

                if event.type == pg.QUIT:
                    run = False
                    self.terminate()

                if settings_state == 0:
                    volume_buttons.handle(event)
                buttons_group.handle(event)

            screen.fill((255, 255, 255))
            if settings_state != -1:
                screen.blit(states[settings_state], (self.MONITOR_W * 0.22, self.MONITOR_H * 0.05))
                if settings_state == 0:
                    slider.draw(screen)
                    volume_buttons.draw(screen)
                    volume_buttons.check_hover(pg.mouse.get_pos())
                    screen.blit(font_surf, (volume_rect.topleft[0] + self.MONITOR_H * 0.05,
                                            volume_rect.topleft[1] + self.MONITOR_W * 0.05))

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
                                        'button.png', text='continue', text_size=self._font_size,
                                        sound='click.wav', group=pause_buttons)
        interface_sounds.add(continue_button._sound)
        quit_to_menu = DefaultButton((pause_rect.centerx, pause_rect.centery + 200), 200, 100,
                                     'button.png', text='menu', text_size=self._font_size,
                                     sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_to_menu._sound)
        quit_from_the_game = DefaultButton((pause_rect.centerx, pause_rect.centery + 300), 200, 100,
                                           'button.png', text='exit', text_size=self._font_size,
                                           sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_from_the_game._sound)

        interface_sounds.set_volume(self._interface_volume)

        run = True
        while run:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                        or (event.type == pg.USEREVENT and event.button == continue_button):
                    run = False
                elif event.type == pg.USEREVENT and event.button == quit_to_menu:
                    run = False
                    self._main_run = False
                    self.main_menu()
                elif (event.type == pg.USEREVENT and event.button == quit_from_the_game) or event.type == pg.QUIT:
                    pg.time.delay(500)
                    self.terminate()
                pause_buttons.handle(event)

            self._main_screen.blit(pause_surf, pause_rect)
            pause_buttons.check_hover(pg.mouse.get_pos())
            pause_buttons.draw(self._main_screen)
            pg.display.update()

    def restart_game(self, lvl_name: str) -> None:
        self._main_screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        if self._all_sprites:
            for sprite in self._all_sprites:
                sprite.kill()

        map_data = get_map_data(f'data/maps/{lvl_name}.dat')
        player_pos = get_player_pos(map_data)
        self._field = self.get_map_surface(map_data)
        self._main_screen.blit(self._field, (0, 0))
        self._hero = Hero(self, player_pos, self.FPS, 8, self.IDLE_ANIM, self.MOVE_ANIM)

    def game(self, lvl_name: str):
        self.restart_game(lvl_name)
        self._hero: Hero

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

        self._main_run = True
        self._to_quit = False
        while self._main_run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_menu()

                if event.type == pg.QUIT:
                    self._main_run = False
                    self.terminate()

            self._main_screen.blit(self._field, (0, 0))

            self._all_sprites.draw(self._main_screen)
            self._hero.update(self._main_screen)
            ui.draw(self._main_screen)
            ui_sprites.draw(self._main_screen)

            pg.display.update()

        if self._to_quit:
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
