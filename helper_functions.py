import pygame

def draw_recording_list(win, recordings):
    font = pygame.font.Font(None, 36)
    y = 50
    for name in recordings.keys():
        text_surface = font.render(name, True, "black")
        win.blit(text_surface, (50, y))
        y += 40