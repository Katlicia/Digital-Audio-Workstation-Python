import pygame
from config import *

class Timeline:
    def __init__(self) -> None:
        self.offset_x = 0
        self.offset_y = 0
        self.track_height = 50
        self.unit_width = 50
        self.track_count = 11
        self.dynamic_length = 100

    def handleScroll(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.offset_x += 100  # Sağa kaydır
            elif event.key == pygame.K_LEFT:
                self.offset_x -= 100  # Sola kaydır
                if self.offset_x < 0:  # Geriye kaydırmayı engelle
                    self.offset_x = 0
        elif event.type == pygame.MOUSEWHEEL:
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

    def drawTracks(self, win, x, y, width, height):
        """
        11 adet track'i belirtilen sınırlar içinde çizer.
        """
        for i in range(self.track_count):
            track_y = y + i * self.track_height - self.offset_y  # Her satırın başlangıç Y pozisyonu
            if y <= track_y <= y + height - self.track_height:  # Çizim sınırları içinde mi?
                pygame.draw.line(win, (150, 150, 150), (x, track_y), (x + width, track_y))  # Satır çizgisi

                # Satır numarasını yazdır
                font = pygame.font.Font(None, 24)
                text = font.render(f"{i + 1}", True, (255, 255, 255))
                win.blit(text, (x - 30, track_y + 15))  # Satır numarasını çiz
    
    def autoExtendTimeline(self, win):
        """
        Kullanıcı sona yaklaştığında sütun uzunluğunu artırır.
        """
        screen_width = win.get_width()
        visible_end = self.dynamic_length * self.unit_width - self.offset_x
        if visible_end < screen_width + self.unit_width * 10:
            self.dynamic_length += 10
