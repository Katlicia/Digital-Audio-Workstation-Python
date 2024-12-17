import os
import pickle
import time
import wave
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from tkinter import filedialog, messagebox
import tkinter as tk
import librosa
from scipy.signal import fftconvolve

from config import MAX_UNDO_STACK_SIZE

class AudioManager:
    def __init__(self, sample_rate=44100, max_tracks=10):
        self.sample_rate = sample_rate
        self.tracks = [None] * max_tracks
        self.playing_audio = None
        self.current_audio_position = 0
        self.volume_level = 1.0
        self.recording = False
        self.current_audio = []
        self.current_track = None
        self.stream = None
        self.timeline = None
        self.muted_tracks = [False] * max_tracks
        self.solo_tracks = [False] * max_tracks
        self.loaded_from_file = [False] * max_tracks
        self.track_fx = [[] for _ in range(10)]
        self.is_dirty = False  # Checks if changed from last save
        self.current_file_path = None  # Saved file path
        self.save_feedback = None
        self.undo_stack = []

    def audio_playback_callback(self, outdata, frames, time, status):
        if self.playing_audio is not None:
            end_position = self.current_audio_position + frames
            audio_chunk = self.playing_audio[self.current_audio_position:end_position]
            audio_chunk = audio_chunk * self.volume_level

            if len(audio_chunk.shape) == 1:
                audio_chunk = audio_chunk[:, np.newaxis]

            if len(audio_chunk) < frames:
                outdata[:len(audio_chunk)] = audio_chunk
                outdata[len(audio_chunk):] = 0
                self.playing_audio = None
            else:
                outdata[:] = audio_chunk

            self.current_audio_position = end_position
        else:
            outdata.fill(0)

    def find_next_empty_track(self):
        for i in range(len(self.tracks)):
            if self.tracks[i] is None:
                return i
        return None

    def start_recording(self):
        next_track = self.find_next_empty_track()
        if next_track is not None:
            self.recording = True
            self.save_state()
            self.current_track = next_track
            self.current_audio = []

            if self.stream is None or not self.stream.active:
                self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.sample_rate)
                self.stream.start()
        else:
            print("Warning: No empty track available for recording.")

    def stop_recording(self):
        if self.recording:
            if self.current_audio and len(self.current_audio) > 0:
                audio_data = np.concatenate(self.current_audio, axis=0)
                self.tracks[self.current_track] = audio_data
                self.mark_dirty()
                self.timeline.reset_waveform_cache(self.current_track)
            else:
                print("Warning: No audio data recorded.")
            self.current_audio = []
            self.recording = False
            if self.stream is not None:
                self.stream.stop()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.current_audio.append(indata.copy())

    def stop_playing(self):
        self.playing_audio = None
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def play_all_tracks(self):
        if self.recording:
            return

        if any(track is not None for track in self.tracks):
            cursor_sample_position = int(self.timeline.cursor_position / self.timeline.unit_width * self.sample_rate)

            max_length = max(
                int(round(self.timeline.track_starts[i] / self.timeline.unit_width * self.sample_rate)) + len(track)
                if track is not None else 0
                for i, track in enumerate(self.tracks)
            )
            max_length = max(max_length, cursor_sample_position)

            mixed_audio = np.zeros(max_length, dtype=np.float32)

            # Solo control
            solo_active = any(self.solo_tracks)

            for i, track in enumerate(self.tracks):
                if track is not None:
                    if solo_active and not self.solo_tracks[i]:
                        continue  # If solo exists, play only the solo audio
                    if not solo_active and self.muted_tracks[i]:
                        continue  # If solo doesn't exist, skip muted tracks

                    track = np.squeeze(track)

                    track_start_in_samples = int(self.timeline.track_starts[i] / self.timeline.unit_width * self.sample_rate)
                    start_in_track = max(0, cursor_sample_position - track_start_in_samples)
                    start_in_mixed = max(0, track_start_in_samples - cursor_sample_position)

                    # Minimum uzunlukta ekleme yap
                    remaining_track_length = len(track[start_in_track:])
                    remaining_mixed_length = len(mixed_audio[start_in_mixed:])
                    length_to_add = min(remaining_track_length, remaining_mixed_length)

                    if length_to_add > 0:
                        mixed_audio[start_in_mixed:start_in_mixed + length_to_add] += track[start_in_track:start_in_track + length_to_add]

            # if np.max(np.abs(mixed_audio)) > 0:
            #     mixed_audio /= np.max(np.abs(mixed_audio))

            self.playing_audio = mixed_audio[cursor_sample_position:]
            self.current_audio_position = 0

            if self.stream is not None:
                self.stream.close()
            self.stream = sd.OutputStream(callback=self.audio_playback_callback, samplerate=self.sample_rate, channels=1)
            self.stream.start()

    def export_tracks_to_file(self):

        if all(track is None for track in self.tracks):
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Export Warning", "There are no tracks to export!")
            return

        if not any(track is not None for track in self.tracks):
            return

        max_length = max(
            int(round(self.timeline.track_starts[i] / self.timeline.unit_width * self.sample_rate)) + len(track)
            if track is not None else 0
            for i, track in enumerate(self.tracks)
        )

        mixed_audio = np.zeros(max_length, dtype=np.float32)

        for i, track in enumerate(self.tracks):
            if track is not None:

                if len(track.shape) > 1:
                    track = np.mean(track, axis=1)

                track_start_in_samples = int(self.timeline.track_starts[i] / self.timeline.unit_width * self.sample_rate)
                mixed_audio[track_start_in_samples:track_start_in_samples + len(track)] += track

        if np.max(np.abs(mixed_audio)) > 0:
            mixed_audio /= np.max(np.abs(mixed_audio))

        output_audio = (mixed_audio * 32767).astype(np.int16)

        # Tkinter file dialog for saving the file
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window

        # Ask the user for the file name and format
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")],
            title="Export As",
            initialfile="Untitled"
        )

        if not file_path:  # If user cancels
            return

        filetype = file_path.split('.')[-1].lower()  # Determine the file type by extension

        if filetype == "wav":
            with wave.open(file_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(output_audio.tobytes())
        elif filetype == "mp3":
            temp_wav_file = file_path.replace(".mp3", "_temp.wav")
            try:
                with wave.open(temp_wav_file, "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(output_audio.tobytes())
                audio = AudioSegment.from_wav(temp_wav_file)
                audio.export(file_path, format="mp3")
            finally:
                # Remove the temp file
                if os.path.exists(temp_wav_file):
                    os.remove(temp_wav_file)
                    print(f"Temporary file {temp_wav_file} deleted.")
        else:
            print(f"Unsupported file type: {filetype}")
            return

        print(f"Tracks exported to {file_path}")

    def adjust_volume(self, change):
        self.volume_level = round(max(0.0, min(1.50, self.volume_level + change)), 2)
        self.mark_dirty()

    def load_audio_file(self, file_path, track_index):
        """
        Loads an audio file to the next empty track.
        Args:
            file_path (str): File path of the desired audio.
        """
        try:
            # Load MP3 or WAV file
            if file_path.endswith(".mp3"):
                audio = AudioSegment.from_mp3(file_path)
            elif file_path.endswith(".wav"):
                audio = AudioSegment.from_wav(file_path)
            else:
                print("Unsupported file format. Only MP3 and WAV are supported.")
                return

            #Convert pydub data to numpy array.
            audio = audio.set_frame_rate(self.sample_rate).set_channels(1)
            samples = np.array(audio.get_array_of_samples(), dtype=np.float16) / 32768.0
            self.save_state()

            # Load to track.
            self.tracks[track_index] = samples
            self.loaded_from_file[track_index] = True
            self.mark_dirty()
            self.timeline.reset_waveform_cache(track_index)
        except Exception as e:
            print(f"Error loading audio file: {e}")

    def delete_track(self, track_index):
        """
        Deletes the specified track and resets its data.
        """
        if 0 <= track_index < len(self.tracks):
            self.tracks[track_index] = None # Clear audio data
            self.timeline.track_starts[track_index] = 0 # Clear start position on timeline
            self.muted_tracks[track_index] = False
            self.solo_tracks[track_index] = False
            self.mark_dirty()
            self.save_state()
            self.timeline.reset_waveform_cache(track_index)
        else:
            print("Invalid track.")

    def apply_volume(self, track, gain=1.0):
        track = np.squeeze(track).astype(np.float32)
        track_with_gain = track * gain
        track_with_gain = np.clip(track_with_gain, -1.0, 1.0)
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return track_with_gain

    # Equalizer (Low, Mid, High Frequencies)
    def apply_equalizer(self, track, low_gain=1.0, mid_gain=1.0, high_gain=1.0):
        from scipy.signal import butter, sosfilt
        def bandpass_filter(data, lowcut, highcut):
            sos = butter(10, [lowcut / (0.5 * self.sample_rate), highcut / (0.5 * self.sample_rate)], btype='band', output='sos')
            return sosfilt(sos, data)
        track = np.squeeze(track)
        low = bandpass_filter(track, 20, 300) * low_gain
        mid = bandpass_filter(track, 300, 3000) * mid_gain
        high = bandpass_filter(track, 3000, 20000) * high_gain
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return low + mid + high

    # Reverb Effect
    def apply_reverb(self, track, intensity=0.3, max_length=2.0):
        track = np.squeeze(track).astype(np.float32)
        track_max = np.max(np.abs(track)) if np.max(np.abs(track)) > 0 else 1.0
        track = track / track_max 
        max_decay_samples = int(self.sample_rate * max_length)
        decay = np.linspace(1, 0, max_decay_samples, dtype=np.float32)
        decay /= np.sum(decay)
        reverberated = fftconvolve(track, decay, mode="full")[:len(track)]
        output = (1 - intensity) * track + (intensity * reverberated)
        output = np.clip(output, -1.0, 1.0)
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return output

    # Delay Effect
    def apply_delay(self, track, delay_time=0.3, feedback=0.5):
        track = np.squeeze(track)   # 1 Dimensional
        delay_samples = int(delay_time * self.sample_rate)
        delayed_track = np.zeros(len(track) + delay_samples, dtype=np.float32)
        delayed_track[:len(track)] += track
        delayed_track[delay_samples:] += track * feedback
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return delayed_track[:len(track)]

    # Pitch
    def apply_pitch_shift(self, track, semitones=0):
        track = np.squeeze(track)  # 1 Dimensional
        if len(track) < 2048:
            n_fft = len(track)  # Use a n_fft no larger than the track length
        else:
            n_fft = 2048
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return librosa.effects.pitch_shift(track, sr=self.sample_rate, n_steps=semitones, n_fft=n_fft)

    # Distortion Effect
    def apply_distortion(self, track, intensity=2.0):
        self.mark_dirty()
        self.save_state()
        self.timeline.reset_waveform_cache(self.current_track)
        return np.tanh(track * intensity)
    

    def mark_dirty(self):
        self.is_dirty = True

    def save_project(self, TrackRectList):
        if self.current_file_path:
            self._save_to_path(self.current_file_path, TrackRectList)
        else:
            self._save_as_new(TrackRectList)

    def _save_as_new(self, TrackRectList):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".daw",
            filetypes=[("DAW Project Files", "*.daw")],
            initialfile="Untitled",
            title="Save Project"
        )
        if file_path:
            self.current_file_path = file_path
            self._save_to_path(file_path, TrackRectList)
            self.save_feedback = (f"Project saved.", time.time())

    def _save_to_path(self, file_path, TrackRectList):
        try:
            with open(file_path, 'wb') as f:
                project_data = {
                    "tracks": self.tracks,
                    "muted_tracks": self.muted_tracks,
                    "solo_tracks": self.solo_tracks,
                    "track_fx": self.track_fx,
                    "track_names": [track.text for track in TrackRectList]
                }
                pickle.dump(project_data, f)
            self.is_dirty = False
            self.save_feedback = (f"Project saved.", time.time())
        except Exception as e:
            self.save_feedback = (f"Error saving project: {e}", time.time())
            print(f"Error saving project: {e}")

    def load_project(self, TrackRectList):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("DAW Project Files", "*.daw")],
            title="Load Project"
        )
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    project_data = pickle.load(f)
                    self.tracks = project_data["tracks"]
                    self.muted_tracks = project_data["muted_tracks"]
                    self.solo_tracks = project_data["solo_tracks"]
                    self.track_fx = project_data["track_fx"]

                    # Track Names
                    loaded_track_names = project_data.get("track_names", [])
                    for i, track_name in enumerate(loaded_track_names):
                        if i < len(TrackRectList):
                            TrackRectList[i].text = track_name
                    
                    self.current_file_path = file_path 
                    self.is_dirty = False
            except Exception as e:
                messagebox.showerror("Error", f"Error loading project: {e}")
                print(f"Error loading project: {e}")

    def save_state(self):
        state = {
            "tracks": [track.copy() if track is not None else None for track in self.tracks],
            "muted_tracks": self.muted_tracks[:],
            "solo_tracks": self.solo_tracks[:],
            "track_fx": [fx_list[:] for fx_list in self.track_fx]
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > MAX_UNDO_STACK_SIZE:
            self.undo_stack.pop(0)
    
    def undo(self):
        if self.undo_stack:
            last_state = self.undo_stack.pop()
            self.tracks = last_state["tracks"]
            self.muted_tracks = last_state["muted_tracks"]
            self.solo_tracks = last_state["solo_tracks"]
            self.track_fx = last_state["track_fx"]
        else:
            print("Undo stack is empty. Nothing to undo.")

    def is_project_empty(self):
        """
        Checks if the project has no tracks or data.
        """
        return all(track is None for track in self.tracks)
