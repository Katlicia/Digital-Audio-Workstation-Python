import json
import os
import re
import threading
import time
from tkinter import messagebox
import numpy as np
import pygame
from button import Button, ImageButton
from config import *
from timeline import Timeline
from audio_utils import AudioManager
import tkinter as tk
from tkinter import filedialog

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont("Arial", 24)
fxfont = pygame.font.SysFont("Arial", 12)

track_spacing = 10
track_start_y = 50
editing_track = None
original_text = ""
playing_now = False
dragging_effect = None
dragging_pos = (0, 0)

def save_theme_to_file(theme_name):
    """
    Saves theme to settings.json
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({"theme": theme_name}, f)
    except Exception as e:
        print(f"Error saving theme: {e}")

def load_theme_from_file():
    """
    Uploads theme from settings.json
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("theme", "darkTheme")
        except Exception as e:
            print(f"Error loading theme: {e}")
            return "darkTheme"
    return "darkTheme"

loaded_theme = load_theme_from_file()
if loaded_theme == "darkTheme":
    theme = darkTheme
elif loaded_theme == "lightTheme":
    theme = lightTheme
elif loaded_theme == "strawberryTheme":
    theme = strawberryTheme
elif loaded_theme == "greenteaTheme":
    theme = greenteaTheme
elif loaded_theme == "mochiTheme":
    theme = mochiTheme
elif loaded_theme == "sakuraTheme":
    theme = sakuraTheme

themestr = loaded_theme

timelinetrackcolor = theme[0] # Timelinetrack color
temptrackcolor = theme[1] # Temp track, waveform color
linecolor = theme[2] # Line, active button color
rectcolor = theme[3] # Track, passive button color
wincolor = theme[4] # Win, timeline color
text_color = (255, 255, 255) # Text color

recordButton = ImageButton(record_button_x, menu_button_y_pos, "images/record.png", win)
playButton = ImageButton(play_button_x, menu_button_y_pos, f"images/{themestr}/playpassive.png", win)
stopButton = ImageButton(stop_button_x, menu_button_y_pos, f"images/{themestr}/pausepassive.png", win)
resetButton = ImageButton(reset_button_x, menu_button_y_pos, f"images/{themestr}/resetpassive.png", win)
volumeUpButton = ImageButton(volume_up_button_x, menu_button_y_pos, f"images/{themestr}/sounduppassive.png", win)
volumeDownButton = ImageButton(volume_down_button_x, menu_button_y_pos, f"images/{themestr}/sounddownpassive.png", win)

file_menu_open = False
file_menu_buttons = [
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height, 120, menu_button_height, win, rectcolor, linecolor, text_color, "Load Project", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height * 2, 120, menu_button_height, win, rectcolor, linecolor, text_color, "Export as WAV/MP3", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height * 3, 120, menu_button_height, win, rectcolor, linecolor, text_color, "Import as WAV/MP3", font_size=15)

]

theme_menu_open = False
theme_menu_buttons = [
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Dark", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 2, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Light", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 3, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Strawberry", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 4, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Green Tea", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 5, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Mochi", font_size=15), 
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 6, 80, menu_button_height, win, rectcolor, linecolor, text_color, "Sakura", font_size=15)
]

save_menu_open = False
save_menu_buttons = [
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*2, menu_button_y_pos + menu_button_height, 83, menu_button_height, win, rectcolor, linecolor, text_color, "Save Project", font_size=15)
]

edit_menu_open = False
edit_menu_buttons = [
     Button(menu_button_start_pos_x+gui_line_border+menu_button_width, menu_button_y_pos + menu_button_height, 50, menu_button_height, win, rectcolor, linecolor, text_color, "Undo", font_size=15)
]

