import threading
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

# Kaydedilecek verileri tutacak liste
recording_data = []
is_recording = False  # Kayıt durumu
recording_thread = None  # Kayıt işlemi için thread

def start_recording(sample_rate=44100, channels=2):
    """
    Ses kaydını başlatır.
    Args:
        sample_rate (int): Ses örnekleme hızı.
        channels (int): Ses kanalı sayısı.
    """
    global recording_data, is_recording
    is_recording = True
    recording_data = []

    def callback(indata, frames, time, status):
        if is_recording:  # Eğer kayıt devam ediyorsa
            recording_data.append(indata.copy())  # Veriyi buffer'a ekle

    def record_loop():
        global is_recording
        with sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback):
            while is_recording:
                sd.sleep(100)  # Kısa bir gecikme ile döngü devam eder
    
    # Kayıt işlemini ayrı bir thread'de başlat
    global recording_thread
    recording_thread = threading.Thread(target=record_loop)
    recording_thread.start()
    print("Kayıt başladı...")

def stop_recording(filename="output.wav", sample_rate=44100):
    """
    Ses kaydını durdurur ve WAV dosyasına yazar.
    Args:
        filename (str): Kaydedilecek dosyanın adı.
        sample_rate (int): Ses örnekleme hızı.
    """
    global is_recording, recording_data, recording_thread
    is_recording = False

    if recording_thread:
        recording_thread.join()  # Thread'in bitmesini bekle
        print("Kayıt durduruldu.")

    # Kaydedilen verileri birleştir
    if recording_data:
        full_recording = np.concatenate(recording_data, axis=0)
        print("Dosya kaydediliyor...")
        write(filename, sample_rate, (full_recording * 32767).astype(np.int16))
        print(f"Kayıt başarıyla {filename} dosyasına kaydedildi.")
