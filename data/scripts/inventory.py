import pygame as pg


class Inventory:
    def __init__(self, target):
        self.items = [[[], [], []],
                       [[], [], []],
                       [[], [], []]]
        target._inventory = self
