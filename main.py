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
    """
    Çalma sırasında ses akışı için callback fonksiyonu.
    """
    global playing_audio, current_audio_position, volume_level

    if playing_audio is not None:
        # Çalınacak sesin pozisyonunu hesapla
        end_position = current_audio_position + frames
        audio_chunk = playing_audio[current_audio_position:end_position]

        # Ses seviyesi uygula
        audio_chunk = audio_chunk * volume_level

        # Ses verisini doğru şekle dönüştür (mono için)
        if len(audio_chunk.shape) == 1:
            audio_chunk = audio_chunk[:, np.newaxis]  # Tek kanallı ses için (num_frames, 1)

        # Akışa yaz
        if len(audio_chunk) < frames:
            outdata[:len(audio_chunk)] = audio_chunk
            outdata[len(audio_chunk):] = 0  # Kalan kısmı sıfırla
            playing_audio = None  # Sesin sonuna ulaşıldı
        else:
            outdata[:] = audio_chunk

        current_audio_position = end_position
    else:
        outdata.fill(0)  # Çalınacak ses yoksa sessizlik gönder


def find_next_empty_track():
    for i in range(len(tracks)):
        if tracks[i] is None:
            return i
    return None


def start_recording():
    global recording, current_audio, current_track
    next_track = find_next_empty_track()
    if next_track is not None:
        recording = True
        current_track = next_track
        current_audio = []  # Yeni ses verisi için liste oluştur


def stop_recording():
    global recording, current_audio, tracks
    if recording:
        # Ses verisini numpy array'e dönüştür
        audio_data = np.concatenate(current_audio, axis=0)
        tracks[current_track] = audio_data  # Track'e ses verisini kaydet
        recording = False
    else:
        recording = False
        return


def audio_callback(indata, frames, time, status):
    if recording:
        current_audio.append(indata.copy())  # Alınan sesi listeye ekle


def play_selected_track():
    """
    Seçili track'i çalar.
    """
    global playing_audio, current_audio_position, stream
    if selected_track is not None and tracks[selected_track] is not None:
        playing_audio = tracks[selected_track]
        current_audio_position = 0

        # Akışı başlat
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
    """
    Tüm track'leri aynı anda çalar.
    """
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

        mixed_audio /= np.max(np.abs(mixed_audio))  # Normalize et
        playing_audio = mixed_audio
        current_audio_position = 0

        # Akışı başlat
        if stream is not None:
            stream.close()
        stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
        stream.start()


def adjust_volume(change):
    """
    Ses seviyesini artırır veya azaltır.
    Args:
        change (float): Ses seviyesi değişikliği (+ veya -).
    """
    global volume_level
    volume_level = max(0.0, min(1.50, volume_level + change))  # 0.0 ile 1.0 arasında sınırla



clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont("Arial", 24)

# Track Info
tracks = [None] * 10  # Max 10 Track
track_height = 50
track_spacing = 10
track_start_y = 50
selected_track = None
recording = False
current_track = None
editing_track = None
original_text = ""
playing_now = False

# Ses akışı için değişkenler
playing_audio = None
current_audio_position = 0
stream = None

# Audio save and play variables
sample_rate = 44100
current_audio = None

# Create audio stream with SoundDevice
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
stream.start()

# Ses seviyesi değişkeni
volume_level = 1.0  # Başlangıç seviyesi (tam ses)

# Ses seviyesi butonları
volumeUpButton = Button(650, 10, 40, 25, win, "+")
volumeDownButton = Button(700, 10, 40, 25, win, "-")

color1 = grey
color2 = dark_grey
color3 = "grey"

MenuButtonList = [
    # FileButton
    Button(menu_button_start_pos_x, menu_button_y_pos, menu_button_width, menu_button_height, win, "FILE", menu_button_font_size, color1),
    # EditButton
    Button(menu_button_start_pos_x+menu_button_width, menu_button_y_pos, menu_button_width, menu_button_height, win, "EDIT", menu_button_font_size, color1),
    # SaveButton 
    Button(menu_button_start_pos_x+menu_button_width*2, menu_button_y_pos, menu_button_width, menu_button_height, win, "SAVE", menu_button_font_size, color1),
    # ThemeButton
    Button(menu_button_start_pos_x+menu_button_width*3, menu_button_y_pos, menu_button_width+5, menu_button_height, win, "THEME", menu_button_font_size, color1)
]


recordButton = ImageButton(record_button_x, menu_button_y_pos, "images/record.png", win)
playButton = ImageButton(play_button_x, menu_button_y_pos, "images/play.png", win)
stopButton = ImageButton(stop_button_x, menu_button_y_pos, "images/pause.png", win)
resetButton = ImageButton(reset_button_x, menu_button_y_pos, "images/reset.png", win)


TrackRectList = [
    Button(3, 70, 167, 56, win, "Track 1", 15, "white", "black"),
    Button(3, 127, 167, 56, win, "Track 2", 15, "white", "black"),
    Button(3, 184, 167, 56, win, "Track 3", 15, "white", "black"),
    Button(3, 241, 167, 56, win, "Track 4", 15, "white", "black"),
    Button(3, 298, 167, 56, win, "Track 5", 15, "white", "black"),
    Button(3, 355, 167, 56, win, "Track 6", 15, "white", "black"),
    Button(3, 412, 167, 56, win, "Track 7", 15, "white", "black"),
    Button(3, 469, 167, 56, win, "Track 8", 15, "white", "black"),
    Button(3, 526, 167, 56, win, "Track 9", 15, "white", "black"),
    Button(3, 583, 167, 53, win, "Track 10", 15, "white", "black")
]

