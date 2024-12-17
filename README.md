# 🎵 Digital Audio Workstation (DAW)

A custom-built, feature-rich **Digital Audio Workstation** (DAW) designed for multi-track recording, playback, and audio processing. This application allows users to record, play, mix, and apply effects to audio tracks.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Available Effects](#available-effects)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **Multi-track Recording:** Record up to 10 audio tracks simultaneously.
- **Waveform Visualization:** Visualize waveforms for each track.
- **Playback and Mixing:** Play individual tracks or mix all tracks together.
- **Undo Functionality:** Undo changes with a multi-level undo stack.
- **Import/Export Support:** Import MP3/WAV files and export your project as WAV/MP3.
- **Audio Effects:** Apply effects like reverb, delay, pitch shift, distortion, gain, and equalizer.
- **Custom Themes:** Switch between different themes for a personalized UI.
- **Volume Control:** Adjust global volume with a user-friendly interface.

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Katlicia/Digital-Audio-Workstation-Python
cd Digital-Audio-Workstation-Python
```

### 2. Install Dependencies
Make sure you have Python installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Launch the DAW by running:
```bash
python main.py
```

---

## 🚀 Usage

### 🎙️ Recording
1. Click the **Record Button** to start recording.
2. Stop recording to save the track.

### 🎧 Playback
- Use the **Play** button to play all tracks.
- Use the **Pause** or **Reset** buttons to control playback.

### 🔊 Importing Audio
- Go to the **File** menu and select **Import as WAV/MP3**.

### 💾 Saving/Loading Projects
- **Save Project:** Go to the **Save** menu.
- **Load Project:** Use the **Load Project** option under the **File** menu.

### 🎨 Theme Customization
- Open the **Theme** menu to switch between:
  - Dark
  - Light
  - Strawberry
  - Green Tea
  - Mochi
  - Sakura

---

## 📂 Project Structure

```
daw/
│
├── main.py             # Entry point of the application
├── button.py           # UI button components
├── config.py           # Application settings and theme configurations
├── timeline.py         # Timeline class for managing playback and recording
├── audio_utils.py      # Audio recording, playback, and effects utilities
├── requirements.txt    # Dependencies
├── images/             # Image assets for buttons
└── README.md           # This documentation
```

---

## 🎛️ Available Effects

| Effect       | Parameters                      | Description                        |
|--------------|--------------------------------|------------------------------------|
| **Reverb**   | Intensity, Max Length           | Adds reverb to the track           |
| **Delay**    | Delay Time, Feedback            | Adds an echo effect                |
| **Pitch Shift** | Semitones                    | Changes the pitch of the track     |
| **Distortion** | Intensity                     | Adds distortion to the audio       |
| **Gain**     | Gain                            | Adjusts the volume of the track    |
| **Equalizer**| Low Gain, Mid Gain, High Gain   | Adjusts frequency ranges           |

---

## 🧩 Dependencies

The DAW relies on the following Python libraries:
- `pygame` - For GUI and event handling.
- `pydub` - For MP3 and WAV processing.
- `numpy` - For audio array operations.
- `sounddevice` - For recording and playback.
- `librosa` - For pitch shifting.
- `scipy` - For signal processing.
- `tkinter` - For dynamic GUI.
- `pickle` - For save management system.
- `wave` - For handling wav files.


Install all dependencies via:
```bash
pip install -r requirements.txt
```

---

## 🙌 Contributing

Contributions are welcome! If you'd like to improve the DAW:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m "Add new feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

Enjoy creating music with your new **Digital Audio Workstation**! 🎶
