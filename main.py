import pygame
from button import Button, ImageButton
from config import *
import wave
from timeline import Timeline
import sounddevice as sd
import numpy as np
from pydub import AudioSegment

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
    global recording, current_audio, current_track, stream
    next_track = find_next_empty_track()
    if next_track is not None:
        recording = True
        current_track = next_track
        current_audio = []  # Yeni ses verisi için listeyi sıfırla

        # Mikrofon akışını başlat
        if stream is None or not stream.active:
            stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
            stream.start()

        # print(f"Recording started on track {current_track}.")
    else:
        print("Warning: No empty track available for recording.")

def stop_recording():
    global recording, current_audio, tracks

    if recording:
        # print(f"Stopping recording. Current audio length: {len(current_audio)}")
        if current_audio and len(current_audio) > 0:
            # Kaydedilen tüm ses verilerini birleştir ve track'e ekle
            audio_data = np.concatenate(current_audio, axis=0)
            tracks[current_track] = audio_data
            #print(f"Track {current_track} saved with length {len(audio_data)}.")
        else:
            print("Warning: No audio data recorded.")
        current_audio = []
        recording = False

        # Mikrofon akışını durdur
        if stream is not None:
            stream.stop()
    else:
        print("Recording is not active.")

def audio_callback(indata, frames, time, status):
    global current_audio
    if recording:
        # print(f"Recording is active. Frames: {frames}")
        current_audio.append(indata.copy())  # Alınan mikrofon verisini current_audio'ya ekle
    else:
        pass
        # print("Recording is inactive.")


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
    Zaman çizelgesindeki başlangıç pozisyonlarına ve cursor'un bulunduğu yere göre tüm track'leri çalar.
    """
    global playing_audio, current_audio_position, stream

    if recording:
        # print("Recording is active. Playback cannot start during recording.")
        return  # Eğer kayıt aktifse, çalma işlemini iptal et

    # Çalma işlemini devam ettir
    if any(track is not None for track in tracks):
        # Cursor'un sample cinsinden pozisyonunu hesapla
        cursor_sample_position = int(timeline.cursor_position / timeline.unit_width * sample_rate)

        # Tüm track'lerin miksleme için maksimum uzunluğunu hesapla
        max_length = max(
            int(round(timeline.track_starts[i] / timeline.unit_width * sample_rate)) + len(track)
            if track is not None else 0
            for i, track in enumerate(tracks)
        )
        max_length = max(max_length, cursor_sample_position)  # Cursor'u hesaba kat

        # Ses mikslemesi için boş bir array oluştur
        mixed_audio = np.zeros(max_length, dtype=np.float32)

        for i, track in enumerate(tracks):
            if track is not None:
                # Stereo ses ise mono'ya çevir
                if len(track.shape) > 1:
                    track = np.mean(track, axis=1)

                # Track'in zaman çizelgesindeki başlangıç pozisyonunu hesapla (sample bazında)
                track_start_in_samples = int(timeline.track_starts[i] / timeline.unit_width * sample_rate)

                # Eğer track cursor'un gerisindeyse, sadece cursor'dan sonraki kısmı miksle
                if track_start_in_samples + len(track) > cursor_sample_position:
                    start_in_track = max(0, cursor_sample_position - track_start_in_samples)
                    track_end = len(track)
                    if start_in_track < track_end:
                        start_in_mixed = max(0, track_start_in_samples - cursor_sample_position)
                        mixed_audio[start_in_mixed:start_in_mixed + (track_end - start_in_track)] += track[start_in_track:]

        # Sesleri normalize et
        if np.max(np.abs(mixed_audio)) > 0:
            mixed_audio /= np.max(np.abs(mixed_audio))

        # Mikslenmiş sesin sadece cursor pozisyonundan sonraki kısmını çal
        playing_audio = mixed_audio[cursor_sample_position:]
        current_audio_position = 0

        # Mevcut bir ses akışı varsa kapat
        if stream is not None:
            stream.close()

        # Yeni bir ses akışı başlat
        stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
        stream.start()


def export_tracks_to_file(filename="output", filetype="wav"):
    """
    Tüm track'leri miksleyip bir WAV veya MP3 dosyasına dışa aktarır.
    Args:
        filename (str): Çıkış dosyasının adı (uzantı olmadan).
        filetype (str): Çıkış formatı ("wav" veya "mp3").
    """
    if not any(track is not None for track in tracks):
        print("No tracks to export.")
        return

    # Tüm track'lerin miksleme için maksimum uzunluğunu hesapla
    max_length = max(
        int(round(timeline.track_starts[i] / timeline.unit_width * sample_rate)) + len(track)
        if track is not None else 0
        for i, track in enumerate(tracks)
    )

    # Ses mikslemesi için boş bir array oluştur
    mixed_audio = np.zeros(max_length, dtype=np.float32)

    for i, track in enumerate(tracks):
        if track is not None:
            # Stereo ses ise mono'ya çevir
            if len(track.shape) > 1:
                track = np.mean(track, axis=1)

            # Track'in zaman çizelgesindeki başlangıç pozisyonunu hesapla (sample bazında)
            track_start_in_samples = int(timeline.track_starts[i] / timeline.unit_width * sample_rate)

            # Track'i miksleme array'ine ekle
            mixed_audio[track_start_in_samples:track_start_in_samples + len(track)] += track

    # Sesleri normalize et
    if np.max(np.abs(mixed_audio)) > 0:
        mixed_audio /= np.max(np.abs(mixed_audio))

    # NumPy array'ini int16 formatına dönüştür
    output_audio = (mixed_audio * 32767).astype(np.int16)

    # Çıkış dosyası formatına göre yaz
    if filetype == "wav":
        output_file = f"{filename}.wav"
        with wave.open(output_file, "w") as wf:
            wf.setnchannels(1)  # Mono kanal
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(output_audio.tobytes())
    elif filetype == "mp3":
        output_file = f"{filename}.mp3"
        # WAV formatına geçici bir dosya yaz
        temp_wav_file = f"{filename}_temp.wav"
        with wave.open(temp_wav_file, "w") as wf:
            wf.setnchannels(1)  # Mono kanal
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(output_audio.tobytes())
        # WAV'ı MP3'e dönüştür
        audio = AudioSegment.from_wav(temp_wav_file)
        audio.export(output_file, format="mp3")
    else:
        print(f"Unsupported file type: {filetype}")
        return

    print(f"Tracks exported to {output_file}")


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

theme = darkTheme
themestr = "darkTheme"
rectcolor = theme[3] # Track, passive button color
linecolor = theme[2] # Line, active button color
wincolor = theme[4] # Win, timeline color
temptrackcolor = theme[1] # Temp track, waveform color
timelinetrackcolor = theme[0] # timelinetrack color
text_color = (255, 255, 255) # Text color

recordButton = ImageButton(record_button_x, menu_button_y_pos, "images/record.png", win)
playButton = ImageButton(play_button_x, menu_button_y_pos, f"images/{themestr}/playpassive.png", win)
stopButton = ImageButton(stop_button_x, menu_button_y_pos, f"images/{themestr}/pausepassive.png", win)
resetButton = ImageButton(reset_button_x, menu_button_y_pos, f"images/{themestr}/resetpassive.png", win)
volumeUpButton = ImageButton(volume_up_button_x, menu_button_y_pos, f"images/{themestr}/sounduppassive.png", win)
volumeDownButton = ImageButton(volume_down_button_x, menu_button_y_pos, f"images/{themestr}/sounddownpassive.png", win)

file_menu_open = False
file_menu_buttons = [
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Export as WAV", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border, menu_button_y_pos + menu_button_height * 2, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Export as MP3", font_size=15)
]

theme_menu_open = False
theme_menu_buttons = [
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Dark", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 2, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Light", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 3, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Strawberry", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 4, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Green Tea", font_size=15),
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 5, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Mochi", font_size=15), 
    Button(menu_button_start_pos_x+gui_line_border+menu_button_width*3, menu_button_y_pos + menu_button_height * 6, 150, menu_button_height, win, rectcolor, linecolor, text_color, "Sakura", font_size=15)
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


timeline = Timeline()

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

        timeline.handleScroll(event)  # Sadece timeline'ı kaydır
        timeline.handleClick(event, timeline_x, timeline_y, x, timeline_height)

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
                theme_menu_open = False  # Menü kapatıldı

            # Sonra dosya menüsü kontrolü
            elif file_menu_open:
                for file_button in file_menu_buttons:
                    if file_button.isClicked(pos):
                        if file_button.text == "Export as WAV":
                            export_tracks_to_file(filename="output", filetype="wav")
                        elif file_button.text == "Export as MP3":
                            export_tracks_to_file(filename="output", filetype="mp3")
                file_menu_open = False  # Menü kapatıldı

            # Ana menü tıklamaları
            elif MenuButtonList[0].isClicked(pos):  # File menüsü
                file_menu_open = not file_menu_open
            elif MenuButtonList[-1].isClicked(pos):  # Theme menüsü
                theme_menu_open = not theme_menu_open

            if recordButton.isClicked(pos):
                if recording:
                    stop_recording()
                    timeline.stop_timeline_recording()
                    recordButton.setImage("images/record.png")
                else:
                    start_recording()
                    timeline.start_timeline_recording(current_track)
                    recordButton.setImage("images/recording.png")

            if playButton.isClicked(pos) and recording == False:
                play_all_tracks()
                play_selected_track()
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
                adjust_volume(0.1)  # %10 artır
            if volumeDownButton.isClicked(pos):
                adjust_volume(-0.1)  # %10 azalt

            for i, solo in enumerate(TrackSoloButtonList):
                if solo.isClicked(pos):
                    if tracks[i] is not None and len(tracks[i]) > 0:
                        selected_track = i

            for button in TrackRectList:  # TrackRectList içindeki her bir butonu kontrol et
                # Yazı alanını hesapla
                text_surface = button.font.render(button.text, True, text_color)
                text_rect = text_surface.get_rect(topleft=button.rect.topleft)

                # Eğer mouse pozisyonu text alanına denk geliyorsa
                if text_rect.collidepoint(pos):
                    editing_track = TrackRectList.index(button)
                    original_text = button.text
                    break
                else:
                    editing_track = None

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
                    play_all_tracks()
            
            if event.key == pygame.K_r:
                timeline.cursor_position = 0
                timeline.is_playing = False
                stop_playing()
                playing_now = False
    wincolor = theme[4]
    win.fill(wincolor)

    width = 0
    for MenuButton in MenuButtonList:
        MenuButton.passive_color = rectcolor
        MenuButton.active_color = linecolor
        MenuButton.text_color = text_color
        MenuButton.draw()
        MenuButton.isClicked(pos)
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


    menuFrameRect = pygame.Rect(menu_button_start_pos_x, menu_button_y_pos, width + 2.5, menu_button_height)
    pygame.draw.rect(win, linecolor, menuFrameRect, gui_line_border)
    
    volumeFrameRect = pygame.Rect(volume_up_button_x, menu_button_y_pos, 25 * 2 - 1, menu_button_height)
    pygame.draw.rect(win, linecolor, volumeFrameRect, gui_line_border)

    controlFrameRect = pygame.Rect(play_button_x, menu_button_y_pos, 25 * 3 - 1, menu_button_height)
    pygame.draw.rect(win, linecolor, controlFrameRect, gui_line_border)
    
    timelineFrameRect = pygame.Rect(0.5, 40, x, 599)  # Sabit değerlerle tanımla
    pygame.draw.rect(win, linecolor, timelineFrameRect, gui_line_border + 1)
    timeline.drawTimeline(win, timeline_x, timeline_y, x, timeline_height, tracks, sample_rate, rectcolor, linecolor, temptrackcolor, timelinetrackcolor, temptrackcolor)

    trackFrameLine = pygame.draw.line(win, linecolor, (0.5, 69), (300, 69))
    text = font.render("Tracks", True, text_color)
    text_rect = text.get_rect(center=(85, 55))
    win.blit(text, text_rect)

    for i in range(1, 10):
        pygame.draw.line(win, linecolor, (0.5, 69 + 57 * i), (170, 69 + 57 * i))

    for i, trackRect in enumerate(TrackRectList):
        trackRect.passive_color = rectcolor
        trackRect.active_color = linecolor
        trackRect.text_color = text_color
        if editing_track == i:
            pygame.draw.rect(win, trackRect.passive_color, trackRect.rect)  # Düzenleme sırasında beyaz arka plan
            text_surface = font.render(trackRect.text, True, text_color)
            win.blit(text_surface, (trackRect.rect.x + 5, trackRect.rect.y + (trackRect.rect.height - text_surface.get_height()) // 2))
        else:
            trackRect.drawLeft()           
    
    for muteButton in TrackMuteButtonList:
        muteButton.passive_color = rectcolor
        muteButton.active_color = linecolor
        muteButton.text_color = text_color
        pygame.draw.rect(win, linecolor, pygame.Rect(muteButton.rect.x - gui_line_border, muteButton.rect.y - gui_line_border, 46, 24), gui_line_border)
        pygame.draw.line(win, linecolor, (muteButton.rect.x + muteButton.width, muteButton.rect.y - gui_line_border), (muteButton.rect.x + muteButton.width, muteButton.rect.y + 21), gui_line_border)
        muteButton.draw()
        muteButton.isClicked(pos)

    for soloButton in TrackSoloButtonList:
        soloButton.passive_color = rectcolor
        soloButton.active_color = linecolor
        soloButton.text_color = text_color
        soloButton.draw()
        soloButton.isClicked(pos)

    if file_menu_open:
        for file_button in file_menu_buttons:
            file_button.passive_color = rectcolor
            file_button.active_color = linecolor
            file_button.draw()

    if theme_menu_open:
        for theme_button in theme_menu_buttons:
            theme_button.passive_color = rectcolor
            theme_button.active_color = linecolor
            theme_button.draw()
    
    pygame.display.update()
    
    clock.tick(144)

pygame.quit()
