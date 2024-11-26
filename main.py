import pygame
from button import *
from config import *
from audio import *

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

clock = pygame.time.Clock()
running = True

recordButton = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 100, 100, win, "Record")
stopButton = Button(SCREEN_WIDTH / 2 + 200, SCREEN_HEIGHT / 2, 100, 100, win, "Stop")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if recordButton.isClicked(pos):
                start_recording()
            if stopButton.isClicked(pos):
                stop_recording()

    win.fill("white")
    
    recordButton.draw()
    stopButton.draw()


    x, y = win.get_size()

    
    pygame.display.update()
    
pygame.quit()