TrackMuteButtonList = [
    Button(110, 98, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 155, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 212, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 269, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 326, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 383, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 440, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 497, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 554, 20, 20, win, "M", 15, color1, "white"),
    Button(110, 611, 20, 20, win, "M", 15, color1, "white")
]

TrackSoloButtonList = [
    Button(132, 98, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 155, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 212, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 269, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 326, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 383, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 440, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 497, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 554, 20, 20, win, "S", 15, color1, "white"),
    Button(132, 611, 20, 20, win, "S", 15, color1, "white")
]


timeline = Timeline()

while running:
    x, y = win.get_size()
    pygame.key.set_repeat(200, 50)

    delta_time = clock.get_time() / 1000

    color1 = grey
    color2 = dark_grey
    color3 = "grey"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        pos = pygame.mouse.get_pos()
        
        timeline.handleScroll(event)  # Sadece timeline'ı kaydır
        # if not timeline.is_playing:
        timeline.handleClick(event, timeline_x, timeline_y, x, timeline_height)

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
                timeline.is_playing = True
                playing_now = True

            if stopButton.isClicked(pos):
                stop_playing()
                timeline.is_playing = False
                playing_now = False

            if resetButton.isClicked(pos):
                timeline.cursor_position = 0
                timeline.is_playing = False
                stop_playing()
                playing_now = False

            if volumeUpButton.isClicked(pos):
                adjust_volume(0.1)  # %10 artır
            if volumeDownButton.isClicked(pos):
                adjust_volume(-0.1)  # %10 azalt

            for i in range(len(tracks)):
                y = track_start_y + i * (track_height + track_spacing)
                if y <= pos[1] <= y + track_height:
                    selected_track = i  # Seçili track'i güncelle

            for button in TrackRectList:  # TrackRectList içindeki her bir butonu kontrol et
                # Yazı alanını hesapla
                text_surface = button.font.render(button.text, True, pygame.Color('black'))
                text_rect = text_surface.get_rect(topleft=button.rect.topleft)

                # Eğer mouse pozisyonu text alanına denk geliyorsa
                if text_rect.collidepoint(pos):
                    editing_track = TrackRectList.index(button)
                    original_text = button.text
                    break

        if event.type == pygame.KEYDOWN:
            if editing_track is not None:  # Düzenleme modundaysak
                if event.key == pygame.K_BACKSPACE:  # Silme işlemi
                    if len(TrackRectList[editing_track].text) > 0:
                        TrackRectList[editing_track].text = TrackRectList[editing_track].text[:-1]
                elif event.key == pygame.K_RETURN and len(TrackRectList[editing_track].text) > 0:  # Enter tuşu ile değişikliği kaydet
                    editing_track = None  # Düzenleme modundan çık
                elif event.key == pygame.K_ESCAPE:  # ESC tuşu ile eski haline dön
                    TrackRectList[editing_track].text = original_text  # Eski yazıyı geri yükle
                    editing_track = None  # Düzenleme modundan çık
                else:  # Karakter ekleme
                    if len(TrackRectList[editing_track].text) < 15:  # Maksimum 15 karakter
                        TrackRectList[editing_track].text += event.unicode

            if event.key == pygame.K_SPACE:  # Space tuşuna basınca oynatma durumu değişir
                timeline.is_playing = not timeline.is_playing
                if playing_now:
                    stop_playing()
                else:
                    play_selected_track()
            
            if event.key == pygame.K_r:
                timeline.cursor_position = 0
                timeline.is_playing = False
                stop_playing()
                playing_now = False

    timeline.update_cursor(delta_time)
                
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
    pygame.draw.rect(win, color2, menuFrameRect, gui_line_border)
    
    controlFrameRect = pygame.Rect(play_button_x, menu_button_y_pos, 25 * 3 - 1, menu_button_height)
    pygame.draw.rect(win, color2, controlFrameRect, gui_line_border)
    
    timelineFrameRect = pygame.Rect(0.5, 40, x, 599)  # Sabit değerlerle tanımla
    pygame.draw.rect(win, color2, timelineFrameRect, gui_line_border + 1)
    timeline.drawTimeline(win, timeline_x, timeline_y, x, timeline_height, tracks, sample_rate, color3, color2)

    trackFrameLine = pygame.draw.line(win, color2, (0.5, 69), (300, 69))
    text = font.render("Tracks", True, color2)
    text_rect = text.get_rect(center=(85, 55))
    win.blit(text, text_rect)

    for i in range(1, 10):
        pygame.draw.line(win, color2, (0.5, 69 + 57 * i), (170, 69 + 57 * i))

    for i, trackRect in enumerate(TrackRectList):
        if editing_track == i:
            pygame.draw.rect(win, pygame.Color('white'), trackRect.rect)  # Düzenleme sırasında beyaz arka plan
            text_surface = font.render(trackRect.text, True, pygame.Color('black'))
            win.blit(text_surface, (trackRect.rect.x + 5, trackRect.rect.y + (trackRect.rect.height - text_surface.get_height()) // 2))
        else:
            trackRect.drawLeft()           
    
    for muteButton in TrackMuteButtonList:
        pygame.draw.rect(win, color2, pygame.Rect(muteButton.rect.x - gui_line_border, muteButton.rect.y - gui_line_border, 46, 24), gui_line_border)
        pygame.draw.line(win, color2, (muteButton.rect.x + muteButton.width, muteButton.rect.y - gui_line_border), (muteButton.rect.x + muteButton.width, muteButton.rect.y + 21), gui_line_border)
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
