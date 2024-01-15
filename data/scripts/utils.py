import math

import pygame as pg

from data.scripts.UI import DefaultButton


def scale_with_colorkey(image: pg.Surface, scale: tuple[int, int],
                        colorkey: tuple[int, int, int] or str = (0, 0, 0)) -> pg.Surface:
    image = pg.transform.scale(image, scale)
    image.set_colorkey(colorkey)

    return image


def load_with_colorkey(image_path: str, colorkey: tuple[int, int, int] or str = (0, 0, 0)) -> pg.Surface:
    image = pg.image.load(image_path).convert_alpha()
    image.set_colorkey(colorkey)

    return image


def show_coords(player, screen: pg.Surface, coords: tuple[int, int] = (30, 150)) -> None:
    player_coords = player.rect.center
    font = pg.font.Font(None, 30)
    font_surf = font.render(f'Player position: {player_coords}', True, 'green')
    screen.blit(font_surf, coords)


def show_mouse_coords(mouse_coords: tuple[int, int], screen: pg.Surface, coords: tuple[int, int] = (30, 100)) -> None:
    font = pg.font.Font(None, 30)
    font_surf = font.render(f'Mouse coords: {mouse_coords}', True, 'green')
    screen.blit(font_surf, coords)


def show_fps(game: 'main.Game', screen: pg.Surface, coords: tuple[int, int] = (30, 200)):
    font = pg.font.Font(None, 30)
    fps_text = font.render(f'fps: {game.calc_fps()}', True, (0, 255, 0))
    screen.fill('#818181', (0, 0, fps_text.get_width() + 20, fps_text.get_height()))

    screen.blit(fps_text, coords)


def create_bg(size: tuple[int, int], image: pg.Surface) -> pg.Surface:
    width, height = size
    surface = pg.Surface(size)
    surface_rect = surface.get_rect()
    for row in range(0, width, 100):
        for col in range(0, height, 100):
            surface.blit(image, (surface_rect.left + row, surface_rect.top + col))

    return surface


def check_distance(obj_1_center: tuple[int, int], obj_2_center: tuple[int, int], max_distance: int) -> bool:
    x1, y1 = obj_1_center
    x2, y2 = obj_2_center
    if math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2) <= max_distance:
        return True
    return False


def show_hint(game: 'main.Game', coords: tuple[int, int], screen: pg.Surface) -> None:
    hint = DefaultButton(coords, 150, 100, game.HINT_BUTTON,
                         text='space', text_size=30)
    hint.draw(screen)
