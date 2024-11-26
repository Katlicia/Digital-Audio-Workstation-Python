import pygame
from button import *
from config import *
from audio import *

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

clock = pygame.time.Clock()
running = True

MenuButtonList = [
    # FileButton
    Button(menu_button_start_pos_x, menu_button_y_pos, menu_button_width, menu_button_height, win, "FILE", menu_button_font_size, dark_grey),
    # EditButton
    Button(menu_button_start_pos_x+menu_button_width, menu_button_y_pos, menu_button_width, menu_button_height, win, "EDIT", menu_button_font_size, dark_grey),
    # SaveButton 
    Button(menu_button_start_pos_x+menu_button_width*2, menu_button_y_pos, menu_button_width, menu_button_height, win, "SAVE", menu_button_font_size, dark_grey),
    # ThemeButton
    Button(menu_button_start_pos_x+menu_button_width*3, menu_button_y_pos, menu_button_width+5, menu_button_height, win, "THEME", menu_button_font_size, dark_grey)
]

# recordButton = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 100, 100, win, "Record")
# stopButton = Button(SCREEN_WIDTH / 2 + 200, SCREEN_HEIGHT / 2, 100, 100, win, "Stop")

# playButton = Button(100, 100, 100, 100, win, "Play")
# exportButton = Button(300, 100, 100, 100, win, "Export")

def draw_recording_list(win, recordings):
    font = pygame.font.Font(None, 36)
    y = 50
    for name in recordings.keys():
        text_surface = font.render(name, True, "black")
        win.blit(text_surface, (50, y))
        y += 40


while running:
    x, y = win.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        pos = pygame.mouse.get_pos()
        
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     pos = pygame.mouse.get_pos()
        #     if recordButton.isClicked(pos):
        #         start_recording()
        #     if stopButton.isClicked(pos):
        #         stop_recording("sound1")
        #     if playButton.isClicked(pos):
        #         play_recording("sound1")
        #     if exportButton.isClicked(pos):
        #         export_recording("sound1", "sound1.wav")


    win.fill("grey")
    pygame.draw.rect(win, light_blue, pygame.Rect(0, 0, x, 40))

    width = 0
    for MenuButton in MenuButtonList:
        MenuButton.draw()
        MenuButton.isClicked(pos)
        width += MenuButton.width

    pygame.draw.rect(win, (59, 59, 59), pygame.Rect(5, 7.5, width + 2.5, 25), 2)
    # recordButton.draw()
    # stopButton.draw()
    # playButton.draw()
    # exportButton.draw()
    # draw_recording_list(win, recordings)
    

    pygame.display.update()
    
pygame.quit()
