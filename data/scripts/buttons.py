import pygame as pg
import os

pg.init()


class DefaultButton:
    def __init__(self, pos: tuple[int, int], width: int, height: int,
                 button_img: str, hover_image: str = None,
                 sound: str = None,
                 text: str = '', text_color: tuple[int, int, int] or str = (255, 255, 255), text_size: int = 36) -> None:
        self._x, self._y = pos
        self._width = width
        self._height = height
        self._text = text
        self._text_color = text_color
        self._sound = None

        self._font = pg.font.Font(None, text_size)

        image_path = os.path.join('data', 'images', 'buttons', button_img)
        try:
            self._image = pg.image.load(image_path)
        except FileNotFoundError:
            raise FileNotFoundError('Button image not found')
        self._image = pg.transform.scale(self._image, (width, height))
        self._hover_image = self._image

        if hover_image is not None:
            hover_path = os.path.join('data', 'images', 'buttons', 'hover', hover_image)
            try:
                self._hover_image = pg.image.load(hover_path)
            except FileNotFoundError:
                raise FileNotFoundError('Hover image not found')
            self._hover_image = pg.transform.scale(self._hover_image, (width, height))

        self._rect = self._image.get_rect(center=pos)

        if sound is not None:
            sound_path = os.path.join('data', 'sounds', 'buttons', sound)
            try:
                self._sound = pg.mixer.Sound(sound_path)
            except Exception:
                raise Exception('Sound file not found')

        self._is_hovered = False

    def draw(self, screen: pg.Surface) -> None:
        current_image = self._hover_image if self._is_hovered else self._image
        screen.blit(current_image, self._rect.topleft)

        text_surf = self._font.render(self._text, True, self._text_color)
        text_rect = text_surf.get_rect(center=self._rect.center)
        screen.blit(text_surf, text_rect)

    def hover_check(self, mouse_pos: tuple[int, int]) -> None:
        self._is_hovered = self._rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self._is_hovered:
            if self._sound:
                self._sound.play()
            pg.event.post(pg.event.Event(pg.USEREVENT, button=self))
