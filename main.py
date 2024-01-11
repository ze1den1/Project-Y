import os.path
import random
import sys

import pygame as pg

pg.display.set_mode((0, 0))

from data.scripts.utils import load_with_colorkey, scale_with_colorkey
from data.scripts.sprites import Hero, SpriteSheet
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject, Border, Objects, Chest, Crate
from data.scripts.particles import Particles, Snowflake, Materials
from data.scripts.UI import DefaultButton, ButtonGroup, Slider, Counter
from data.scripts.sounds import SoundsList
from data.scripts.camera import CameraGroup

pg.init()
pg.mixer.init()


class Game:
    FPS = 60
    BACKGROUND = pg.Color((255, 255, 255))
    TILE_SIZE = 72
    MONITOR_W = pg.display.Info().current_w
    MONITOR_H = pg.display.Info().current_h

    MENU_BG = pg.transform.scale(pg.image.load('data/images/UI/menu_bg.png'),
                                 (MONITOR_W, MONITOR_H))
    sheet = SpriteSheet(pg.image.load('data/images/UI/menu_buttons.png'))

    START_BUTTON = sheet.get_frames(0, 1451, 345, 2, colorkey=(0, 0, 0))
    SETTINGS_BUTTON = sheet.get_frames(1, 1451, 345, 2, colorkey=(0, 0, 0))
    CREDITS_BUTTON = sheet.get_frames(2, 1451, 345, 2, colorkey=(0, 0, 0))
    QUIT_BUTTON = sheet.cut_image((0, 1035), 1451, 345, colorkey=(0, 0, 0))

    BUTTON = load_with_colorkey('data/images/UI/button.png', (0, 0, 0))
    HINT_BUTTON = load_with_colorkey('data/images/UI/hint_btn.png', (0, 0, 0))
    LEFT_ARROW = pg.image.load('data/images/UI/left_arrow.png')
    RIGHT_ARROW = pg.image.load('data/images/UI/right_arrow.png')

    HEART_IMG = scale_with_colorkey(pg.image.load('data/images/UI/heart.png'), (48, 48), (0, 0, 0))

    HERO_SPRITESHEET = SpriteSheet(pg.image.load('data/images/creatures/hero.png'))
    HERO_IDLE = HERO_SPRITESHEET.get_frames(0, 16, 16, 18, new_size=(64, 64),
                                            colorkey=(0, 0, 0))
    HERO_MOVE = HERO_SPRITESHEET.get_frames(1, 16, 16, 2, new_size=(64, 64),
                                            colorkey=(0, 0, 0))
    HERO_HIT = HERO_SPRITESHEET.get_frames(2, 16, 16, 8, new_size=(64, 64),
                                           colorkey=(0, 0, 0))

    EFFECTS_SOUNDS = SoundsList()
    PICKAXE_SOUNDS = [(pg.mixer.Sound('data/sounds/Effects/Rock_hit-1.mp3'),
                      pg.mixer.Sound('data/sounds/Effects/Rock_hit-2.mp3'),
                      pg.mixer.Sound('data/sounds/Effects/Rock_hit-3.mp3')),
                      (pg.mixer.Sound('data/sounds/Effects/Wood_hit-1.mp3'),),
                      (pg.mixer.Sound('data/sounds/Effects/Crate_crash.mp3'),)]
    for sounds in PICKAXE_SOUNDS:
        for sound in sounds:
            EFFECTS_SOUNDS.add(sound)

    MAPS_DICT = {}
    for number, image in enumerate(os.listdir('data/maps/map_previews')):
        MAPS_DICT[number] = (pg.image.load(f'data/maps/map_previews/{image}'), image)

    def __init__(self) -> None:
        self._to_quit = False
        self._main_run = False

        self._interface_volume = 1.0

        self._effects_volume = 1.0

        self._music_sounds = SoundsList()
        self._music_volume = 1.0

        self._all_sprites = pg.sprite.Group()
        self._obstacles = pg.sprite.Group()
        self._breakable = pg.sprite.Group()
        self._particles = Particles()
        self._chests = []
        self._borders = []
        self._creatures = pg.sprite.Group()
        self._camera_group = CameraGroup(self)

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
        interface_sounds = SoundsList()
        snowflakes = Particles()

        start_button = DefaultButton((self.MONITOR_W * 0.11 + self.MONITOR_W * 0.09,
                                      self.MONITOR_H * 0.88 + self.MONITOR_H * 0.04),
                                     self.MONITOR_W * 0.19, self.MONITOR_H * 0.08,
                                     self.START_BUTTON[0], hover_image=self.START_BUTTON[1],
                                     sound='click.wav', group=buttons_group)
        interface_sounds.add(start_button._sound)
        settings_button = DefaultButton((start_button._rect.right + self.MONITOR_W * 0.008
                                         + (start_button._rect.w >> 1),
                                         self.MONITOR_H * 0.88 + self.MONITOR_H * 0.04),
                                        self.MONITOR_W * 0.19, self.MONITOR_H * 0.08,
                                        self.SETTINGS_BUTTON[0], hover_image=self.SETTINGS_BUTTON[1],
                                        sound='click.wav', group=buttons_group)
        interface_sounds.add(settings_button._sound)
        credits_button = DefaultButton((settings_button._rect.right + self.MONITOR_W * 0.008
                                        + (settings_button._rect.w >> 1),
                                        self.MONITOR_H * 0.88 + self.MONITOR_H * 0.04),
                                       self.MONITOR_W * 0.19, self.MONITOR_H * 0.08,
                                       self.CREDITS_BUTTON[0], self.CREDITS_BUTTON[1],
                                       sound='click.wav', group=buttons_group)
        interface_sounds.add(credits_button._sound)
        quit_button = DefaultButton((credits_button._rect.right + self.MONITOR_W * 0.008
                                     + (credits_button._rect.w >> 1),
                                     self.MONITOR_H * 0.88 + self.MONITOR_H * 0.04),
                                    self.MONITOR_W * 0.19, self.MONITOR_H * 0.08,
                                    self.QUIT_BUTTON, sound='click.wav', group=buttons_group)
        interface_sounds.add(quit_button._sound)

        interface_sounds.set_volume(self._interface_volume)

        clock = pg.time.Clock()
        run = True
        while run:
            clock.tick(self.FPS)

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
                elif event.type == pg.USEREVENT and event.button == credits_button:
                    pass
                buttons_group.handle(event)

            buttons_group.check_hover(pg.mouse.get_pos())

            screen.blit(self.MENU_BG, (0, 0))
            snowflake = Snowflake(self, (random.randrange(0, self.MONITOR_W - 20), 0), self.FPS)
            snowflakes.add(snowflake)
            snowflakes.update(screen)

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
                                   self.BUTTON, text='Return', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        next_map = DefaultButton(((self.MONITOR_W >> 1) + (preview_rect.width >> 1) + 30, self.MONITOR_H >> 1),
                                 self.MONITOR_W * 0.02, 50, self.RIGHT_ARROW, sound='click.wav',
                                 group=buttons_group)
        previous_map = DefaultButton(((self.MONITOR_W >> 1) - (preview_rect.width >> 1) - 30, self.MONITOR_H >> 1),
                                     self.MONITOR_W * 0.02, 50, self.LEFT_ARROW, sound='click.wav',
                                     group=buttons_group)
        start = DefaultButton((self.MONITOR_W >> 1, self.MONITOR_H * 0.7),
                              self.MONITOR_W * 0.1, self.MONITOR_H * 0.1, self.BUTTON, sound='click.wav',
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

            screen.fill(self.BACKGROUND)
            pg.draw.polygon(screen, (0, 0, 0), ((preview_rect.topleft[0] - 5, preview_rect.topleft[1] - 5),
                                                (preview_rect.topright[0] + 5, preview_rect.topright[1] - 5),
                                                (preview_rect.bottomright[0] + 5, preview_rect.bottomright[1] + 5),
                                                (preview_rect.bottomleft[0] - 5, preview_rect.bottomleft[1] + 5)),
                            5)
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

        UI_text = self._font.render('UI sounds', True, (0, 0, 0))
        effects_text = self._font.render('Effects sounds', True, (0, 0, 0))

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
        interface_sounds = SoundsList()

        return_btn = DefaultButton((150, 100), 200, 100,
                                   self.BUTTON, text='Return', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(return_btn._sound)
        volume_btn = DefaultButton((150, 250), 200, 100,
                                   self.BUTTON, text='volume', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group)
        interface_sounds.add(volume_btn._sound)
        video_btn = DefaultButton((150, 400), 200, 100,
                                  self.BUTTON, text='video', text_size=self._font_size,
                                  sound='click.wav', group=buttons_group)
        interface_sounds.add(video_btn._sound)

        volume_buttons = ButtonGroup()
        UI_slider = Slider((volume_rect.w * 0.4 + volume_rect.topleft[0],
                            volume_rect.h * 0.1 + volume_rect.topleft[1]),
                           volume_rect.w * 0.4, 60,
                           slider_color=(126, 134, 148))
        decrease_UI = DefaultButton((volume_rect.w * 0.35 + volume_rect.topleft[0],
                                     volume_rect.h * 0.12 + volume_rect.topleft[1]),
                                    volume_rect.w * 0.05, 50,
                                    self.LEFT_ARROW,
                                    sound='click.wav', group=volume_buttons)
        interface_sounds.add(decrease_UI._sound)
        increase_UI = DefaultButton((volume_rect.w * 0.85 + volume_rect.topleft[0],
                                     volume_rect.h * 0.12 + volume_rect.topleft[1]),
                                    volume_rect.w * 0.05, 50,
                                    self.RIGHT_ARROW,
                                    sound='click.wav', group=volume_buttons)
        interface_sounds.add(increase_UI._sound)
        effects_slider = Slider((volume_rect.w * 0.4 + volume_rect.topleft[0],
                                 volume_rect.h * 0.2 + volume_rect.topleft[1]),
                                volume_rect.w * 0.4, 60,
                                slider_color=(126, 134, 148))
        decrease_effects = DefaultButton((volume_rect.w * 0.35 + volume_rect.topleft[0],
                                          volume_rect.h * 0.22 + volume_rect.topleft[1]),
                                         volume_rect.w * 0.05, 50,
                                         self.LEFT_ARROW,
                                         sound='click.wav', group=volume_buttons)
        interface_sounds.add(decrease_effects._sound)
        increase_effects = DefaultButton((volume_rect.w * 0.85 + volume_rect.topleft[0],
                                          volume_rect.h * 0.22 + volume_rect.topleft[1]),
                                         volume_rect.w * 0.05, 50,
                                         self.RIGHT_ARROW,
                                         sound='click.wav', group=volume_buttons)
        interface_sounds.add(increase_effects._sound)

        interface_sounds.set_volume(self._interface_volume)

        UI_value = int(self._interface_volume * 10)
        UI_slider.change(UI_value)
        effects_value = int(self._effects_volume * 10)
        effects_slider.change(effects_value)

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

                elif event.type == pg.USEREVENT and event.button == decrease_UI and 0 < UI_value <= 10:
                    UI_value -= 1
                    UI_slider.change(UI_value)
                    self._interface_volume = UI_value / 10
                    interface_sounds.set_volume(self._interface_volume)
                elif event.type == pg.USEREVENT and event.button == increase_UI and 0 <= UI_value < 10:
                    UI_value += 1
                    UI_slider.change(UI_value)
                    self._interface_volume = UI_value / 10
                    interface_sounds.set_volume(self._interface_volume)

                elif event.type == pg.USEREVENT and event.button == decrease_effects and 0 < effects_value <= 10:
                    effects_value -= 1
                    effects_slider.change(effects_value)
                    self._effects_volume = effects_value / 10
                elif event.type == pg.USEREVENT and event.button == increase_effects and 0 <= effects_value < 10:
                    effects_value += 1
                    effects_slider.change(effects_value)
                    self._effects_volume = effects_value / 10

                if event.type == pg.QUIT:
                    run = False
                    self.terminate()

                if settings_state == 0:
                    volume_buttons.handle(event)
                buttons_group.handle(event)

            screen.fill(self.BACKGROUND)
            if settings_state != -1:
                screen.blit(states[settings_state], (self.MONITOR_W * 0.22, self.MONITOR_H * 0.05))
                if settings_state == 0:
                    UI_slider.draw(screen)
                    effects_slider.draw(screen)
                    volume_buttons.draw(screen)
                    volume_buttons.check_hover(pg.mouse.get_pos())
                    screen.blit(UI_text, (volume_rect.topleft[0] + self.MONITOR_W * 0.05,
                                          volume_rect.topleft[1] + self.MONITOR_H * 0.08))
                    screen.blit(effects_text, (volume_rect.topleft[0] + self.MONITOR_W * 0.05,
                                               volume_rect.topleft[1] + self.MONITOR_H * 0.18))

            buttons_group.check_hover(pg.mouse.get_pos())
            buttons_group.draw(screen)
            pg.display.update()

    def pause_menu(self) -> None:
        pause_surf = pg.Surface((480, 720))
        pause_surf.fill((98, 104, 115, 150))
        pause_pos = (self.MONITOR_W >> 1, self.MONITOR_H >> 1)
        pause_rect = pause_surf.get_rect(center=pause_pos)

        pause_buttons = ButtonGroup()
        interface_sounds = SoundsList()

        continue_button = DefaultButton((pause_rect.centerx, pause_rect.centery - 200), 200, 100,
                                        self.BUTTON, text='continue', text_size=self._font_size,
                                        sound='click.wav', group=pause_buttons)
        interface_sounds.add(continue_button._sound)
        quit_to_menu = DefaultButton((pause_rect.centerx, pause_rect.centery + 200), 200, 100,
                                     self.BUTTON, text='menu', text_size=self._font_size,
                                     sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_to_menu._sound)
        quit_from_the_game = DefaultButton((pause_rect.centerx, pause_rect.centery + 300), 200, 100,
                                           self.BUTTON, text='exit', text_size=self._font_size,
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
        self._main_screen = pg.display.set_mode((0, 0), pg.FULLSCREEN, pg.DOUBLEBUF)
        if self._all_sprites:
            for sprite in self._all_sprites:
                sprite.kill()

        map_data = get_map_data(f'data/maps/{lvl_name}.dat')
        player_pos = get_player_pos(map_data)
        self._field = self.get_map_surface(map_data)
        self._main_screen.blit(self._field, (0, 0))

        map_width = len(map_data[0]) * self.TILE_SIZE
        map_height = len(map_data) * self.TILE_SIZE
        self._borders.append(Border(self, -30, map_width + 30, -30, -30))  # Top
        self._borders.append(Border(self, -30, map_width + 30, map_height + 30, map_height + 30))  # Bot
        self._borders.append(Border(self, -30, -30, -30, map_height + 30))  # Left
        self._borders.append(Border(self, map_width + 30, map_width + 30, -30, map_height + 30))  # Right

        self._hero = Hero(self, player_pos, self.FPS, 5,
                          self.HERO_IDLE, self.HERO_MOVE, self.HERO_HIT)

    def game(self, lvl_name: str):
        self.restart_game(lvl_name)
        self._hero: Hero

        self.EFFECTS_SOUNDS.set_volume(self._effects_volume)
        cur_sound = 0

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
        prev_hit = pg.time.get_ticks()

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
            for sprite in self._borders:
                self._main_screen.blit(sprite.image, sprite.rect.topleft)
            self._camera_group.custom_draw(self._hero, self._main_screen)

            for chest in self._chests:
                if chest.check_position(self._hero) and not chest.is_open:
                    offset = self._camera_group.get_offset(self._hero)
                    offset_pos = chest.rect.topleft - offset
                    chest.show_hint(self, (int(offset_pos.x) + (chest.rect.w >> 1),
                                           int(offset_pos.y) - 50), self._main_screen)
                    chest.open_chest()

            for obstacle in self._breakable:
                obstacle: SimpleObject

                offset = self._camera_group.get_offset(self._hero)
                obstacle_offset = obstacle.rect.topleft - offset
                if (obstacle.check_position(self._hero)
                        and self._hero.check_hit(obstacle_offset, obstacle.rect.w, pg.mouse.get_pos())
                        and pg.time.get_ticks() - prev_hit > 800):
                    obstacle.hit(self, (obstacle_offset[0] + (obstacle.rect.w >> 1),
                                        obstacle_offset[1] + (obstacle.rect.h >> 1)))

                    if obstacle.MATERIAL == Materials.WOOD and obstacle._hp != 0:
                        self.PICKAXE_SOUNDS[1][0].play()
                    elif obstacle.MATERIAL == Materials.WOOD and obstacle._hp == 0:
                        self.PICKAXE_SOUNDS[2][0].play()
                    else:
                        self.PICKAXE_SOUNDS[0][cur_sound % 3].play()
                        cur_sound += 1
                    prev_hit = pg.time.get_ticks()
                    break

            if self._particles.sprites():
                self._particles.update(self._main_screen)

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
                    if int(data[y][x]) == Objects.CHEST:
                        self._chests.append(Chest(self, x, y))
                    elif int(data[y][x]) == Objects.CRATE:
                        Crate(self, x, y, self._breakable)
                    else:
                        SimpleObject(self, int(data[y][x]), x, y, self._breakable)
        return lvl_map

    @staticmethod
    def terminate() -> None:
        pg.quit()
        sys.exit(1)


if __name__ == '__main__':
    game = Game()
    game.main()
    input()
