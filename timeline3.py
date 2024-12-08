import pygame
# Renk tanımları
dark_grey = (50, 50, 50)
light_grey = (200, 200, 200)
white = (255, 255, 255)
red = (255, 0, 0)

# Timeline sınıfı
class Timeline:
    def __init__(self):
        self.offset_x = 0
        self.track_height = 50
        self.unit_width = 50
        self.track_count = 10
        self.dynamic_length = 100
        self.cursor_x = 0  # İmleç pozisyonu
        self.tracks = {}

    def drawTimeline(self, win, x, y, width, height):
        """
        Timeline'ı ve grid çizgilerini çizer.
        """
        total_length_px = self.dynamic_length * self.unit_width
        self.autoExtendTimeline(win)

        # Track'lerin arka planını çiz
        for row in range(self.track_count):
            track_y = y + row * self.track_height
            color = light_grey if row % 2 == 0 else white
            pygame.draw.rect(win, color, (x + self.unit_width * 2, track_y, width, self.track_height))

            # Track başlıklarını ekle
            font = pygame.font.Font(None, 24)
            text = font.render(f"Track {row + 1}", True, dark_grey)
            win.blit(text, (x + 5, track_y + self.track_height // 2 - 12))  # Yatay ve dikey hizalama

        # Sütun çizgileri
        for col in range(0, total_length_px, self.unit_width):
            pos_x = col - self.offset_x + x + self.unit_width * 2  # Sol ofseti ekledik
            if x + self.unit_width * 2 <= pos_x <= x + width + self.unit_width * 2:
                pygame.draw.line(win, dark_grey, (pos_x, y), (pos_x, y + height))

                # Sütun numaralarını çiz
                font = pygame.font.Font(None, 24)
                text = font.render(str(col // self.unit_width + 1), True, dark_grey)
                win.blit(text, (pos_x + 2, y - 20))  # Sütun numaraları üstte gösterilir.

        self.drawTrackLines(win, x, y, width)

    def drawCursor(self, win, x, y, height):
        """
        İmleci (cursor) çizer.
        """
        pos_x = self.cursor_x - self.offset_x + x + self.unit_width * 2
        if pos_x >= x + self.unit_width * 2:
            pygame.draw.line(win, red, (pos_x, y), (pos_x, y + height), 2)


    def autoExtendTimeline(self, win):
        """
        Kullanıcı sona yaklaştığında timeline'ı genişletir.
        """
        screen_width = win.get_width()
        visible_end = self.dynamic_length * self.unit_width - self.offset_x + 100
        if visible_end < screen_width + self.unit_width * 10:
            self.dynamic_length += 10

    def handleScroll(self, event):
        """
        Fare tekerleğiyle kaydırmayı yönetir.
        """
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:  # Fare tekerleği yukarı
                self.offset_x += 100
            elif event.y == -1:  # Fare tekerleği aşağı
                self.offset_x -= 100
                if self.offset_x < 0:  # Geriye kaydırmayı engelle
                    self.offset_x = 0

    def handleKeyboard(self):
        """
        Klavye ile imleci hareket ettirme ve ekran kaydırma.
        """
        keys = pygame.key.get_pressed()
        cursor_speed = 10  # İmlecin hareket hızı
        screen_width = pygame.display.get_surface().get_width()

        if keys[pygame.K_RIGHT]:
            self.cursor_x += cursor_speed

            # Eğer cursor görünür ekranın sonuna yaklaşıyorsa ekranı kaydır
            if self.cursor_x > self.offset_x + screen_width - 300:  # Sağ kenara yaklaşma
                self.offset_x += cursor_speed

        if keys[pygame.K_LEFT]:
            self.cursor_x -= cursor_speed

            # Eğer cursor görünür ekranın başına yaklaşıyorsa ekranı geri kaydır
            if self.cursor_x < self.offset_x + 50 and self.offset_x > 0:
                self.offset_x -= cursor_speed

            # Cursor sıfırın altına inmesin
            if self.cursor_x < 0:
                self.cursor_x = 0

    def addTrack(self, track_id, width):
        """
        Yeni bir track'i zaman çizelgesine ekler.
        Args:
            track_id (int): Track ID'si.
            width (float): Track'in zaman çizelgesindeki genişliği (piksel).
        """
        self.tracks[track_id] = width

    def drawTracks(self, win, x_start, y_start):
        """
        Zaman çizelgesindeki track'leri çizer.
        Args:
            win: Pencere yüzeyi.
            x_start: Çizimin başlangıç X pozisyonu.
            y_start: Çizimin başlangıç Y pozisyonu.
        """
        self.autoExtendTimeline(win)
        track_y_offset = 50  # Track'ler arası mesafe
        for track_id, width in self.tracks.items():
            # Her track'in pozisyonu
            y_pos = y_start + track_id * track_y_offset
            pygame.draw.rect(win, (0, 255, 0), (x_start + self.unit_width * 2 + 1, y_pos+1, width, self.track_height-1))

    def drawTrackLines(self, win, x, y, width):
        """
        Track'lerin arasına yatay çizgiler çizer.
        """
        line_color = dark_grey
        for row in range(self.track_count + 1):  # Track sayısına göre çizgiler
            line_y = y + row * self.track_height
            pygame.draw.line(win, line_color, (x, line_y), (x + width + self.unit_width * 2, line_y), 1)
