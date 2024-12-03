import pygame
from button import Button, ImageButton
from config import *
from timeline2 import Timeline
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


def draw_tracks(win, tracks, selected_track):
    for i, track in enumerate(tracks):
        y = track_start_y + i * (track_height + track_spacing)
        color = (135, 206, 250) if i == selected_track else (59, 59, 59)
        pygame.draw.rect(win, color, (50, y, 700, track_height))
        
        if track is not None:  # Eğer track doluysa
            pygame.draw.rect(win, (100, 149, 237), (50, y, 700, track_height))
            font = pygame.font.Font(None, 24)
            text = font.render(f"Track {i + 1}", True, "white")
            win.blit(text, (60, y + 15))  # Track ismi


def start_recording():
    global recording, current_audio, current_track
    next_track = find_next_empty_track()
    if next_track is not None:
        recording = True
        current_track = next_track
        current_audio = []  # Yeni ses verisi için liste oluştur


def stop_recording():
    global recording, current_audio, tracks, timeline

    if recording:
        if current_audio:  # Liste boş değilse işlemi yap
            # Ses verisini numpy array'e dönüştür
            audio_data = np.concatenate(current_audio, axis=0)

            # Track'e ses verisini kaydet
            tracks[current_track] = audio_data

            # Track süresini hesapla (saniye)
            track_duration = len(audio_data) / sample_rate

            # Timeline üzerinde gösterilecek uzunluğu hesapla
            track_pixel_width = track_duration * timeline.unit_width

            # Timeline'a track ekle
            timeline.addTrack(current_track, track_pixel_width)
        else:
            print("Kaydedilecek ses verisi yok.")

        recording = False




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

def draw_recording_list(win, recordings):
    font = pygame.font.Font(None, 36)
    y = 50
    for name in recordings.keys():
        text_surface = font.render(name, True, "black")
        win.blit(text_surface, (50, y))
        y += 40


clock = pygame.time.Clock()
running = True

# Track Info
tracks = [None] * 10  # Max 10 Track
track_height = 50
track_spacing = 10
track_start_y = 50
selected_track = None
recording = False
current_track = None



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

timeline = Timeline()


while running:
    x, y = win.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        pos = pygame.mouse.get_pos()
        
        timeline.handleScroll(event)  # Sadece timeline'ı kaydır

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

    timeline.handleKeyboard()

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
    timelineFrameRect = pygame.Rect(width + 2.5, 67, x, 507)  # Sabit değerlerle tanımla
    pygame.draw.rect(win, dark_grey, timelineFrameRect, gui_line_border + 1)
    timeline.drawTimeline(win, width + 5, 70, x, 500)
    timeline.drawTracks(win, width + 5, 70)
    timeline.drawCursor(win, width + 5, 70, 500)
    volumeUpButton.draw()
    volumeDownButton.draw()

    pygame.display.update()
    
pygame.quit()
