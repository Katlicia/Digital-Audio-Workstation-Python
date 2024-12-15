import pygame
class DropdownMenu:
    def __init__(self, x, y, width, height, options, win, font_size=18, bg_color=(99, 99, 99), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = pygame.font.SysFont("Arial", font_size)
        self.bg_color = bg_color
        self.text_color = text_color
        self.win = win
        self.visible = False  # Menü başlangıçta gizli
        self.selected_option = None

    def draw(self):
        # Ana düğmeyi çiz
        pygame.draw.rect(self.win, self.bg_color, self.rect)
        placeholder = self.font.render("Select", True, self.text_color)
        self.win.blit(placeholder, placeholder.get_rect(center=self.rect.center))

        # Dropdown seçenekleri çiz
        if self.visible:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(self.win, self.bg_color, option_rect)
                text = self.font.render(option, True, self.text_color)
                self.win.blit(text, text.get_rect(center=option_rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Sol tıklama
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                self.visible = not self.visible  # Tıklanınca menüyü aç/kapat
            elif self.visible:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = option  # Seçimi güncelle
                        self.visible = False
                        break
                else:
                    self.visible = False  # Dropdown dışında bir yere tıklandıysa menüyü kapat