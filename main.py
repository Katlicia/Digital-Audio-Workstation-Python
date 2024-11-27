import pygame
from button import *
from config import *
from audio import *

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Digital Audio Workstation")

clock = pygame.time.Clock()
running = True

######################

# Track bilgileri
tracks = [None] * 10  # Maksimum 10 track
track_height = 50
track_spacing = 10
track_start_y = 50
selected_track = None
recording = False
current_track = None

# Ses kaydetme ve çalma değişkenleri
sample_rate = 44100
current_audio = None

# Butonlar
recordButton = Button(50, 10, 100, 30, win, "Record", font_size=20, color=(135, 206, 250))
playButton = Button(200, 10, 100, 30, win, "Play", font_size=20, color=(100, 149, 237))
stopButton = Button(350, 10, 100, 30, win, "Stop", font_size=20, color=(255, 0, 0))
playAllButton = Button(550, 10, 100, 30, win, "Play All", font_size=20, color=(255, 0, 0))

def find_next_empty_track():
    """
    Boş olan ilk track'i bulur.
    """
    for i in range(len(tracks)):
        if tracks[i] is None:
            return i
    return None


def draw_tracks(win, tracks, selected_track):
    """
    Track'leri ekrana çizer.
    """
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
    """
    Kayıt işlemini başlatır.
    """
    global recording, current_audio, current_track
    next_track = find_next_empty_track()
    if next_track is not None:
        recording = True
        current_track = next_track
        current_audio = []  # Yeni ses verisi için liste oluştur


def stop_recording():
    """
    Kayıt işlemini durdurur.
    """
    global recording, current_audio, tracks
    if recording:
        # Ses verisini numpy array'e dönüştür
        audio_data = np.concatenate(current_audio, axis=0)
        tracks[current_track] = audio_data  # Track'e ses verisini kaydet
        recording = False


def audio_callback(indata, frames, time, status):
    """
    Ses kaydı sırasında çağrılan callback.
    """
    if recording:
        current_audio.append(indata.copy())  # Alınan sesi listeye ekle


def play_selected_track():
    """
    Seçili track'i çalar.
    """
    if selected_track is not None and tracks[selected_track] is not None:
        sd.play(tracks[selected_track], samplerate=sample_rate)


def stop_playing():
    """
    Çalan tüm sesleri durdurur.
    """
    sd.stop()

def play_all_tracks():
    """
    Tüm track'leri aynı anda çalar.
    """
    if any(track is not None for track in tracks):  # En az bir track doluysa
        # En uzun track'in uzunluğunu bul
        max_length = max(len(track) for track in tracks if track is not None)
        
        # Track'leri hizala ve karıştır
        mixed_audio = np.zeros(max_length, dtype=np.float32)
        for track in tracks:
            if track is not None:
                # Track'in mono olup olmadığını kontrol et
                if len(track.shape) > 1:  # Stereo ise
                    track = np.mean(track, axis=1)  # Kanalları birleştirerek mono'ya çevir
                padded_track = np.pad(track, (0, max_length - len(track)), 'constant')  # Kısa track'leri doldur
                mixed_audio[:len(padded_track)] += padded_track  # Toplama işlemi

        # Karışımı normalize et (aşırı yüksek sesleri engellemek için)
        max_val = np.max(np.abs(mixed_audio))  # En yüksek ses değeri
        if max_val > 0:  # Bölme hatalarını önlemek için kontrol
            mixed_audio /= max_val

        # Tüm track'leri çal
        sd.play(mixed_audio, samplerate=sample_rate)



# SoundDevice ile ses akışı oluştur
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
stream.start()

######################

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
        
        ######################
        if event.type == pygame.MOUSEBUTTONDOWN:
            if recordButton.isClicked(pos):
                if recording:
                    stop_recording()
                else:
                    start_recording()

            if playButton.isClicked(pos):
                play_selected_track()

            if stopButton.isClicked(pos):
                stop_playing()
            
            if playAllButton.isClicked(pos):
                play_all_tracks()

            # Track'e tıklama
            for i in range(len(tracks)):
                y = track_start_y + i * (track_height + track_spacing)
                if y <= pos[1] <= y + track_height:
                    selected_track = i  # Seçili track'i güncelle
        ######################

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

    # Track'leri çiz
    draw_tracks(win, tracks, selected_track)

    # Düğmeleri çiz
    recordButton.draw()
    playButton.draw()
    stopButton.draw()
    playAllButton.draw()

    # recordButton.draw()
    # stopButton.draw()
    # playButton.draw()
    # exportButton.draw()
    # draw_recording_list(win, recordings)
    

    pygame.display.update()
    
pygame.quit()
