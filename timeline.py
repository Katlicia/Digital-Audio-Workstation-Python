import pygame
from config import *

class Timeline:
    def __init__(self) -> None:
        self.offset_x = 0
        self.track_height = 50
        self.unit_width = 50
        self.track_count = 11
        self.dynamic_length = 100

    def handleScroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:  # Fare tekerleği yukarı
                self.offset_x += 100
            elif event.y == -1:  # Fare tekerleği aşağı
                self.offset_x -= 100
                if self.offset_x < 0:  # Geriye kaydırmayı engelle
                    self.offset_x = 0

    def drawTimeline(self, win, x, y, width, height):
        """
        Timeline'ı belirtilen sınırlar içinde çizer.
        """
        total_length_px = self.dynamic_length * self.unit_width
        self.autoExtendTimeline(win)  # Genişletme kontrolü

        # Sütun çizimi
        for col in range(0, total_length_px, self.unit_width):
            pos_x = col - self.offset_x + x
            if x <= pos_x <= x + width:
                pygame.draw.line(win, dark_grey, (pos_x, y), (pos_x, y + height))
                font = pygame.font.Font(None, 24)
                text = font.render(str(col // self.unit_width + 1), True, dark_grey)  # 1'den başla
                win.blit(text, (pos_x + 2, y + 2))

    def autoExtendTimeline(self, win):
        """
        Kullanıcı sona yaklaştığında sütun uzunluğunu artırır.
        """
        screen_width = win.get_width()
        visible_end = self.dynamic_length * self.unit_width - self.offset_x
        if visible_end < screen_width + self.unit_width * 10:
            self.dynamic_length += 10
