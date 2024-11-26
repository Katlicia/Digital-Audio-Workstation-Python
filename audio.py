import pygame
import sounddevice as sd
import numpy as np
import threading
from scipy.io.wavfile import write

recordings = {}  # Tüm kayıtları saklayan sözlük
is_recording = False
current_recording_name = None

def start_recording(sample_rate=44100, channels=2):
    global is_recording, current_recording_data
    is_recording = True
    current_recording_data = []

    def callback(indata, frames, time, status):
        if is_recording:
            current_recording_data.append(indata.copy())

    stream = sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback)
    global recording_thread
    recording_thread = threading.Thread(target=lambda: stream.start())
    recording_thread.start()
    print("Kayıt başladı.")

def stop_recording(recording_name):
    global is_recording, recordings
    if is_recording:
        is_recording = False

        # Kaydı birleştir ve bellekte sakla
        full_recording = np.concatenate(current_recording_data, axis=0)
        recordings[recording_name] = full_recording
        print(f"Kayıt '{recording_name}' başarıyla belleğe alındı.")
    else:
        print("Kayıtta değil.")

def play_recording(recording_name, sample_rate=44100):
    if recording_name in recordings:
        # Pygame Mixer için ses formatını düzenle
        audio = (recordings[recording_name] * 32767).astype(np.int16)
        pygame.mixer.init(frequency=sample_rate)
        sound = pygame.sndarray.make_sound(audio)
        sound.play()
        print(f"'{recording_name}' çalınıyor.")
    else:
        print(f"Kayıt bulunamadı: {recording_name}")

from pydub import AudioSegment

def export_recording(recording_name, filename, format="wav", sample_rate=44100):
    if recording_name in recordings:
        # WAV Formatı
        if format == "wav":
            write(filename, sample_rate, (recordings[recording_name] * 32767).astype(np.int16))
            print(f"Kayıt {filename} olarak kaydedildi.")
        # MP3 Formatı
        elif format == "mp3":
            audio = (recordings[recording_name] * 32767).astype(np.int16)
            sound = AudioSegment(audio.tobytes(), frame_rate=sample_rate, sample_width=2, channels=2)
            sound.export(filename, format="mp3")
            print(f"Kayıt {filename} olarak MP3 formatında kaydedildi.")
    else:
        print(f"Kayıt bulunamadı: {recording_name}")
