import pygame

class ImageButton:
    def __init__(self, x, y, image, win):
        self.coordinates = x, y
        self.image = pygame.image.load(image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.win = win
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw(self):
        self.win.blit(self.image, self.coordinates)
    
    def isClicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def setImage(self, image):
        self.image = pygame.image.load(image)

class Button:
    def __init__(self, x, y, width, height, win, passive_color, active_color, text_color, text=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.win = win
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size)
        self.passive_color = passive_color
        self.active_color = active_color
        self.text_color = text_color
        self.color = self.passive_color
        self.active = False

    def draw(self):
        pygame.draw.rect(self.win, self.passive_color, self.rect)
        if self.text != None:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center = self.rect.center)
            self.win.blit(text_surface, text_rect)
    
    def drawLeft(self):
        pygame.draw.rect(self.win, self.passive_color, self.rect)
        if self.text != None:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(topleft = self.rect.topleft)
            self.win.blit(text_surface, text_rect)

    def isClicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = self.active_color
            return self.rect.collidepoint(mouse_pos)
        else:
            self.color = self.passive_color
            return self.rect.collidepoint(mouse_pos)


