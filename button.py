import pygame

class Button:
    def __init__(self, x, y, image, win, text=None) -> None:
        self.coordinates = x, y
        self.image = image
        self.win = win
        self.text = text
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
    
    def draw(self):
        self.win.blit(self.image, self.coordinates)
    
    def isClicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)