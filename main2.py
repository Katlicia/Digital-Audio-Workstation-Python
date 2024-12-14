import pygame
from button import Button, ImageButton
from config import *
from timeline import Timeline
import sounddevice as sd
import numpy as np

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

def audio_playback_callback(outdata, frames, time, status):
    global playing_audio, current_audio_position, volume_level

    if playing_audio is not None:
        end_position = current_audio_position + frames
        audio_chunk = playing_audio[current_audio_position:end_position]
        audio_chunk = audio_chunk * volume_level

        if len(audio_chunk.shape) == 1:
            audio_chunk = audio_chunk[:, np.newaxis]

        if len(audio_chunk) < frames:
            outdata[:len(audio_chunk)] = audio_chunk
            outdata[len(audio_chunk):] = 0
            playing_audio = None
        else:
            outdata[:] = audio_chunk

        current_audio_position = end_position
    else:
        outdata.fill(0)

def find_next_empty_track():
    return next((i for i, track in enumerate(tracks) if track is None), None)

def start_recording():
    global recording, current_audio, current_track
    next_track = find_next_empty_track()
    if next_track is not None:
        recording = True
        current_track = next_track
        current_audio = []

def stop_recording():
    global recording, current_audio, tracks
    if recording:
        if current_audio:
            audio_data = np.concatenate(current_audio, axis=0)
            tracks[current_track] = audio_data
        recording = False

def audio_callback(indata, frames, time, status):
    if recording:
        current_audio.append(indata.copy())

def play_selected_track():
    global playing_audio, current_audio_position, stream
    if selected_track is not None and tracks[selected_track] is not None:
        playing_audio = tracks[selected_track]
        current_audio_position = 0
        if stream is not None:
            stream.close()
        stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
        stream.start()

def stop_playing():
    global playing_audio, stream
    playing_audio = None
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None

def play_all_tracks():
    global playing_audio, current_audio_position, stream
    if any(track is not None for track in tracks):
        max_length = max(len(track) for track in tracks if track is not None)
        mixed_audio = np.zeros(max_length, dtype=np.float32)

        for track in tracks:
            if track is not None:
                if len(track.shape) > 1:
                    track = np.mean(track, axis=1)
                padded_track = np.pad(track, (0, max_length - len(track)), 'constant')
                mixed_audio += padded_track

        mixed_audio /= np.max(np.abs(mixed_audio))
        playing_audio = mixed_audio
        current_audio_position = 0

        if stream is not None:
            stream.close()
        stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
        stream.start()

def play_tracks_based_on_timeline(delta_time):
    global playing_audio, current_audio_position, stream
    cursor_time = timeline.cursor_position / timeline.unit_width  # Current time in seconds

    for i, track in enumerate(tracks):
        if track is not None:
            track_start_time = timeline.track_starts[i] / timeline.unit_width
            if cursor_time >= track_start_time and not np.array_equal(playing_audio, track):
                playing_audio = track
                current_audio_position = int((cursor_time - track_start_time) * sample_rate)
                if stream is not None:
                    stream.close()
                stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
                stream.start()
                break

def adjust_volume(change):
    global volume_level
    volume_level = max(0.0, min(1.50, volume_level + change))

clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 24)

tracks = [None] * 10
selected_track = None
recording = False
current_track = None
editing_track = None
original_text = ""
playing_now = False

playing_audio = None
current_audio_position = 0
stream = None

sample_rate = 44100
current_audio = None

stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
stream.start()

volume_level = 1.0

volumeUpButton = Button(650, 10, 40, 25, win, "+")
volumeDownButton = Button(700, 10, 40, 25, win, "-")

MenuButtonList = [
    Button(menu_button_start_pos_x, menu_button_y_pos, menu_button_width, menu_button_height, win, "FILE", menu_button_font_size, grey),
    Button(menu_button_start_pos_x+menu_button_width, menu_button_y_pos, menu_button_width, menu_button_height, win, "EDIT", menu_button_font_size, grey),
    Button(menu_button_start_pos_x+menu_button_width*2, menu_button_y_pos, menu_button_width, menu_button_height, win, "SAVE", menu_button_font_size, grey),
    Button(menu_button_start_pos_x+menu_button_width*3, menu_button_y_pos, menu_button_width+5, menu_button_height, win, "THEME", menu_button_font_size, grey)
]

