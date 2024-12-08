import sounddevice as sd
import numpy as np

# Ses İşlemleri Değişkenleri
sample_rate = 44100
tracks = [None] * 10
current_audio = []
recording = False
playing_audio = None
current_audio_position = 0
volume_level = 1.0
stream = None
track_height = 50
track_spacing = 10
track_start_y = 50
selected_track = None
recording = False
current_track = None

def initialize_audio_stream():
    """
    Giriş akışını başlatır.
    """
    global stream
    stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
    stream.start()

def close_audio_stream():
    """
    Ses akışlarını temizler.
    """
    global stream
    if stream is not None:
        stream.stop()
        stream.close()

def audio_callback(indata, frames, time, status):
    """
    Kayıt sırasında çağrılır.
    """
    global recording, current_audio
    if recording:
        current_audio.append(indata.copy())

def start_recording():
    """
    Yeni bir ses kaydı başlatır.
    """
    global recording, current_audio
    recording = True
    current_audio = []

def stop_recording():
    """
    Kaydı durdurur ve kaydedilen ses verisini saklar.
    """
    global recording, current_audio, tracks
    if recording:
        audio_data = np.concatenate(current_audio, axis=0) if current_audio else None
        if audio_data is not None:
            for i, track in enumerate(tracks):
                if track is None:
                    tracks[i] = audio_data
                    break
        recording = False

def play_selected_track():
    """
    Seçili track'i çalar.
    """
    global playing_audio, current_audio_position, stream
    if tracks[0] is not None:
        playing_audio = tracks[0]
        current_audio_position = 0
        if stream is not None:
            stream.close()
        stream = sd.OutputStream(callback=audio_playback_callback, samplerate=sample_rate, channels=1)
        stream.start()

def adjust_volume(change):
    """
    Ses seviyesini artırır veya azaltır.
    """
    global volume_level
    volume_level = max(0.0, min(1.50, volume_level + change))

def audio_playback_callback(outdata, frames, time, status):
    """
    Çalma sırasında ses akışı için callback fonksiyonu.
    """
    global playing_audio, current_audio_position, volume_level
    if playing_audio is not None:
        end_position = current_audio_position + frames
        audio_chunk = playing_audio[current_audio_position:end_position]
        audio_chunk *= volume_level
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

def stop_playing():
    global playing_audio, stream
    playing_audio = None
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None