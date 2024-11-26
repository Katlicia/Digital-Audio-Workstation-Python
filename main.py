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

playButton = Button(100, 100, 100, 100, win, "Play")
exportButton = Button(300, 100, 100, 100, win, "Export")

def draw_recording_list(win, recordings):
    font = pygame.font.Font(None, 36)
    y = 50
    for name in recordings.keys():
        text_surface = font.render(name, True, "black")
        win.blit(text_surface, (50, y))
        y += 40


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if recordButton.isClicked(pos):
                start_recording()
            if stopButton.isClicked(pos):
                stop_recording("sound1")
            if playButton.isClicked(pos):
                play_recording("sound1")
            if exportButton.isClicked(pos):
                export_recording("sound1", "sound1.wav")


    win.fill("white")
    
    recordButton.draw()
    stopButton.draw()
    playButton.draw()
    exportButton.draw()
    draw_recording_list(win, recordings)

    x, y = win.get_size()

    
    pygame.display.update()
    
pygame.quit()
