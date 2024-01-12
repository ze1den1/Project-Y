import pygame as pg

pg.init()
pg.mixer.init()


class SoundsList:
    def __init__(self):
        self.sounds = []

    def add(self, sound: pg.mixer.Sound) -> None:
        self.sounds.append(sound)

    def set_volume(self, volume: float) -> None:
        for sound in self.sounds:
            sound.set_volume(volume)
