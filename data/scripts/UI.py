import pygame as pg
import os
pg.init()


class ButtonGroup:
    def __init__(self) -> None:
        self.button_list = []

    def add(self, button) -> None:
        self.button_list.append(button)

    def draw(self, screen: pg.Surface) -> None:
        for button in self.button_list:
            button.draw(screen)

    def handle(self, event) -> None:
        for button in self.button_list:
            button.handle_event(event)

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        for button in self.button_list:
            button.hover_check(mouse_pos)


class DefaultButton:
    STANDARD_SOUND = pg.mixer.Sound('data/sounds/UI/click.wav')

    def __init__(self, pos: tuple[int or float, int or float], width: int or float, height: int or float,
                 button_img: pg.Surface, hover_image: pg.Surface = None,
                 sound: str = None,
                 text: str = '', text_color: tuple[int, int, int] or str = (255, 255, 255),
                 text_size: int = 36,
                 group: ButtonGroup = None) -> None:
        self._text = text
        self._text_color = text_color
        self._sound = None

        self._font = pg.font.Font(None, text_size)

        self._image = pg.transform.scale(button_img, (width, height))
        self._hover_image = self._image
        if hover_image is not None:
            self._hover_image = pg.transform.scale(hover_image, (width, height))

        self._rect = self._image.get_rect(center=pos)

        if sound is not None:
            self._sound = self.STANDARD_SOUND

        self._is_hovered = False

        if group is not None:
            group.add(self)

    def draw(self, screen: pg.Surface) -> None:
        current_image = self._hover_image if self._is_hovered else self._image
        screen.blit(current_image, self._rect.topleft)

        text_surf = self._font.render(self._text, True, self._text_color)
        text_rect = text_surf.get_rect(center=self._rect.center)
        screen.blit(text_surf, text_rect)

    def hover_check(self, mouse_pos: tuple[int, int]) -> None:
        self._is_hovered = self._rect.collidepoint(mouse_pos)

    def handle_event(self, event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self._is_hovered:
            if self._sound:
                self._sound.play()
            pg.event.post(pg.event.Event(pg.USEREVENT, button=self))


class Slider:
    def __init__(self, pos: tuple[int, int], width: int, height: int,
                 slider_color: tuple[int, int, int] or str = (93, 106, 110),
                 change_color: tuple[int, int, int] or str = (66, 194, 237),
                 step: int = 10):
        self._rect = pg.rect.Rect(pos[0], pos[1], width, height)
        self._slider_surf = pg.Surface((self._rect.width - 10, self._rect.height))
        self._slider_surf.fill(slider_color)
        self._change_color = change_color
        self._changed_surf = pg.Surface((self._rect.width, self._rect.height))
        self._changed_surf.fill(self._change_color)

        self._piece = self._rect.width // step
        self.value = step

    def change(self, value: int) -> None:
        self.value = value
        self._changed_surf = pg.Surface((self._piece * self.value, self._rect.height))
        self._changed_surf.fill(self._change_color)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self._slider_surf, self._rect.topleft)
        screen.blit(self._changed_surf, self._rect.topleft)

    def get_value(self) -> int:
        return self.value


class Counter:
    def __init__(self, pos: tuple[int, int], width: int, height: int,
                 number_color: tuple[int, int, int] or str = (0, 0, 0),
                 bg_color: tuple[int, int, int] or str = (0, 0, 0),
                 group: ButtonGroup = None):
        self._rect = pg.rect.Rect(pos[0], pos[1], width, height)
        self._count = 0
        self._font = pg.font.Font(None, 80)
        self._color = number_color
        self._counter_surf = pg.Surface((self._rect.width, self._rect.height))
        self._counter_surf.fill(bg_color)

        self._numbers_surf = self._font.render('$' + str(self._count).ljust(4, '0'),
                                               True, self._color)

        if group is not None:
            group.add(self)

    def change(self, value: int) -> None:
        self._count = value
        self._numbers_surf = self._font.render('$' + str(self._count).ljust(4, '0'),
                                               True, self._color)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self._counter_surf, self._rect.topleft)
        screen.blit(self._numbers_surf, (self._rect.topleft[0] + 20, self._rect.topleft[1]))
