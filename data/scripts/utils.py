import pygame as pg


def scale_with_colorkey(image: pg.Surface, scale: tuple[int, int],
                        colorkey: tuple[int, int, int] or str) -> pg.Surface:
    image = pg.transform.scale(image, scale)
    image.set_colorkey(colorkey)

    return image


def load_with_colorkey(image_path: str, colorkey: tuple[int, int, int] or str) -> pg.Surface:
    image = pg.image.load(image_path).convert_alpha()
    image.set_colorkey(colorkey)

    return image
