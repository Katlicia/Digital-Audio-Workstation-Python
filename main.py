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

track_spacing = 10
track_start_y = 50
editing_track = None
original_text = ""
playing_now = False

theme = darkTheme
themestr = "darkTheme"
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
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height, 120, menu_button_height, win, rectcolor, linecolor, text_color, "Export as WAV", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height * 2, 120, menu_button_height, win, rectcolor, linecolor, text_color, "Export as MP3", font_size=15),
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
    Button(700, 680, 120, 30, win, linecolor, linecolor, text_color, "Reverb", 15),
    Button(700, 720, 120, 30, win, linecolor, linecolor, text_color, "Delay", 15),
    Button(700, 760, 120, 30, win, linecolor, linecolor, text_color, "Pitch Shift", 15),
    Button(700, 800, 120, 30, win, linecolor, linecolor, text_color, "Distortion", 15),
    Button(700, 840, 120, 30, win, linecolor, linecolor, text_color, "Gain", 15),
    Button(700, 880, 120, 30, win, linecolor, linecolor, text_color, "Equalizer", 15),
]

# Gain (gain 0.0 - 2.0)
# EQ (low_gain = 1.0, mid_gan = 1.0, high_gain = 1.0) 0.0 - 2.0 1 Değiştirmez
# Reverb (intensity = 0.0 - 1.0, max_length = 2.0 saniye)
# Delay (delay_time = 0.1 - 1.0 saniye, feedback = 0.0 - 1.0 tam yankı)
# Pitch shift (semitones= 0 değişmez) - 12 bir oktav düşür + 12 bir oktav yükselt
# Distortion (intensity = 0.5 - 5.0, )

timeline = Timeline()
audio_manager = AudioManager()
audio_manager.timeline = timeline

def update_menu_colors():
    for file_button in file_menu_buttons:
        file_button.passive_color = rectcolor
        file_button.active_color = linecolor
        file_button.text_color = text_color
    
    for theme_button in theme_menu_buttons:
        theme_button.passive_color = rectcolor
        theme_button.active_color = linecolor
        theme_button.text_color = text_color

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
                update_menu_colors()
                theme_menu_open = False

            elif file_menu_open:
                for file_button in file_menu_buttons:
                    if file_button.isClicked(pos):
                        if file_button.text == "Export as WAV" or file_button.text == "Export as MP3":
                            audio_manager.export_tracks_to_file()
                        elif file_button.text == "Import as WAV/MP3":
                            load_track()

                file_menu_open = False

            elif MenuButtonList[0].isClicked(pos):
                file_menu_open = not file_menu_open
            elif MenuButtonList[-1].isClicked(pos):
                theme_menu_open = not theme_menu_open

            if recordButton.isClicked(pos):
                if audio_manager.recording:
                    audio_manager.stop_recording()
                    timeline.stop_timeline_recording()
                    recordButton.setImage("images/record.png")
                else:
                    audio_manager.start_recording()
                    timeline.start_timeline_recording(audio_manager.current_track)
                    recordButton.setImage("images/recording.png")

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
    
    fx_frame_rect = pygame.Rect(x / 2 - 400 - gui_line_border, timeline_y + timeline_height + 25 - gui_line_border, 800 + gui_line_border, 300 + gui_line_border)
    pygame.draw.rect(win, linecolor, fx_frame_rect)

    fx_rect = pygame.Rect(x / 2 - 400, timeline_y + timeline_height + 25, 800 - gui_line_border, 300 - gui_line_border)
    pygame.draw.rect(win, rectcolor, fx_rect)

    font2 = pygame.font.SysFont("Arial", 300)
    text = font2.render("FX", True, linecolor)
    text_rect = text.get_rect(center=(fx_rect.center))
    win.blit(text, text_rect)

    for i in effectButtonList:
        i.rect.x = fx_rect.x + 20
        i.draw()

    update_menu_colors()
    pygame.display.update()

    clock.tick()

pygame.quit()