MenuButtonList = [
    # FileButton
    Button(menu_button_start_pos_x, menu_button_y_pos, menu_button_width, menu_button_height, win, rectcolor, linecolor, text_color, "FILE", menu_button_font_size),
    # EditButton
    Button(menu_button_start_pos_x+menu_button_width, menu_button_y_pos, menu_button_width, menu_button_height, win, rectcolor, linecolor, text_color, "EDIT", menu_button_font_size),
    # SaveButton 
    Button(menu_button_start_pos_x+menu_button_width*2, menu_button_y_pos, menu_button_width, menu_button_height, win, rectcolor, linecolor, text_color, "SAVE", menu_button_font_size),
    # ThemeButton
    Button(menu_button_start_pos_x+menu_button_width*3, menu_button_y_pos, menu_button_width+5, menu_button_height, win, rectcolor, linecolor, text_color, "THEME", menu_button_font_size)
]

TrackRectList = [
    Button(3, 70, 167, 56, win, rectcolor, linecolor, text_color, "Track 1", 15),
    Button(3, 127, 167, 56, win, rectcolor, linecolor, text_color, "Track 2", 15),
    Button(3, 184, 167, 56, win, rectcolor, linecolor, text_color, "Track 3", 15),
    Button(3, 241, 167, 56, win, rectcolor, linecolor, text_color, "Track 4", 15),
    Button(3, 298, 167, 56, win, rectcolor, linecolor, text_color, "Track 5", 15),
    Button(3, 355, 167, 56, win, rectcolor, linecolor, text_color, "Track 6", 15),
    Button(3, 412, 167, 56, win, rectcolor, linecolor, text_color, "Track 7", 15),
    Button(3, 469, 167, 56, win, rectcolor, linecolor, text_color, "Track 8", 15),
    Button(3, 526, 167, 56, win, rectcolor, linecolor, text_color, "Track 9", 15),
    Button(3, 583, 167, 53, win, rectcolor, linecolor, text_color, "Track 10", 15)
]

TrackMuteButtonList = [
    Button(110, 98, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 155, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 212, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 269, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 326, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 383, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 440, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 497, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 554, 20, 20, win, rectcolor, linecolor, text_color, "M", 15),
    Button(110, 611, 20, 20, win, rectcolor, linecolor, text_color, "M", 15)
]

TrackSoloButtonList = [
    Button(132, 98, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 155, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 212, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 269, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 326, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 383, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 440, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 497, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 554, 20, 20, win, rectcolor, linecolor, text_color, "S", 15),
    Button(132, 611, 20, 20, win, rectcolor, linecolor, text_color, "S", 15)
]



effectButtonList = [
    {"button": Button(300, 680, 120, 30, win, linecolor, rectcolor, text_color, "Reverb", 15), "effect": "apply_reverb", "params": {"intensity": 0.8, "max_length": 2.0}},
    {"button": Button(700, 720, 120, 30, win, linecolor, rectcolor, text_color, "Delay", 15), "effect": "apply_delay", "params": {"delay_time": 0.3, "feedback": 0.5}},
    {"button": Button(700, 760, 120, 30, win, linecolor, rectcolor, text_color, "Pitch Shift", 15), "effect": "apply_pitch_shift", "params": {"semitones": 3}},
    {"button": Button(700, 800, 120, 30, win, linecolor, rectcolor, text_color, "Distortion", 15), "effect": "apply_distortion", "params": {"intensity": 5.0}},
    {"button": Button(700, 840, 120, 30, win, linecolor, rectcolor, text_color, "Gain", 15), "effect": "apply_volume", "params": {"gain": 2.0}},
    {"button": Button(700, 880, 120, 30, win, linecolor, rectcolor, text_color, "Equalizer", 15), "effect": "apply_equalizer", "params": {"low_gain": 1.2, "mid_gain": 1.0, "high_gain": 1.5}}
]

timeline = Timeline()
audio_manager = AudioManager()
audio_manager.timeline = timeline

def update_menu_colors():
    for file_button in file_menu_buttons:
        file_button.passive_color = rectcolor
        file_button.active_color = linecolor
    
    for theme_button in theme_menu_buttons:
        theme_button.passive_color = rectcolor
        theme_button.active_color = linecolor
    
    for save_button in save_menu_buttons:
        save_button.passive_color = rectcolor
        save_button.active_color = linecolor
    
    for edit_button in edit_menu_buttons:
        edit_button.passive_color = rectcolor
        edit_button.active_color = linecolor

