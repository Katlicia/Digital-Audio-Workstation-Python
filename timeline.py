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
        self.cursor_position = 0  # Cursor'un piksel olarak pozisyonu
        self.is_playing = False  # Cursor hareketi aktif mi?

    def handleScroll(self, event):
        # Eğer Alt tuşu basılıysa zoom işlemi yapılacak
        if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
            if event.type == pygame.MOUSEWHEEL:
                zoom_change = 10  # Zoom değişim miktarı
                cursor_time = self.cursor_position / self.unit_width  # Zoom öncesi cursor zamanı
                if event.y == -1 and self.unit_width - zoom_change >= self.min_zoom:  # Fare tekerleği yukarı (zoom in)
                    self.unit_width -= zoom_change
                elif event.y == 1 and self.unit_width + zoom_change <= self.max_zoom:  # Fare tekerleği aşağı (zoom out)
                    self.unit_width += zoom_change
                self.cursor_position = cursor_time * self.unit_width  # Zoom sonrası cursor pozisyonunu koru
        else:
            # Kaydırma işlemi, Alt tuşu basılı değilse
            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:  # Fare tekerleği yukarı
                    self.offset_x += 100
                elif event.y == -1:  # Fare tekerleği aşağı
                    self.offset_x -= 100
                    if self.offset_x < 0:  # Geriye kaydırmayı engelle
                        self.offset_x = 0 

    def handleClick(self, event, timeline_x, timeline_y, timeline_width, timeline_height):
        """
        Zaman çizelgesinde bir tıklama algılandığında, cursor'u tıklanan yere taşır.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Sol tıklama
            mouse_x, mouse_y = event.pos
            if timeline_x <= mouse_x <= timeline_x + timeline_width and timeline_y <= mouse_y <= timeline_y + timeline_height:
                # Tıklamanın zaman çizelgesi alanında olduğundan emin ol
                self.cursor_position = mouse_x + self.offset_x - timeline_x

    def drawTimeline(self, win, x, y, width, height, tracks, sample_rate, color1, color2):
        """
        Timeline'ı ve track'leri belirtilen sınırlar içinde çizer.
        """
        total_length_px = self.dynamic_length * self.unit_width
        self.autoExtendTimeline(win)  # Genişletme kontrolü
        
        # Zaman çizelgesi yüzeyi oluşturuluyor
        timeline_surface = pygame.Surface((width, height))
        timeline_surface.fill(color1)  # Arka plan rengi

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
                pygame.draw.line(timeline_surface, color2, (0, line_y), (width, line_y), 1)

        # Zaman çizelgesi sütunlarını çiz
        for col in range(0, int(total_length_px), int(self.unit_width)):
            pos_x = col - self.offset_x
            if 0 <= pos_x <= width:
                pygame.draw.line(timeline_surface, color2, (pos_x, 0), (pos_x, height))  # Dikey çizgi
                pygame.draw.line(timeline_surface, color2, (0, 26), (pos_x + 300, 26)) 
                # Sütun üzerindeki zamanı yaz
                text = font.render(str(col // self.unit_width + 1), True, color2)
                text_rect = text.get_rect(topleft=(pos_x+1, 5))
                timeline_surface.blit(text, text_rect)

        # Cursor'u çiz
        self.draw_cursor(timeline_surface, width, height, color="red")

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

    def draw_cursor(self, surface, width, height, color="red"):
        """
        Zaman çizelgesindeki cursor'u çizer.
        """
        cursor_x = self.cursor_position - self.offset_x
        if 0 <= cursor_x <= width:
            pygame.draw.line(surface, color, (cursor_x, 0), (cursor_x, height), 2)

    def update_cursor(self, delta_time):
        """
        Cursor'un pozisyonunu günceller.
        delta_time: Bir önceki çerçeveden bu yana geçen süre.
        """
        if self.is_playing:
            self.cursor_position += delta_time * self.unit_width  # Zamanla doğru orantılı hareket
            self.cursor_position %= (self.dynamic_length * self.unit_width)  # Döngüel hareket için
