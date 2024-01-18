import os.path
import random
import sqlite3
import sys
import time

import pandas as pd
import pygame as pg

pg.display.set_mode((0, 0))

from data.scripts.utils import (load_with_colorkey, scale_with_colorkey, create_bg, show_coords, show_mouse_coords,
                                show_fps, check_distance, show_hint)
from data.scripts.sprites import Hero, SpriteSheet
from data.scripts.inventory import Inventory, Cell
from data.scripts.mapReader import get_map_data, get_player_pos
from data.scripts.obstacles import SimpleObject, Border, Objects, Chest, Crate, Loot
from data.scripts.particles import Particles, Snowflake, Materials
from data.scripts.UI import DefaultButton, ButtonGroup, Slider, Counter
from data.scripts.sounds import SoundsList
from data.scripts.camera import CameraGroup

pg.init()
pg.mixer.init()


class Game:
    FPS = 60
    BACKGROUND = pg.Color('#818181')
    TILE_SIZE = 72
    MONITOR_SIZE = MONITOR_W, MONITOR_H = pg.display.Info().current_w, pg.display.Info().current_h

    PRICES = {'copper': 10,
              'iron': 15,
              'ruby': 50,
              'sapphire': 25}

    MENU_BG = pg.transform.scale(pg.image.load('data/images/UI/menu_bg.png'),
                                 (MONITOR_W, MONITOR_H))
    GAME_BG_TILE = pg.transform.scale(pg.image.load('data/images/objects/game_bg.png'), (100, 100))
    sheet = SpriteSheet(pg.image.load('data/images/UI/menu_buttons.png'))

    START_BUTTON = sheet.get_frames(0, 1451, 345, 2, colorkey=(0, 0, 0))
    SETTINGS_BUTTON = sheet.get_frames(1, 1451, 345, 2, colorkey=(0, 0, 0))
    CREDITS_BUTTON = sheet.get_frames(2, 1451, 345, 2, colorkey=(0, 0, 0))
    QUIT_BUTTON = sheet.cut_image((0, 1035), 1451, 345, colorkey=(0, 0, 0))
    SAVE_BUTTON = pg.image.load('data/images/UI/save_btn.png')
    TRASH = pg.image.load('data/images/UI/trash-can.png')

    sheet = SpriteSheet(pg.image.load('data/images/UI/wooden-buttons.png'))
    BUTTON = load_with_colorkey('data/images/UI/button.png')
    PAUSE_BUTTON = sheet.cut_image((1957, 2503), 1636, 629, colorkey=(0, 0, 0))
    PAUSE_MENU = sheet.cut_image((1961, 1634), 1630, 633, colorkey=(0, 0, 0))
    LEVEL_BTN = sheet.cut_image((35, 0), 1660, 580, colorkey=(0, 0, 0))
    HINT_BUTTON = load_with_colorkey('data/images/UI/hint_btn.png')
    LEFT_ARROW = pg.image.load('data/images/UI/left_arrow.png')
    RIGHT_ARROW = pg.image.load('data/images/UI/right_arrow.png')

    HEART_IMG = pg.transform.scale(pg.image.load('data/images/UI/heart.png'), (48, 48))

    HERO_SPRITESHEET = SpriteSheet(pg.image.load('data/images/creatures/hero.png'))
    HERO_IDLE = HERO_SPRITESHEET.get_frames(0, 16, 16, 18, new_size=(54, 54),
                                            colorkey=(0, 0, 0))
    HERO_MOVE = HERO_SPRITESHEET.get_frames(1, 16, 16, 2, new_size=(54, 54),
                                            colorkey=(0, 0, 0))
    HERO_HIT = HERO_SPRITESHEET.get_frames(2, 16, 16, 8, new_size=(54, 54),
                                           colorkey=(0, 0, 0))

    sheet = SpriteSheet(pg.image.load('data/images/objects/obstacles.png'))
    ROCKS = [sheet.cut_image((0, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
             sheet.cut_image((16, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
             sheet.cut_image((32, 0), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))]
    ORES = [sheet.cut_image((0, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
            sheet.cut_image((16, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
            sheet.cut_image((32, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0)),
            sheet.cut_image((48, 16), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))]
    CRATE = sheet.cut_image((0, 32), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))
    CHEST_CLOSED = sheet.cut_image((0, 48), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))
    CHEST_OPEN = sheet.cut_image((16, 48), 16, 16, new_size=(72, 72), colorkey=(0, 0, 0))

    sheet = SpriteSheet(pg.image.load('data/images/objects/store.png'))
    STORE_ANIM = sheet.get_frames(0, 128, 128, 4, new_size=(512, 512), colorkey=(0, 0, 0))

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
        settings = pd.read_csv('data/saves/settings.csv', delimiter=';')
        settings = settings['value']

        self._selected_save_file = 0

        self._to_quit = False
        self._main_run = False

        self._interface_volume = settings[0]

        self._effects_volume = settings[1]

        self._music_sounds = SoundsList()
        self._music_volume = settings[2]

        self._all_sprites = pg.sprite.Group()
        self._obstacles = pg.sprite.Group()
        self._breakable = pg.sprite.Group()
        self._picked = pg.sprite.Group()
        self._particles = Particles()
        self._chests = []
        self._borders = []
        self._creatures = pg.sprite.Group()
        self._camera_group = CameraGroup(self)

        self._hero: Hero | None = None
        self._inventory: Inventory | None = None
        self.store_rect = None
        self._counter: Counter | None = None
        self.t = 0
        self.real_fps = 0

        self.current_map = 0
        self._main_screen: pg.Surface | None = None
        self._map_conditions = {}
        self._field: pg.Surface | None = None

        self._font_scale = round(self.MONITOR_W // 16) >> 1
        self._font_size = round(0.8 * self._font_scale)
        self._font = pg.font.Font(None, self._font_size)

    def main(self) -> None:
        self.main_menu()

    def create_save_button(self, save_number: int, pos: tuple[int, int], file_window_rect: pg.Rect,
                           font: pg.font.Font, group: ButtonGroup,
                           sql_cur: sqlite3.Cursor) -> tuple[DefaultButton, pg.Surface, pg.Rect, pg.Surface, pg.Rect]:
        file_1_button = DefaultButton(pos, file_window_rect.w * 0.7, file_window_rect.h * 0.16, self.SAVE_BUTTON,
                                      sound='click.wav', group=group)
        file_1_button_rect = file_1_button._rect
        file_1_count = sql_cur.execute(f'''SELECT money FROM hero_stats
         WHERE save_id == "{save_number}"''').fetchone()[0]
        count_surf = font.render(f'money: {file_1_count}', True, (255, 255, 255))
        count_rect = count_surf.get_rect(topleft=(file_1_button_rect.centerx + (file_1_button_rect.w >> 2),
                                                  file_1_button_rect.bottom - 50))
        file_name_surf = font.render(f'File {save_number}', True, (255, 255, 255))
        file_name_rect = file_name_surf.get_rect(topleft=(file_1_button_rect.left + 20, file_1_button_rect.top + 20))

        return file_1_button, count_surf, count_rect, file_name_surf, file_name_rect

    @staticmethod
    def _clear_save_file(file: int, font: pg.font.Font) -> pg.Surface:
        con = sqlite3.connect('data/saves/saves.sqlite')
        cur = con.cursor()
        cur.execute(f"""UPDATE hero_stats SET hp = 100, speed = 6, money = 0
    WHERE save_id == {file}""")
        cur.execute(f"""UPDATE levels set [level 1] = 0, [level 2] = 0, [level 3] = 0, [level 4] = 0, [level 5] = 0
    WHERE save_id == {file}""")
        con.commit()

        return font.render(f'money: 0', True, (255, 255, 255))

    def main_menu(self) -> None:
        con = sqlite3.connect('data/saves/saves.sqlite')
        cur = con.cursor()

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

        credits_surf = pg.Surface((self.MONITOR_W * 0.4, self.MONITOR_H * 0.4))
        credits_rect = credits_surf.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        credits_font = pg.font.Font(None, self._font_size)
        author_font = pg.font.Font(None, round(self._font_size * 1.5))
        author_2_font = pg.font.Font(None, round(self._font_size * 0.5))
        authors_text_surf = credits_font.render('Authors', False, (255, 255, 255))
        name_text_surf = author_font.render('Dmitry Skorokhodov', True, (255, 255, 255))
        name1_rect = name_text_surf.get_rect(center=(credits_rect.centerx, credits_rect.h * 0.4 + credits_rect.top))
        name2_text_surf = author_2_font.render('Matvey Polupanov', True, (255, 255, 255))
        name2_rect = name2_text_surf.get_rect(center=(credits_rect.centerx, credits_rect.h * 0.6 + credits_rect.top))
        credits_surf.fill('black')
        credits_surf.set_alpha(128)

        file_surf = pg.Surface((self.MONITOR_W * 0.4, self.MONITOR_H * 0.6))
        file_rect = file_surf.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        file_surf.fill((0, 0, 0))
        file_surf.set_alpha(128)
        files_font = pg.font.Font(None, round(self._font_size * 0.5))
        file_buttons = ButtonGroup()

        back_btn = DefaultButton((file_rect.left + file_rect.w * 0.05, file_rect.top + file_rect.h * 0.05),
                                 file_rect.w * 0.1, file_rect.h * 0.1, self.SAVE_BUTTON, sound='click.wav',
                                 text='<-', text_size=self._font_size, group=file_buttons)
        (file_btn_1, count_surf_1, count_rect_1,
         file_name_1,
         file_name_1_rect) = self.create_save_button(1, (
            file_rect.centerx, file_rect.top + file_rect.h * 0.23), file_rect, files_font, file_buttons, cur)
        delete_1 = DefaultButton((file_rect.right - file_rect.w * 0.1, file_rect.top + file_rect.h * 0.21),
                                 50, 50, self.TRASH, sound='click.wav', group=file_buttons)
        (file_btn_2, count_surf_2, count_rect_2,
         file_name_2, file_name_2_rect) = self.create_save_button(2, (
            file_rect.centerx, file_rect.top + file_rect.h * 0.53), file_rect, files_font, file_buttons, cur)
        delete_2 = DefaultButton((file_rect.right - file_rect.w * 0.1, file_rect.top + file_rect.h * 0.51),
                                 50, 50, self.TRASH, sound='click.wav', group=file_buttons)
        (file_btn_3, count_surf_3, count_rect_3,
         file_name_3, file_name_3_rect) = self.create_save_button(3, (
            file_rect.centerx, file_rect.top + file_rect.h * 0.83), file_rect, files_font, file_buttons, cur)
        delete_3 = DefaultButton((file_rect.right - file_rect.w * 0.1, file_rect.top + file_rect.h * 0.81),
                                 50, 50, self.TRASH, sound='click.wav', group=file_buttons)

        clock = pg.time.Clock()
        show_credits = False
        show_file_select = False
        run = True
        while run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.USEREVENT and (event.button == start_button or event.button == back_btn):
                    show_file_select = not show_file_select
                elif (event.type == pg.USEREVENT and event.button == quit_button) or event.type == pg.QUIT:
                    run = False
                    pg.time.delay(500)
                    self._to_quit = True
                elif event.type == pg.USEREVENT and event.button == settings_button:
                    run = False
                    self.settings_menu()
                elif event.type == pg.USEREVENT and event.button == credits_button:
                    show_credits = not show_credits

                elif event.type == pg.USEREVENT and event.button == file_btn_1:
                    run = False
                    self._selected_save_file = 1
                    self.select_level()
                elif event.type == pg.USEREVENT and event.button == file_btn_2:
                    run = False
                    self._selected_save_file = 2
                    self.select_level()
                elif event.type == pg.USEREVENT and event.button == file_btn_3:
                    run = False
                    self._selected_save_file = 3
                    self.select_level()

                elif event.type == pg.USEREVENT and event.button == delete_1:
                    count_surf_1 = self._clear_save_file(1, files_font)
                elif event.type == pg.USEREVENT and event.button == delete_2:
                    count_surf_2 = self._clear_save_file(2, files_font)
                elif event.type == pg.USEREVENT and event.button == delete_3:
                    count_surf_3 = self._clear_save_file(3, files_font)

                buttons_group.handle(event)
                if show_file_select:
                    file_buttons.handle(event)

            file_buttons.check_hover(pg.mouse.get_pos())
            buttons_group.check_hover(pg.mouse.get_pos())

            screen.blit(self.MENU_BG, (0, 0))
            snowflake = Snowflake(self, (random.randrange(0, self.MONITOR_W - 20), 0), self.FPS)
            snowflakes.add(snowflake)
            snowflakes.update(screen)

            if show_credits:
                screen.blit(credits_surf, credits_rect)
                screen.blit(authors_text_surf,
                            (credits_rect.centerx - (authors_text_surf.get_width() >> 1), credits_rect.top + 50))
                screen.blit(name_text_surf, name1_rect)
                screen.blit(name2_text_surf, name2_rect)

            if show_file_select:
                screen.blit(file_surf, file_rect)
                file_buttons.draw(screen)
                screen.blit(count_surf_1, count_rect_1)
                screen.blit(file_name_1, file_name_1_rect)
                screen.blit(count_surf_2, count_rect_2)
                screen.blit(file_name_2, file_name_2_rect)
                screen.blit(count_surf_3, count_rect_3)
                screen.blit(file_name_3, file_name_3_rect)

            buttons_group.draw(screen)

            pg.display.update()

        if self._to_quit:
            self.terminate()

    def select_level(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        preview_img, preview_rect, name_rect, name, name_surf = self.get_preview_values(
            *self.MAPS_DICT[self.current_map % len(self.MAPS_DICT)])

        buttons_group = ButtonGroup()
        return_btn = DefaultButton((150, 100), self.MONITOR_W * 0.1, self.MONITOR_H * 0.05,
                                   self.LEVEL_BTN, text='Return', text_size=self._font_size,
                                   sound='click.wav', group=buttons_group, colorkey=(0, 0, 0))
        next_map = DefaultButton(((self.MONITOR_W >> 1) + (preview_rect.width >> 1) + 30, self.MONITOR_H >> 1),
                                 self.MONITOR_W * 0.02, 50, self.RIGHT_ARROW, sound='click.wav',
                                 group=buttons_group)
        previous_map = DefaultButton(((self.MONITOR_W >> 1) - (preview_rect.width >> 1) - 30, self.MONITOR_H >> 1),
                                     self.MONITOR_W * 0.02, 50, self.LEFT_ARROW, sound='click.wav',
                                     group=buttons_group)
        start = DefaultButton((self.MONITOR_W >> 1, self.MONITOR_H * 0.7),
                              self.MONITOR_W * 0.1, self.MONITOR_H * 0.05, self.LEVEL_BTN, sound='click.wav',
                              group=buttons_group, text='Start', text_size=self._font_size, colorkey=(0, 0, 0))

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
        con = sqlite3.connect('data/saves/saves.sqlite')
        cur = con.cursor()

        preview_img = pg.transform.scale(image, (self.MONITOR_W * 0.3, self.MONITOR_H * 0.25))
        name = name[:name.find('.')]

        if cur.execute(f"""SELECT [{name}] FROM levels
         WHERE save_id == {self._selected_save_file}""").fetchone()[0] == 1:
            write_name = name + ' (completed)'
        else:
            write_name = name

        name_surf = self._font.render(write_name, True, (0, 0, 0))
        preview_rect = preview_img.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        name_rect = name_surf.get_rect(center=(preview_rect.midtop[0], preview_rect.midtop[1] - 100))

        return preview_img, preview_rect, name_rect, name, name_surf

    def settings_menu(self) -> None:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        UI_text = self._font.render('UI sounds', True, (0, 0, 0))
        effects_text = self._font.render('Effects sounds', True, (0, 0, 0))
        music_text = self._font.render('Music', True, (0, 0, 0))

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
        music_slider = Slider((volume_rect.w * 0.4 + volume_rect.topleft[0],
                               volume_rect.h * 0.3 + volume_rect.topleft[1]),
                              volume_rect.w * 0.4, 60,
                              slider_color=(126, 134, 148))
        decrease_music = DefaultButton((volume_rect.w * 0.35 + volume_rect.topleft[0],
                                        volume_rect.h * 0.32 + volume_rect.topleft[1]),
                                       volume_rect.w * 0.05, 50,
                                       self.LEFT_ARROW,
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(decrease_music._sound)
        increase_music = DefaultButton((volume_rect.w * 0.85 + volume_rect.topleft[0],
                                        volume_rect.h * 0.32 + volume_rect.topleft[1]),
                                       volume_rect.w * 0.05, 50,
                                       self.RIGHT_ARROW,
                                       sound='click.wav', group=volume_buttons)
        interface_sounds.add(increase_music._sound)

        interface_sounds.set_volume(self._interface_volume)

        UI_value = int(self._interface_volume * 10)
        UI_slider.change(UI_value)
        effects_value = int(self._effects_volume * 10)
        effects_slider.change(effects_value)
        music_value = int(self._music_volume * 10)
        music_slider.change(music_value)

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

                elif event.type == pg.USEREVENT and event.button == decrease_music and 0 < music_value <= 10:
                    music_value -= 1
                    music_slider.change(music_value)
                    self._music_volume = music_value / 10
                elif event.type == pg.USEREVENT and event.button == increase_music and 0 <= music_value < 10:
                    music_value += 1
                    music_slider.change(music_value)
                    self._music_volume = music_value / 10

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
                    music_slider.draw(screen)
                    volume_buttons.draw(screen)
                    volume_buttons.check_hover(pg.mouse.get_pos())
                    screen.blit(UI_text, (volume_rect.topleft[0] + self.MONITOR_W * 0.05,
                                          volume_rect.topleft[1] + self.MONITOR_H * 0.08))
                    screen.blit(effects_text, (volume_rect.topleft[0] + self.MONITOR_W * 0.05,
                                               volume_rect.topleft[1] + self.MONITOR_H * 0.18))
                    screen.blit(music_text, (volume_rect.topleft[0] + self.MONITOR_W * 0.05,
                                             volume_rect.topleft[1] + self.MONITOR_H * 0.28))

            buttons_group.check_hover(pg.mouse.get_pos())
            buttons_group.draw(screen)
            pg.display.update()

    def confirm_choice(self, store_frame: int, pause_surf: pg.Surface, pause_rect: pg.Rect,
                       pause_buttons: ButtonGroup) -> bool:
        confirm_surf = pg.Surface((self.MONITOR_W * 0.2, self.MONITOR_H * 0.2))
        confirm_rect = confirm_surf.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        confirm_surf.set_alpha(170)
        text_surf = (pg.font.Font(None, round(self._font_size * 0.5)).
                     render('Are you sure you want to exit?', True, (255, 255, 255)))
        text_rect = text_surf.get_rect(center=(confirm_rect.centerx, confirm_rect.top + confirm_rect.h * 0.2))

        button_group = ButtonGroup()
        yes_btn = DefaultButton((confirm_rect.left + confirm_rect.w * 0.3, confirm_rect.centery),
                                confirm_rect.w * 0.3, confirm_rect.h * 0.2, self.SAVE_BUTTON, sound='click.wav',
                                text='YES', text_size=round(self._font_size * 0.5), group=button_group)
        no_btn = DefaultButton((confirm_rect.left + confirm_rect.w * 0.7, confirm_rect.centery),
                               confirm_rect.w * 0.3, confirm_rect.h * 0.2, self.SAVE_BUTTON, sound='click.wav',
                               text='NO', text_size=round(self._font_size * 0.5), group=button_group)

        run = True
        while run:
            for event in pg.event.get():
                if ((event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
                        or (event.type == pg.USEREVENT and event.button == no_btn)):
                    return False
                elif event.type == pg.USEREVENT and event.button == yes_btn:
                    return True

                button_group.handle(event)
            button_group.check_hover(pg.mouse.get_pos())

            self._camera_group.custom_draw(self._hero, self._main_screen, self._counter,
                                           (self.STORE_ANIM[store_frame % 4], self.store_rect), True)
            pause_buttons.draw(self._main_screen)
            self._main_screen.blit(pause_surf, pause_rect)
            self._main_screen.blit(confirm_surf, confirm_rect)
            button_group.draw(self._main_screen)
            self._main_screen.blit(text_surf, text_rect)

            pg.display.update()

    def pause_menu(self, store_frame: int) -> None:
        pause_surf = pg.Surface((480, 720), depth=32)
        pause_surf.fill((102, 109, 112))
        pause_surf.set_alpha(180)

        pause_pos = (self.MONITOR_W >> 1, self.MONITOR_H >> 1)
        pause_rect = pause_surf.get_rect(center=pause_pos)

        pause_buttons = ButtonGroup()
        interface_sounds = SoundsList()

        continue_button = DefaultButton((pause_rect.centerx, pause_rect.centery - 200), 250, 100,
                                        self.PAUSE_BUTTON, text='continue', text_size=self._font_size,
                                        sound='click.wav', group=pause_buttons, colorkey=(0, 0, 0))
        interface_sounds.add(continue_button._sound)
        quit_to_menu = DefaultButton((pause_rect.centerx, pause_rect.centery + 200), 200, 80,
                                     self.PAUSE_MENU, text='menu', text_size=self._font_size,
                                     sound='click.wav', group=pause_buttons, colorkey=(0, 0, 0))
        interface_sounds.add(quit_to_menu._sound)
        quit_from_the_game = DefaultButton((pause_rect.centerx, pause_rect.centery + 300), 200, 50,
                                           self.QUIT_BUTTON, sound='click.wav', group=pause_buttons)
        interface_sounds.add(quit_from_the_game._sound)

        interface_sounds.set_volume(self._interface_volume)

        run = True
        while run:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) \
                        or (event.type == pg.USEREVENT and event.button == continue_button):
                    run = False
                elif event.type == pg.USEREVENT and event.button == quit_to_menu:
                    if self.confirm_choice(store_frame, pause_surf, pause_rect, pause_buttons):
                        run = False
                        self._main_run = False
                        self.select_level()
                elif (event.type == pg.USEREVENT and event.button == quit_from_the_game) or event.type == pg.QUIT:
                    if self.confirm_choice(store_frame, pause_surf, pause_rect, pause_buttons):
                        pg.time.delay(500)
                        self.terminate()
                pause_buttons.handle(event)

            self._camera_group.custom_draw(self._hero, self._main_screen, self._counter,
                                           (self.STORE_ANIM[store_frame % 4], self.store_rect), True)

            self._main_screen.blit(pause_surf, pause_rect)

            pause_buttons.check_hover(pg.mouse.get_pos())
            pause_buttons.draw(self._main_screen)

            pg.display.update()

    def restart_game(self, lvl_name: str) -> int:
        con = sqlite3.connect('data/saves/saves.sqlite')
        cur = con.cursor()

        hero_hp, hero_speed, start_money = cur.execute(f"""SELECT hp, speed, money FROM hero_stats
    WHERE save_id == {self._selected_save_file}""").fetchall()[0]

        self._main_screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        if self._all_sprites:
            for sprite in self._all_sprites:
                sprite.kill()

        map_data, self._map_conditions = get_map_data(f'data/maps/{lvl_name}.dat')
        player_pos = get_player_pos(map_data)
        self._field = self.get_map_surface(map_data)
        background = create_bg(self._field.get_size(), self.GAME_BG_TILE)
        self._camera_group.set_bg(background)
        self._main_screen.blit(self._field, (0, 0))

        map_width = len(map_data[0]) * self.TILE_SIZE
        map_height = len(map_data) * self.TILE_SIZE
        self._borders.append(Border(self, -30, map_width + 30, -30, -30))  # Top
        self._borders.append(Border(self, -30, map_width + 30, map_height + 30, map_height + 30))  # Bot
        self._borders.append(Border(self, -30, -30, -30, map_height + 30))  # Left
        self._borders.append(Border(self, map_width + 30, map_width + 30, -30, map_height + 30))  # Right

        self._hero = Hero(self, player_pos, self.FPS, hero_hp, hero_speed, 5,
                          self.HERO_IDLE, self.HERO_MOVE, self.HERO_HIT)
        self._inventory = Inventory(self._hero)

        return start_money

    def game(self, lvl_name: str):
        start_money = self.restart_game(lvl_name)
        self._hero: Hero

        self.EFFECTS_SOUNDS.set_volume(self._effects_volume)
        cur_sound = 0

        ui = ButtonGroup()
        ui_sprites = pg.sprite.Group()
        hp_bar = Slider((75, 20), 300, 50, (5, 5, 5),
                        (227, 25, 25), self._hero.get_cur_hp())
        heart = pg.sprite.Sprite()
        heart.image = self.HEART_IMG
        heart.rect = (20, 20, 64, 64)
        ui_sprites.add(heart)
        ui.add(hp_bar)
        self._counter = Counter((self.MONITOR_W - 250, 20), 300, 50, start_money,
                                number_color=(255, 255, 255), group=ui)
        end_text_upper = self._font.render("You've reached the quota.",
                                           True, (0, 0, 0, 255)).convert_alpha()
        end_text_lower = self._font.render("press Enter to leave.",
                                           True, (0, 0, 0, 255)).convert_alpha()
        goal_text = (pg.font.Font(None, round(0.5 * self._font_size)).
                     render(f'goal: ${self._map_conditions['win_count']}', True, (0, 0, 0)))
        goal_text_rect = goal_text.get_rect(center=(self.MONITOR_W - 100, 100))
        alpha_lvl = 255

        clock = pg.time.Clock()
        prev_hit = pg.time.get_ticks()
        store_tick = pg.time.get_ticks()
        store_frame = 0
        self.store_rect = pg.Rect(0, 0, 420, 480)
        self.real_fps = 0
        self.t = time.time()

        debug = False
        is_win = False
        self._main_run = True
        self._to_quit = False
        while self._main_run:
            clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_menu(store_frame)

                elif event.type == pg.KEYDOWN and event.key == pg.K_F5:
                    debug = not debug

                elif event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                    self.inventory()

                elif check_distance(self._hero.rect.center, self.store_rect.center, 400) and \
                        event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    self.store()

                if event.type == pg.QUIT:
                    self._main_run = False
                    self.terminate()

                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and is_win:
                    self._main_run = False
                    self.win_page(store_frame, start_money, lvl_name)

            self._main_screen.blit(self._field, (0, 0))
            for sprite in self._borders:
                self._main_screen.blit(sprite.image, sprite.rect.topleft)
            if pg.time.get_ticks() - store_tick > 400:
                store_frame += 1
                store_tick = pg.time.get_ticks()
            self._camera_group.custom_draw(self._hero, self._main_screen, self._counter,
                                           (self.STORE_ANIM[store_frame % 4], self.store_rect))

            offset = self._camera_group.get_offset(self._hero)
            for chest in self._chests:
                if check_distance(self._hero.rect.center, chest.rect.center, 120) and not chest.is_open:
                    offset_pos = chest.rect.topleft - offset
                    show_hint(self, (int(offset_pos.x) + (chest.rect.w >> 1),
                                     int(offset_pos.y) - 50), self._main_screen)
                    chest.open_chest()

            if check_distance(self._hero.rect.center, self.store_rect.center, 400):
                offset_pos = self.store_rect.center - offset
                show_hint(self, (int(offset_pos.x), int(offset_pos.y)), self._main_screen)

            for obstacle in self._breakable:
                obstacle: SimpleObject

                obstacle_offset = obstacle.rect.topleft - offset
                if (check_distance(self._hero.rect.center, obstacle.rect.center, 120)
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

            if self._counter.get_value() - start_money >= self._map_conditions['win_count']:
                is_win = True
                if alpha_lvl >= 0:
                    alpha_lvl = self.show_win_text(end_text_upper, end_text_lower, alpha_lvl)

            ui.draw(self._main_screen)
            ui_sprites.draw(self._main_screen)
            self._main_screen.blit(goal_text, goal_text_rect)
            if debug:
                show_coords(self._hero, self._main_screen)
                show_mouse_coords(pg.mouse.get_pos(), self._main_screen)
                show_fps(self, self._main_screen)

            pg.display.update()

        if self._to_quit:
            self.terminate()

    def win_page(self, store_frame: int, start_score: int, lvl_name: str) -> None:
        win_surf = pg.Surface((self.MONITOR_W * 0.4, self.MONITOR_H * 0.6))
        win_surf.set_alpha(128)
        win_rect = win_surf.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))

        font = pg.font.Font(None, self._font_size * 2)
        font2 = pg.font.Font(None, round(self._font_size * 1.5))
        win_text = font.render('YOU WIN!', True, (255, 255, 255))
        win_text_rect = win_text.get_rect(center=(win_rect.centerx, win_rect.top + win_rect.h * 0.1))
        result_text = font2.render(f'Your result: {self._counter.get_value() - start_score}$',
                                   True, (255, 255, 255))
        result_text_rect = result_text.get_rect(center=win_rect.center)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    run = False
                    self.save_changes(lvl_name)
                    self.select_level()

            self._camera_group.custom_draw(self._hero, self._main_screen, self._counter,
                                           (self.STORE_ANIM[store_frame % 4], self.store_rect), True)

            self._main_screen.blit(win_surf, win_rect)
            self._main_screen.blit(win_text, win_text_rect)
            self._main_screen.blit(result_text, result_text_rect)

            pg.display.update()

    def store(self) -> None:
        store_surf = pg.Surface((self.MONITOR_W, self.MONITOR_H))
        store_surf.fill(self.BACKGROUND)

        font = pg.font.Font(None, self._font_size * 3)
        count_font = pg.font.Font(None, round(self._font_scale * 0.5))
        sub_font = pg.font.Font(None, self._font_size * 2)

        text = font.render('Store', True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H * 0.05))
        store_surf.blit(text, text_rect)
        text = sub_font.render('Sell', True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.MONITOR_W * 0.74, self.MONITOR_H * 0.12))
        store_surf.blit(text, text_rect)
        text = sub_font.render('Buy', True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.MONITOR_W * 0.26, self.MONITOR_H * 0.12))
        store_surf.blit(text, text_rect)

        pg.draw.line(store_surf, (0, 0, 0), (self.MONITOR_W >> 1, text_rect.bottom + 10),
                     (self.MONITOR_W >> 1, self.MONITOR_H), width=4)

        one_piece_w = ((self.MONITOR_W >> 1) / 3) - 50
        one_piece_h = one_piece_w
        cells = []

        # Инвентарь игрока
        for row in range(len(self._inventory.items)):
            for col in range(len(self._inventory.items[0])):
                cell = self._inventory.items[col][row]
                rect = pg.rect.Rect(self.MONITOR_W * 0.5 + row * (one_piece_w + 20) + 25,
                                    self.MONITOR_H * 0.18 + col * (one_piece_h + 20),
                                    one_piece_w, one_piece_h)
                cell_obj = Cell(store_surf, rect)
                if cell:
                    item: Loot = cell[1]
                    image = scale_with_colorkey(item.ITEMS[item.loot_type], (one_piece_w // 4, one_piece_h // 4))
                    cell_obj.change_item(self, cell, count_font, image, True)

                cells.append(cell_obj)

        run = True
        while run:
            mouse_pos = pg.mouse.get_pos()
            hover_cell = False
            for cell in cells:
                if cell.rect.collidepoint(*mouse_pos):
                    hover_cell = cell
                    break

            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    run = False

                if hover_cell:
                    if (event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT
                          and hover_cell.content is not None):
                        self._counter.change(self._counter.get_value() + hover_cell.cost)
                        hover_cell.delete_content(self._inventory)

            self._main_screen.blit(store_surf, (0, 0))

            self._counter.draw(self._main_screen)

            pg.display.update()

    def inventory(self) -> None:
        inventory_surf = pg.Surface((self.MONITOR_W * 0.4, self.MONITOR_H * 0.5))
        inventory_rect = inventory_surf.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H >> 1))
        inventory_surf.fill('#739db2')
        inventory_surf.blit(pg.font.Font(None, self._font_size).
                            render('Inventory', True, (0, 0, 0)),
                            (inventory_rect.w * 0.4, inventory_rect.h * 0.05))

        one_piece_w = inventory_rect.w >> 2
        one_piece_h = inventory_rect.h >> 2
        count_font = pg.font.Font(None, round(self._font_scale * 0.5))
        for row in range(len(self._inventory.items)):
            for col in range(len(self._inventory.items[0])):
                cell = self._inventory.items[col][row]
                rect = pg.rect.Rect(inventory_rect.w * 0.1 + row * (one_piece_w + 20),
                                    inventory_rect.h * 0.15 + col * (one_piece_h + 20),
                                    one_piece_w, one_piece_h)
                cell_obj = Cell(inventory_surf, rect)
                if cell:
                    item: Loot = cell[1]
                    image = scale_with_colorkey(item.ITEMS[item.loot_type], (one_piece_w >> 2, one_piece_h >> 2))
                    cell_obj.change_item(self, cell, count_font, image)

        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and (event.key == pg.K_TAB or event.key == pg.K_ESCAPE):
                    run = False
            self._main_screen.blit(inventory_surf, inventory_rect)
            pg.display.update()

    def save_changes(self, lvl_name: str) -> None:
        con = sqlite3.connect('data/saves/saves.sqlite')
        cur = con.cursor()

        cur.execute(f"""UPDATE hero_stats SET hp = {self._hero._max_hp},
         speed = {self._hero.SPEED}
            WHERE save_id == {self._selected_save_file}""")
        if cur.execute(f"""SELECT [{lvl_name}] FROM levels
                    WHERE save_id == {self._selected_save_file}""").fetchone()[0] == 0:
            cur.execute(f"""UPDATE hero_stats SET money = {self._counter.get_value()}
            WHERE save_id == {self._selected_save_file}""")
            cur.execute(f"""UPDATE levels SET [{lvl_name}] = '1' 
                WHERE save_id == {self._selected_save_file}""")
        con.commit()

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
                        Crate(self, x, y, self._breakable, self._all_sprites)
                    else:
                        SimpleObject(self, int(data[y][x]), x, y, self._breakable, self._all_sprites)
        return lvl_map

    def calc_fps(self) -> str:
        cur_t = time.time()
        cur_fps = False
        if cur_t != self.t:
            cur_fps = 1 / (cur_t - self.t)
            if self.real_fps == 0:
                self.real_fps = cur_fps
            else:
                self.real_fps = 0.8 * self.real_fps + 0.2 * cur_fps
        self.t = cur_t
        if cur_fps:
            return str(round(cur_fps))

    def show_win_text(self, upper_text: pg.Surface, lower_text: pg.Surface, alpha: int) -> int:
        upper_text_rect = upper_text.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H * 0.05))
        lower_text_rect = lower_text.get_rect(center=(self.MONITOR_W >> 1, self.MONITOR_H * 0.1))
        upper_text.set_alpha(alpha)
        lower_text.set_alpha(alpha)
        alpha -= 1

        self._main_screen.blit(upper_text, upper_text_rect)
        self._main_screen.blit(lower_text, lower_text_rect)
        return alpha

    def terminate(self) -> None:
        settings = pd.read_csv('data/saves/settings.csv', delimiter=';')
        settings.at[0, 'value'] = self._interface_volume
        settings.at[1, 'value'] = self._effects_volume
        settings.at[2, 'value'] = self._music_volume
        settings.to_csv('data/saves/settings.csv', index=False, sep=';')

        pg.quit()
        sys.exit(1)


if __name__ == '__main__':
    game = Game()
    game.main()
