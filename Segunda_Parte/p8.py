import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

# --- Helper Functions ---
def butter_bandpass(lowcut, highcut, fs, order=6):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
    return b, a

def butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    b, a = butter(order, cutoff/nyq, btype='low')
    return b, a

def plot_fft(signal, fs, title, xlim=None):
    S = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(S), 1/fs)
    mask = freqs >= 0
    plt.figure(figsize=(6,3))
    plt.plot(freqs[mask], np.abs(S[mask]) / len(S))
    plt.title(title)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    if xlim:
        plt.xlim(xlim)
    plt.tight_layout()
    plt.show()

# --- Setup Paths ---
base_dir = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
audio_files = ['audio1.wav', 'audio2.wav', 'audio3.wav']
audio_paths = [os.path.join(base_dir, f) for f in audio_files]

# --- Read and Normalize ---
messages = []
fs = None
for path in audio_paths:
    sr, data = wavfile.read(path)
    fs = sr  # assume same sample rate for all
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(float) / np.max(np.abs(data))
    messages.append(data)

# --- Align lengths by truncating to the shortest message ---
min_len = min(len(m) for m in messages)
messages = [m[:min_len] for m in messages]
t = np.arange(min_len) / fs  # time vector

# --- Carrier freqs and bands ---
fc = [10.5e3, 13.5e3, 16.5e3]
bands = [(9e3, 12e3), (12e3, 15e3), (15e3, 18e3)]

# --- Modulation and FFT plots ---
modulated = []
for idx, m in enumerate(messages):
    carrier = np.cos(2 * np.pi * fc[idx] * t)
    s = m * carrier
    modulated.append(s)
    plot_fft(s, fs, f'Modulated Station {idx+1}', xlim=bands[idx])

# --- Sum signals and plot FFT ---
s_sum = sum(modulated)
plot_fft(s_sum, fs, 'Sum of Stations', xlim=(0, fs/2))

# --- Receiver: bandpass, demod, lowpass ---
lp_cutoff = 3e3
for idx in range(3):
    b_bp, a_bp = butter_bandpass(bands[idx][0], bands[idx][1], fs)
    extracted = filtfilt(b_bp, a_bp, s_sum)
    plot_fft(extracted, fs, f'Extracted Station {idx+1}', xlim=bands[idx])

    carrier = np.cos(2 * np.pi * fc[idx] * t)
    demod_raw = extracted * carrier
    b_lp, a_lp = butter_lowpass(lp_cutoff, fs)
    demod = filtfilt(b_lp, a_lp, demod_raw)
    plot_fft(demod, fs, f'Demodulated Station {idx+1}', xlim=(0, lp_cutoff))

    wavfile.write(os.path.join(base_dir, f'demod_station{idx+1}.wav'),
                  fs, (demod * 32767).astype(np.int16))

plt.show()

from scipy.io import wavfile
from IPython.display import Audio, display

# Paths to demodulated audio files
files = ['demod_station1.wav', 'demod_station2.wav', 'demod_station3.wav']

for i, file in enumerate(files, 1):
    sr, data = wavfile.read(file)
    print(f"Playback Demodulated Station {i}:")
    display(Audio(data, rate=sr))
