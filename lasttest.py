import pygame
from button import Button, ImageButton
from config import *
import sounddevice as sd
import numpy as np
from audio_utils import *
from helper_functions import *

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

clock = pygame.time.Clock()
running = True

# Ses seviyesi butonları
volumeUpButton = Button(650, 10, 40, 25, win, "+")
volumeDownButton = Button(700, 10, 40, 25, win, "-")

MenuButtonList = [
    # FileButton
    Button(menu_button_start_pos_x, menu_button_y_pos, menu_button_width, menu_button_height, win, "FILE", menu_button_font_size, grey),
    # EditButton
    Button(menu_button_start_pos_x+menu_button_width, menu_button_y_pos, menu_button_width, menu_button_height, win, "EDIT", menu_button_font_size, grey),
    # SaveButton 
    Button(menu_button_start_pos_x+menu_button_width*2, menu_button_y_pos, menu_button_width, menu_button_height, win, "SAVE", menu_button_font_size, grey),
    # ThemeButton
    Button(menu_button_start_pos_x+menu_button_width*3, menu_button_y_pos, menu_button_width+5, menu_button_height, win, "THEME", menu_button_font_size, grey)
]

recordButton = ImageButton(record_button_x, menu_button_y_pos, "images/record.png", win)
playButton = ImageButton(play_button_x, menu_button_y_pos, "images/play.png", win)
stopButton = ImageButton(stop_button_x, menu_button_y_pos, "images/pause.png", win)
resetButton = ImageButton(reset_button_x, menu_button_y_pos, "images/reset.png", win)

initialize_audio_stream()

while running:
    x, y = win.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        pos = pygame.mouse.get_pos()
        

        if event.type == pygame.MOUSEBUTTONDOWN:
            if recordButton.isClicked(pos):
                if recording:
                    stop_recording()
                    recordButton.setImage("images/record.png")
                else:
                    start_recording()
                    recordButton.setImage("images/recording.png")

            if playButton.isClicked(pos):
                play_selected_track()

            if stopButton.isClicked(pos):
                stop_playing()

            for i in range(len(tracks)):
                y = track_start_y + i * (track_height + track_spacing)
                if y <= pos[1] <= y + track_height:
                    selected_track = i  # Seçili track'i güncelle

            if volumeUpButton.isClicked(pos):
                adjust_volume(0.1)  # %10 artır
            if volumeDownButton.isClicked(pos):
                adjust_volume(-0.1)  # %10 azalt

    win.fill("grey")
    pygame.draw.rect(win, light_blue, pygame.Rect(0, 0, x, 40))

    width = 0
    for MenuButton in MenuButtonList:
        MenuButton.draw()
        MenuButton.isClicked(pos)
        width += MenuButton.width


    recordButton.draw()
    playButton.draw()
    if playButton.isClicked(pos):
        playButton.setImage("images/onplay.png") 
    else:
        playButton.setImage("images/play.png")
    stopButton.draw()
    if stopButton.isClicked(pos):
        stopButton.setImage("images/onpause.png")
    else:
        stopButton.setImage("images/pause.png")
    resetButton.draw()
    if resetButton.isClicked(pos):
        resetButton.setImage("images/onreset.png")
    else:
        resetButton.setImage("images/reset.png")

    menuFrameRect = pygame.Rect(menu_button_start_pos_x, menu_button_y_pos, width + 2.5, menu_button_height)
    pygame.draw.rect(win, dark_grey, menuFrameRect, gui_line_border)

    controlFrameRect = pygame.Rect(play_button_x, menu_button_y_pos, 25 * 3 - 1, menu_button_height)
    pygame.draw.rect(win, dark_grey, controlFrameRect, gui_line_border)
    
    timelineFrameRect = pygame.Rect(0.5,  40, x + 5, y - 300)
    pygame.draw.rect(win, dark_grey, timelineFrameRect, gui_line_border)

    volumeUpButton.draw()
    volumeDownButton.draw()

    pygame.display.update()

close_audio_stream()
pygame.quit()