def load_track():
    """
    Uploads an audio to the next empty track.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file_path:
        next_empty_track = audio_manager.find_next_empty_track()
        if next_empty_track is not None:
            audio_manager.load_audio_file(file_path, next_empty_track)

def show_effect_params(effect_name, default_params):
    """
    It receives effect parameters from the user and checks them according to the given value ranges.
    """
    params = default_params.copy()
    result = []

    effect_limits = {
        "apply_reverb": {"Intensity": (0.0, 2.0), "Max Length": (0.1, 5.0)},
        "apply_delay": {"Delay Time": (0.1, 2.0), "Feedback": (0.0, 1.0)},
        "apply_pitch_shift": {"Semitones": (-12, 12)},
        "apply_distortion": {"Intensity": (0.5, 5.0)},
        "apply_volume": {"Gain": (0.0, 10.0)},
        "apply_equalizer": {"Low Gain": (0.0, 2.0), "Mid Gain": (0.0, 2.0), "High Gain": (0.0, 2.0)}
    }

    def tkinter_task():
        nonlocal result
        root = tk.Tk()
        root.title(f"Edit {effect_name} Parameters")
        root.geometry("350x300")
        root.resizable(False, False)

        entry_fields = {}
        warning_label = tk.Label(root, text="", fg="red")
        warning_label.grid(row=len(default_params) + 1, column=0, columnspan=2, pady=5)

        def save():
            valid_input = True
            warning_message = ""

            for key, entry in entry_fields.items():
                try:
                    value = float(entry.get())
                    min_val, max_val = effect_limits[effect_name][key]
                    if not (min_val <= value <= max_val):
                        valid_input = False
                        warning_message += f"{key}: {min_val} - {max_val}\n"
                    else:
                        params[key] = value
                except ValueError:
                    valid_input = False
                    warning_message += f"{key}: Enter a valid number!\n"

            if valid_input:
                result.append(params.copy())
                root.quit()
                root.destroy()
            else:
                warning_label.config(text="Incorrect entry!\n" + warning_message)

        def cancel():
            result.append(None)
            root.quit()
            root.destroy()

        # snake_case → Pascal Case
        def snake_to_pascal(name):
            return " ".join(word.capitalize() for word in name.split("_"))

        # Show args
        for idx, (param, value) in enumerate(default_params.items()):
            display_name = snake_to_pascal(param)
            tk.Label(root, text=f"{display_name}:").grid(row=idx, column=0, padx=10, pady=5)
            entry = tk.Entry(root)
            entry.insert(0, str(value))
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entry_fields[display_name] = entry

        # Save and cancel buttons
        tk.Button(root, text="Save", command=save).grid(row=len(default_params) + 2, column=0, pady=10)
        tk.Button(root, text="Cancel", command=cancel).grid(row=len(default_params) + 2, column=1, pady=10)

        root.mainloop()

    # Run Tkinter in a separate thread
    thread = threading.Thread(target=tkinter_task)
    thread.start()
    thread.join()

    return result[0] if result else None

def pascal_to_snake(name):
    """PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).replace(" ", "").lower()

def ask_to_save_before_exit():
    root = tk.Tk()
    root.withdraw()

    response = messagebox.askyesnocancel("Exit", "Do you want to save your project before exiting?")
    root.destroy()
    return response

