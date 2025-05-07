import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import butter, lfilter
from IPython.display import Audio, display

def plot_fft(sinal, fs, title_suffix=""):
    """
    Plota FFT de um sinal.
    """
    N = len(sinal)
    freqs = np.fft.fftfreq(N, d=1/fs)[:N//2]
    fft_vals = np.abs(np.fft.fft(sinal))[:N//2]
    plt.figure(figsize=(8,4))
    plt.stem(freqs, fft_vals, basefmt=" ")
    plt.title(f"FFT {title_suffix}")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.xlim(0, 2000)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 1) Gravação
fs = 44100         # Hz
duration = 3.0     # segundos
print("Gravando por", duration, "s...")
sinal_bruto = sd.rec(int(duration*fs), samplerate=fs, channels=1, dtype='float32')
sd.wait()
sinal_bruto = sinal_bruto.ravel()  # vetor 1D

# tempo para domínio do tempo
t = np.arange(len(sinal_bruto)) / fs

# 2) Plot do sinal no domínio do tempo (primeiros 20 ms)
plt.figure(figsize=(8,3))
plt.plot(t, sinal_bruto, linewidth=0.5)
plt.title("Sinal Gravado — Domínio do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.xlim(0, 3)
plt.grid(True)
plt.tight_layout()
plt.show()

# 3) FFT do sinal bruto
plot_fft(sinal_bruto, fs, "– Sinal Gravado (bruto)")

# 4) Projeta e aplica o filtro passa-baixas
fc = 500
b, a = butter(N=2, Wn=fc/(fs/2), btype='low')
sinal_filtrado = lfilter(b, a, sinal_bruto)

# Plot do sinal filtrado no tempo (primeiros 20 ms)
plt.figure(figsize=(8,3))
plt.plot(t, sinal_filtrado, linewidth=0.5)
plt.title("Sinal Filtrado — Domínio do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.xlim(0, 0.02)
plt.grid(True)
plt.tight_layout()
plt.show()

# 5) FFT do sinal filtrado
plot_fft(sinal_filtrado, fs, "– Sinal Filtrado (fc=500 Hz)")

# 6) Reprodução de áudio
print("▶️ Áudio original:")
display(Audio(sinal_bruto, rate=fs))
print("▶️ Áudio filtrado:")
display(Audio(sinal_filtrado, rate=fs))
