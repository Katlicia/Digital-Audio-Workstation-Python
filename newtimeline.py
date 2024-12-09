import pygame
from config import *

class Timeline:
    def __init__(self) -> None:
        self.offset_x = 0
        self.track_height = 57
        self.unit_width = 50  # 1 saniye için piksel genişliği
        self.track_count = 11
        self.dynamic_length = 100
        self.min_zoom = 40
        self.max_zoom = 400

    def handleScroll(self, event):
        # Eğer Alt tuşu basılıysa zoom işlemi yapılacak
        if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
            if event.type == pygame.MOUSEWHEEL:
                zoom_change = 10  # Zoom değişim miktarı
                if event.y == -1 and self.unit_width - zoom_change >= self.min_zoom:  # Fare tekerleği yukarı (zoom in)
                    self.unit_width -= zoom_change
                elif event.y == 1 and self.unit_width + zoom_change <= self.max_zoom:  # Fare tekerleği aşağı (zoom out)
                    self.unit_width += zoom_change
        else:
            # Kaydırma işlemi, Alt tuşu basılı değilse
            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:  # Fare tekerleği yukarı
                    self.offset_x += 100
                elif event.y == -1:  # Fare tekerleği aşağı
                    self.offset_x -= 100
                    if self.offset_x < 0:  # Geriye kaydırmayı engelle
                        self.offset_x = 0 

    def drawTimeline(self, win, x, y, width, height, tracks, sample_rate):
        """
        Timeline'ı ve track'leri belirtilen sınırlar içinde çizer.
        """
        total_length_px = self.dynamic_length * self.unit_width
        self.autoExtendTimeline(win)  # Genişletme kontrolü
        
        # Zaman çizelgesi yüzeyi oluşturuluyor
        timeline_surface = pygame.Surface((width, height))
        timeline_surface.fill("grey")  # Arka plan rengi

        font = pygame.font.SysFont("Arial", 20)        
        
        # Track'leri zaman çizelgesine ekle
        for i, track in enumerate(tracks):
            track_y = 26 + i * (self.track_height)  # Track'in y pozisyonu
            if track is not None:
                # Track süresi ve genişliği
                track_duration = len(track) / sample_rate
                track_width = int(track_duration * self.unit_width)

                # Track başlangıç ve bitiş pozisyonları
                track_x_start = - self.offset_x
                track_x_end = track_x_start + track_width

                # Track kutusunu çiz
                pygame.draw.rect(
                    timeline_surface, (100, 149, 237), 
                    (track_x_start + 1, track_y+1, track_width, self.track_height)
                )
                
            # Her track'in altına yatay çizgi ekle
            if i < len(tracks) - 1:  # Son track için çizgi çizme
                line_y = track_y + self.track_height
                pygame.draw.line(timeline_surface, dark_grey, (0, line_y), (width, line_y), 1)

        # Zaman çizelgesi sütunlarını çiz
        for col in range(0, total_length_px, self.unit_width):
            pos_x = col - self.offset_x
            if 0 <= pos_x <= width:
                pygame.draw.line(timeline_surface, dark_grey, (pos_x, 0), (pos_x, height))  # Dikey çizgi
                pygame.draw.line(timeline_surface, dark_grey, (0, 26), (pos_x + 300, 26)) 
                # Sütun üzerindeki zamanı yaz
                text = font.render(str(col // self.unit_width + 1), True, dark_grey)
                text_rect = text.get_rect(topleft=(pos_x+1, 5))
                timeline_surface.blit(text, text_rect)

        # Zaman çizelgesini ekrana çiz
        win.blit(timeline_surface, (x, y))

    def autoExtendTimeline(self, win):
        """
        Kullanıcı sona yaklaştığında sütun uzunluğunu artırır.
        """
        screen_width = win.get_width()
        visible_end = self.dynamic_length * self.unit_width - self.offset_x
        if visible_end < screen_width + self.unit_width * 10:
            self.dynamic_length += 10

