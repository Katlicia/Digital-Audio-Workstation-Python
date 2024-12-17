import pygame


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024

menu_button_start_pos_x = 5
menu_button_y_pos = 7.5
menu_button_width = 40
menu_button_height = 25
menu_button_font_size = 15

gui_line_border = 2

grey = (99, 99, 99)
dark_grey = (59, 59, 59)
light_blue = (232,244,248)


record_button_x = 200

control_buttons_gap = 24
play_button_x = 250
stop_button_x = play_button_x + control_buttons_gap
reset_button_x = stop_button_x + control_buttons_gap
volume_up_button_x = reset_button_x + 50
volume_down_button_x = volume_up_button_x + control_buttons_gap 

timeline_x = 170
timeline_y = 43
timeline_height = 593


darkTheme = ((40, 40, 40), (0, 0, 0), (59, 59, 59), (99, 99, 99), (80, 80, 80))
lightTheme = ((120, 120, 120), (80, 80, 80), (99, 99, 99), (200, 200, 200), (160, 160, 160))
strawberryTheme = ((186, 39, 54), (218, 61, 76), (222, 62, 93), (236, 86, 127), (239, 92, 142))
greenteaTheme = ((46, 133, 23), (75, 148, 56), (113, 162, 91), (130, 179, 108), (147, 196, 125))
mochiTheme = ((71, 26, 26), (67, 159, 119), (27, 87, 14), (45, 114, 29), (45, 144, 29))
sakuraTheme = ((112, 64, 65), (173, 242, 241), 	(239, 151, 152), (245, 195, 196), (232, 172, 172))


button_width = 120
button_height = 35
button_gap_x = 100
button_gap_y = 100
shadow_offset = 5
shadow_color = (50, 50, 50)


SETTINGS_FILE = "settings.json"
