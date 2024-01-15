import pygame as pg


class Inventory:
    def __init__(self, target):
        self.items = [[[], [], []],
                      [[], [], []],
                      [[], [], []]]
        target._inventory = self


class Cell:
    BACKGROUND = pg.Color('#818181')

    def __init__(self, screen: pg.Surface, rect: pg.rect.Rect) -> None:
        self.rect = pg.draw.rect(screen, (0, 0, 0), rect, 2, 20)
        self.screen = screen
        self.image: pg.Surface | None = None
        self.content: list | None = None
        self.cost: int | None = None

    def change_item(self, game: 'main.Game', cell_content: list, font: pg.font.Font, image: pg.Surface,
                    price: bool = False) -> None:
        self.content = cell_content
        self.image = image

        self.cost = game.PRICES[self.content[0]] * (len(self.content) - 1)
        count_surf = font.render(str(len(self.content) - 1), True, (0, 0, 0))

        self.screen.blit(image, (self.rect.centerx - (image.get_width() >> 1),
                                 self.rect.centery - (image.get_height() >> 1)))
        self.screen.blit(count_surf, (self.rect.right - count_surf.get_width() * 2,
                                      self.rect.bottom - count_surf.get_height()))
        if price:
            sell_price_surf = font.render(f'$ {str(self.cost)}', True, (0, 0, 0))
            sell_price_rect = sell_price_surf.get_rect(center=(self.rect.left + game.MONITOR_H * 0.02,
                                                               self.rect.top + game.MONITOR_H * 0.02))
            self.screen.blit(sell_price_surf, sell_price_rect)

    def delete_content(self, inventory: Inventory) -> None:
        for row in inventory.items:
            for item in row:
                if item == self.content:
                    item.clear()

        self.content = None
        self.cost = None
        self.image = None

        bg_surf = pg.Surface(self.rect.size)
        bg_surf.fill(self.BACKGROUND)
        self.screen.blit(bg_surf, self.rect.topleft)
        self.rect = pg.draw.rect(self.screen, (0, 0, 0), self.rect, 2, 20)