while running:
    x, y = win.get_size()
    pygame.key.set_repeat(200, 50)

    timelinetrackcolor = theme[0]
    temptrackcolor = theme[1]
    linecolor = theme[2] 
    rectcolor = theme[3] 
    wincolor = theme[4]

    delta_time = clock.get_time() / 1000
    pos = pygame.mouse.get_pos()

    timeline.update_cursor(delta_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if audio_manager.is_project_empty():
                running = False
            if not audio_manager.is_dirty:
                running = False
            else:
                user_choice = ask_to_save_before_exit()
                if user_choice is True:
                    audio_manager.save_project(TrackRectList)
                    running = False
                elif user_choice is False:
                    running = False


        timeline.handleScroll(event)
        timeline.handleClick(event, timeline_x, timeline_y, x, timeline_height, audio_manager)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if theme_menu_open:
                for theme_button in theme_menu_buttons:
                    if theme_button.isClicked(pos):
                        if theme_button.text == "Dark":
                            theme = darkTheme
                            themestr = "darkTheme"
                        elif theme_button.text == "Light":
                            theme = lightTheme
                            themestr = "lightTheme"
                        elif theme_button.text == "Strawberry":
                            theme = strawberryTheme
                            themestr = "strawberryTheme"
                        elif theme_button.text == "Green Tea":
                            theme = greenteaTheme
                            themestr = "greenteaTheme"
                        elif theme_button.text == "Mochi":
                            theme = mochiTheme
                            themestr = "mochiTheme"
                        elif theme_button.text == "Sakura":
                            theme = sakuraTheme
                            themestr = "sakuraTheme"
                        save_theme_to_file(themestr)
                theme_menu_open = False

            elif save_menu_open:
                for save_button in save_menu_buttons:
                    if save_button.isClicked(pos):
                        audio_manager.save_project(TrackRectList)
                save_menu_open = False
            
            elif edit_menu_open:
                for edit_button in edit_menu_buttons:
                    if edit_button.isClicked(pos):
                        audio_manager.undo()
                edit_menu_open = False

            elif file_menu_open:
                for file_button in file_menu_buttons:
                    if file_button.isClicked(pos):
                        if file_button.text == "Export as WAV/MP3":
                            audio_manager.export_tracks_to_file()
                        elif file_button.text == "Import as WAV/MP3":
                            load_track()
                        elif file_button.text == "Load Project":
                            audio_manager.load_project(TrackRectList)

                file_menu_open = False

            elif MenuButtonList[0].isClicked(pos):
                file_menu_open = not file_menu_open
            elif MenuButtonList[-1].isClicked(pos):
                theme_menu_open = not theme_menu_open
            elif MenuButtonList[-2].isClicked(pos):
                save_menu_open = not save_menu_open
            elif MenuButtonList[1].isClicked(pos):
                edit_menu_open = not edit_menu_open

            if recordButton.isClicked(pos) and audio_manager.find_next_empty_track() != None:
                if audio_manager.recording:
                    audio_manager.stop_recording()
                    timeline.stop_timeline_recording()
                    recordButton.setImage("images/record.png")
                else:
                    audio_manager.start_recording()
                    timeline.start_timeline_recording(audio_manager.current_track)
                    recordButton.setImage("images/recording.png")
    
            if recordButton.isClicked(pos) and audio_manager.find_next_empty_track() == None:
                root = tk.Tk()
                root.withdraw()
                messagebox.showwarning("Track Full", "All 10 tracks are full. Cannot start recording!")

            if playButton.isClicked(pos) and audio_manager.recording == False:
                audio_manager.play_all_tracks()
                timeline.is_playing = True
                playing_now = True

            if stopButton.isClicked(pos):
                audio_manager.stop_playing()
                timeline.is_playing = False
                playing_now = False

            if resetButton.isClicked(pos):
                audio_manager.stop_playing()
                timeline.reset_timeline()
                playing_now = False

            if volumeUpButton.isClicked(pos):
                audio_manager.adjust_volume(0.1) # Up %10
            if volumeDownButton.isClicked(pos):
                audio_manager.adjust_volume(-0.1)  # Down %10

            for i, button in enumerate(TrackRectList):
                text_surface = button.font.render(button.text, True, text_color)
                text_rect = text_surface.get_rect(topleft=button.rect.topleft)

                if text_rect.collidepoint(pos): 
                    editing_track = i
                    original_text = button.text
                    break


            for i, solo in enumerate(TrackSoloButtonList):
                if solo.isClicked(pos):
                    # If mute is true for this track, turn it off
                    if audio_manager.muted_tracks[i]:
                        audio_manager.muted_tracks[i] = False
                        TrackMuteButtonList[i].passive_color = rectcolor

                    # If the track is currently soloed, un-solo it
                    if audio_manager.solo_tracks[i]:
                        audio_manager.solo_tracks[i] = False
                        solo.passive_color = rectcolor
                    else:
                        # Un-solo all other tracks
                        for j in range(len(audio_manager.solo_tracks)):
                            audio_manager.solo_tracks[j] = False
                            TrackSoloButtonList[j].passive_color = rectcolor

                        # Solo the clicked track
                        audio_manager.solo_tracks[i] = True
                        solo.passive_color = linecolor

            for i, mute in enumerate(TrackMuteButtonList):
                if mute.isClicked(pos):
                    # If solo is true then solo is false
                    if audio_manager.solo_tracks[i]:
                        audio_manager.solo_tracks[i] = False
                        TrackSoloButtonList[i].passive_color = rectcolor

                    # Change mute state
                    audio_manager.muted_tracks[i] = not audio_manager.muted_tracks[i]
                    mute.passive_color = linecolor if audio_manager.muted_tracks[i] else rectcolor

        if event.type == pygame.KEYDOWN:
            if editing_track is not None:
                if event.key == pygame.K_BACKSPACE:
                    if len(TrackRectList[editing_track].text) > 0:
                        TrackRectList[editing_track].text = TrackRectList[editing_track].text[:-1]
                elif event.key == pygame.K_RETURN and len(TrackRectList[editing_track].text) > 0:
                    editing_track = None
                    audio_manager.mark_dirty()
                elif event.key == pygame.K_ESCAPE:
                    TrackRectList[editing_track].text = original_text
                    editing_track = None
                else:
                    if len(TrackRectList[editing_track].text) < 25:
                        TrackRectList[editing_track].text += event.unicode
            if editing_track == None:
                if event.key == pygame.K_SPACE:
                    timeline.is_playing = not timeline.is_playing
                    if playing_now:
                        audio_manager.stop_playing()
                    else:
                        audio_manager.play_all_tracks()
                
                if event.key == pygame.K_r:
                    audio_manager.stop_playing()
                    timeline.reset_timeline()
                    playing_now = False
            
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                audio_manager.undo()
            
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                audio_manager.save_project(TrackRectList)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for effect in effectButtonList:
                if effect["button"].isClicked(pos):
                    dragging_effect = effect
                    dragging_pos = pos

        if event.type == pygame.MOUSEMOTION and dragging_effect:
            dragging_pos = pos

        if event.type == pygame.MOUSEBUTTONUP and dragging_effect:
            user_params = None
            for track_idx, trackRect in enumerate(TrackRectList):
                if trackRect.rect.collidepoint(pos):
                    effect_name = dragging_effect["effect"]
                    default_params = dragging_effect["params"]

                    user_params = show_effect_params(effect_name, default_params)
                    
                if user_params:
                    if audio_manager.tracks[track_idx] is not None:
                        effect_function = getattr(audio_manager, effect_name)

                        # Pascal Case → Snake Case
                        snake_case_params = {pascal_to_snake(k): v for k, v in user_params.items()}

                        # Change sound data to float32
                        track_data = audio_manager.tracks[track_idx].astype(np.float32)

                        try:
                            audio_manager.tracks[track_idx] = effect_function(track_data, **snake_case_params)
                            audio_manager.track_fx[track_idx].append(effect_name.replace("apply_", "").capitalize())
                            audio_manager.mark_dirty()
                        except Exception as e:
                            print(f"Error applying effect: {e}")

            dragging_effect = None

    wincolor = theme[4]
    win.fill(wincolor)

    width = 0
    for MenuButton in MenuButtonList:
        MenuButton.passive_color = rectcolor
        MenuButton.active_color = linecolor
        MenuButton.text_color = text_color
        MenuButton.draw()
        width += MenuButton.width

    recordButton.draw()
    playButton.draw()
    if playButton.isClicked(pos):
        playButton.setImage(f"images/{themestr}/playactive.png") 
    else:
        playButton.setImage(f"images/{themestr}/playpassive.png")
    stopButton.draw()
    if stopButton.isClicked(pos):
        stopButton.setImage(f"images/{themestr}/pauseactive.png")
    else:
        stopButton.setImage(f"images/{themestr}/pausepassive.png")
    resetButton.draw()
    if resetButton.isClicked(pos):
        resetButton.setImage(f"images/{themestr}/resetactive.png")
    else:
        resetButton.setImage(f"images/{themestr}/resetpassive.png")
    volumeUpButton.draw()
    if volumeUpButton.isClicked(pos):
        volumeUpButton.setImage(f"images/{themestr}/soundupactive.png")
    else:
        volumeUpButton.setImage(f"images/{themestr}/sounduppassive.png")
    volumeDownButton.draw()
    if volumeDownButton.isClicked(pos):
        volumeDownButton.setImage(f"images/{themestr}/sounddownactive.png")
    else:
        volumeDownButton.setImage(f"images/{themestr}/sounddownpassive.png")

    volume_text = font.render(f"Volume: {int(audio_manager.volume_level * 100)}", True, text_color)
    volume_text_rect = volume_text.get_rect(topleft=(volume_up_button_x + 60, menu_button_y_pos-gui_line_border))
    win.blit(volume_text, volume_text_rect)

    menuFrameRect = pygame.Rect(menu_button_start_pos_x, menu_button_y_pos, width + 2.5, menu_button_height)
    pygame.draw.rect(win, linecolor, menuFrameRect, gui_line_border)
    
    volumeFrameRect = pygame.Rect(volume_up_button_x, menu_button_y_pos, 25 * 2 - 1, menu_button_height)
    pygame.draw.rect(win, linecolor, volumeFrameRect, gui_line_border)

    controlFrameRect = pygame.Rect(play_button_x, menu_button_y_pos, 25 * 3 - 1, menu_button_height)
    pygame.draw.rect(win, linecolor, controlFrameRect, gui_line_border)
    
    timelineFrameRect = pygame.Rect(0.5, 40, x, 599)
    pygame.draw.rect(win, linecolor, timelineFrameRect, gui_line_border + 1)
    timeline.drawTimeline(win, timeline_x, timeline_y, x, timeline_height, audio_manager.tracks, audio_manager.sample_rate, rectcolor, linecolor, temptrackcolor, timelinetrackcolor, temptrackcolor, audio_manager)
    
    trackFrameLine = pygame.draw.line(win, linecolor, (0.5, 69), (timeline_x, 69))
    text = font.render("Tracks", True, text_color)
    text_rect = text.get_rect(center=(85, 55))
    win.blit(text, text_rect)

    for i in range(1, 10):
        pygame.draw.line(win, linecolor, (0.5, 69 + 57 * i), (timeline_x, 69 + 57 * i))

    for i, trackRect in enumerate(TrackRectList):
        trackRect.passive_color = rectcolor
        trackRect.active_color = linecolor
        if editing_track == i:
            pygame.draw.rect(win, trackRect.passive_color, trackRect.rect)
            text_surface = font.render(trackRect.text, True, text_color)
            win.blit(text_surface, (trackRect.rect.x + 5, trackRect.rect.y + (trackRect.rect.height - text_surface.get_height()) // 2))
        else:
            trackRect.drawLeft()
            fx_list = audio_manager.track_fx[i]
            if fx_list:
                start_x = trackRect.rect.x + 5
                start_y = trackRect.rect.y + 20

                for fx_idx, fx in enumerate(fx_list):
                    fx_text = fx[:2]
                    fx_surface = fxfont.render(fx_text, True, text_color)
                    fx_rect = fx_surface.get_rect(topleft=(start_x, start_y))

                    win.blit(fx_surface, fx_rect)
                    if event.type == pygame.MOUSEBUTTONDOWN and fx_rect.collidepoint(pos):
                        del audio_manager.track_fx[i][fx_idx]
                        break

                    start_x += fx_rect.width + 10
                
    
    pygame.draw.line(win, linecolor, (timeline_x-1,  timeline_y), (timeline_x-1, timeline_y+timeline_height))

    for i, muteButton in enumerate(TrackMuteButtonList):
        muteButton.passive_color = rectcolor if not audio_manager.muted_tracks[TrackMuteButtonList.index(muteButton)] else linecolor
        muteButton.active_color = linecolor
        pygame.draw.rect(win, linecolor, pygame.Rect(muteButton.rect.x - gui_line_border, muteButton.rect.y - gui_line_border, 46, 24), gui_line_border)
        pygame.draw.line(win, linecolor, (muteButton.rect.x + muteButton.width, muteButton.rect.y - gui_line_border), (muteButton.rect.x + muteButton.width, muteButton.rect.y + 21), gui_line_border)
        muteButton.draw()

    for i, soloButton in enumerate(TrackSoloButtonList):
        soloButton.passive_color = rectcolor if not audio_manager.solo_tracks[TrackSoloButtonList.index(soloButton)] else linecolor
        soloButton.active_color = linecolor
        soloButton.draw()
        soloButton.isClicked(pos)

    if file_menu_open:
        for file_button in file_menu_buttons:
            file_button.drawLeft()

    if theme_menu_open:
        for theme_button in theme_menu_buttons:
            theme_button.drawLeft()
    
    if save_menu_open:
        for save_button in save_menu_buttons:
            save_button.drawLeft()
    
    if edit_menu_open:
        for edit_button in edit_menu_buttons:
            edit_button.drawLeft()
    
    fx_frame_rect = pygame.Rect(x / 2 - 400 - gui_line_border, timeline_y + timeline_height + 25 - gui_line_border, 800 + gui_line_border, 300 + gui_line_border)
    pygame.draw.rect(win, linecolor, fx_frame_rect)

    fx_rect = pygame.Rect(x / 2 - 400, timeline_y + timeline_height + 25, 800 - gui_line_border, 300 - gui_line_border)
    pygame.draw.rect(win, rectcolor, fx_rect)

    font2 = pygame.font.SysFont("Arial", 300)
    text = font2.render("FX", True, linecolor)
    text_rect = text.get_rect(center=(fx_rect.center))
    win.blit(text, text_rect)

    total_width = 3 * button_width + 2 * button_gap_x
    total_height = 2 * button_height + button_gap_y

    start_x = fx_rect.centerx - total_width // 2
    start_y = fx_rect.centery - total_height // 2

    effect_title_font = pygame.font.SysFont("Arial", 28, bold=True)
    effect_title = effect_title_font.render("Effects", True, linecolor)
    win.blit(effect_title, (fx_rect.x + 20, fx_rect.y + 5))
    pygame.draw.line(win, linecolor, (fx_rect.x + 20, fx_rect.y + 35),
                    (fx_rect.x + fx_rect.width - 20, fx_rect.y + 35), 2)

    for idx, effect in enumerate(effectButtonList):
        col = idx % 3
        row = idx // 3

        x = start_x + col * (button_width + button_gap_x)
        y = start_y + row * (button_height + button_gap_y)

        shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, button_width, button_height)
        pygame.draw.rect(win, linecolor, shadow_rect, border_radius=10)

        effect["button"].rect.x = x
        effect["button"].rect.y = y

        if effect["button"].isClicked(pos):
            pygame.draw.rect(win, linecolor, effect["button"].rect, border_radius=10)
        else:
            pygame.draw.rect(win, rectcolor, effect["button"].rect, border_radius=10)

        text_surface = font.render(effect["button"].text, True, text_color)
        text_rect = text_surface.get_rect(center=effect["button"].rect.center)
        win.blit(text_surface, text_rect)

    if dragging_effect:
        effect_surface = font.render(dragging_effect["button"].text, True, text_color)
        win.blit(effect_surface, (dragging_pos[0] - 20, dragging_pos[1] - 10))

    if audio_manager.save_feedback:
        message, timestamp = audio_manager.save_feedback
        elapsed_time = time.time() - timestamp

        if elapsed_time < SAVE_FEEDBACK_DURATION:
            alpha = max(0, 255 - int((elapsed_time / SAVE_FEEDBACK_DURATION) * 255))

            feedback_surface = font.render(message, True, (255, 255, 255))
            feedback_surface.set_alpha(alpha)

            feedback_rect = feedback_surface.get_rect()
            feedback_rect.bottomright = (win.get_width() - 10, win.get_height() - 10)

            background_surface = pygame.Surface(feedback_rect.size)
            background_surface.fill(linecolor)
            background_surface.set_alpha(alpha)

            win.blit(background_surface, feedback_rect)
            win.blit(feedback_surface, feedback_rect)
        else:
            audio_manager.save_feedback = None 


    update_menu_colors()
    pygame.display.update()

    clock.tick()

pygame.quit()
