import wave
import numpy as np
import sounddevice as sd
from pydub import AudioSegment

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
        self.selected_track = None
        self.timeline = None

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
            else:
                print("Warning: No audio data recorded.")
            self.current_audio = []
            self.recording = False

            if self.stream is not None:
                self.stream.stop()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.current_audio.append(indata.copy())

    def play_selected_track(self):
        if self.selected_track is not None and self.tracks[self.selected_track] is not None:
            self.playing_audio = self.tracks[self.selected_track]
            self.current_audio_position = 0

            if self.stream is not None:
                self.stream.close()
            self.stream = sd.OutputStream(callback=self.audio_playback_callback, samplerate=self.sample_rate, channels=1)
            self.stream.start()

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

            for i, track in enumerate(self.tracks):
                if track is not None:
                    if len(track.shape) > 1:
                        track = np.mean(track, axis=1)

                    track_start_in_samples = int(self.timeline.track_starts[i] / self.timeline.unit_width * self.sample_rate)

                    if track_start_in_samples + len(track) > cursor_sample_position:
                        start_in_track = max(0, cursor_sample_position - track_start_in_samples)
                        track_end = len(track)
                        if start_in_track < track_end:
                            start_in_mixed = max(0, track_start_in_samples - cursor_sample_position)
                            mixed_audio[start_in_mixed:start_in_mixed + (track_end - start_in_track)] += track[start_in_track:]

            if np.max(np.abs(mixed_audio)) > 0:
                mixed_audio /= np.max(np.abs(mixed_audio))

            self.playing_audio = mixed_audio[cursor_sample_position:]
            self.current_audio_position = 0

            if self.stream is not None:
                self.stream.close()
            self.stream = sd.OutputStream(callback=self.audio_playback_callback, samplerate=self.sample_rate, channels=1)
            self.stream.start()

    def export_tracks_to_file(self, filename="output", filetype="wav"):
        if not any(track is not None for track in self.tracks):
            print("No tracks to export.")
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

        if filetype == "wav":
            output_file = f"{filename}.wav"
            with wave.open(output_file, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(output_audio.tobytes())
        elif filetype == "mp3":
            temp_wav_file = f"{filename}_temp.wav"
            with wave.open(temp_wav_file, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(output_audio.tobytes())
            audio = AudioSegment.from_wav(temp_wav_file)
            audio.export(f"{filename}.mp3", format="mp3")
        else:
            print(f"Unsupported file type: {filetype}")
            return

        print(f"Tracks exported to {filename}.{filetype}")

    def adjust_volume(self, change):
        self.volume_level = max(0.0, min(1.50, self.volume_level + change))