recordButton = ImageButton(record_button_x, menu_button_y_pos, "images/record.png", win)
playButton = ImageButton(play_button_x, menu_button_y_pos, "images/play.png", win)
stopButton = ImageButton(stop_button_x, menu_button_y_pos, "images/pause.png", win)
resetButton = ImageButton(reset_button_x, menu_button_y_pos, "images/reset.png", win)

TrackRectList = [
    Button(3, 70 + i * 57, 167, 56, win, f"Track {i+1}", 15, "white", "black") for i in range(10)
]

TrackMuteButtonList = [
    Button(110, 98 + i * 57, 20, 20, win, "M", 15, grey, "white") for i in range(10)
]

TrackSoloButtonList = [
    Button(132, 98 + i * 57, 20, 20, win, "S", 15, grey, "white") for i in range(10)
]

timeline = Timeline()

while running:
    delta_time = clock.get_time() / 1000
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        timeline.handleScroll(event)
        timeline.handleClick(event, timeline_x, timeline_y, SCREEN_WIDTH, timeline_height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if recordButton.isClicked(pos):
                if recording:
                    stop_recording()
                    timeline.stop_timeline_recording()
                    recordButton.setImage("images/record.png")
                else:
                    start_recording()
                    timeline.start_timeline_recording(current_track)
                    recordButton.setImage("images/recording.png")

            if playButton.isClicked(pos):
                timeline.is_playing = True
                playing_now = True

            if stopButton.isClicked(pos):
                stop_playing()
                timeline.is_playing = False
                playing_now = False

            if resetButton.isClicked(pos):
                stop_playing()
                timeline.is_playing = False
                playing_now = False
                timeline.cursor_position = 0

            if volumeUpButton.isClicked(pos):
                adjust_volume(0.1)
            if volumeDownButton.isClicked(pos):
                adjust_volume(-0.1)

            for i, solo in enumerate(TrackSoloButtonList):
                if solo.isClicked(pos):
                    if tracks[i] is not None and len(tracks[i]) > 0:
                        selected_track = i

        if event.type == pygame.KEYDOWN:
            if editing_track is not None:
                if event.key == pygame.K_BACKSPACE:
                    TrackRectList[editing_track].text = TrackRectList[editing_track].text[:-1]
                elif event.key == pygame.K_RETURN:
                    editing_track = None
                elif event.key == pygame.K_ESCAPE:
                    TrackRectList[editing_track].text = original_text
                    editing_track = None
                else:
                    if len(TrackRectList[editing_track].text) < 15:
                        TrackRectList[editing_track].text += event.unicode

            if event.key == pygame.K_SPACE:
                timeline.is_playing = not timeline.is_playing
                if not timeline.is_playing:
                    stop_playing()

            if event.key == pygame.K_r:
                timeline.cursor_position = 0
                timeline.is_playing = False
                stop_playing()
                playing_now = False

    if timeline.is_playing:
        play_tracks_based_on_timeline(delta_time)

    timeline.update_cursor(delta_time)
    win.fill("grey")

    for MenuButton in MenuButtonList:
        MenuButton.draw()
        MenuButton.isClicked(pos)

    recordButton.draw()
    playButton.draw()
    stopButton.draw()
    resetButton.draw()

    timeline.drawTimeline(win, timeline_x, timeline_y, SCREEN_WIDTH, timeline_height, tracks, sample_rate, "grey", "white")

    for trackRect in TrackRectList:
        trackRect.drawLeft()

    for muteButton in TrackMuteButtonList:
        muteButton.draw()
        muteButton.isClicked(pos)

    for soloButton in TrackSoloButtonList:
        soloButton.draw()
        soloButton.isClicked(pos)

    volumeUpButton.draw()
    volumeDownButton.draw()

    pygame.display.update()
    clock.tick(144)

pygame.quit()
