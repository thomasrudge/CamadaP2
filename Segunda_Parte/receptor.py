import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# dicionário de acordes (mesmo do emissor)
CHORDS = {
    'Do maior':       [523.25, 659.25, 783.99],
    'Re menor':       [587.33, 698.46, 880.00],
    'Mi menor':       [659.25, 783.99, 987.77],
    'Fa maior':       [698.46, 880.00, 1046.50],
    'Sol maior':      [783.99, 987.77, 1174.66],
    'La menor':       [880.00, 1046.50, 1318.51],
    'Si bemol menor': [493.88, 587.33, 698.46]
}

FS = 44100       # taxa de amostragem do receptor (Hz)
DURATION = 3.0   # duração de gravação (s)


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


def receiver():
    # capta sinal pelo microfone
    print(f"Gravando por {DURATION} segundos...")
    recording = sd.rec(int(FS*DURATION), samplerate=FS, channels=1)
    sd.wait()
    signal = recording.flatten()

    # ajuste de volume opcional
    level = np.max(np.abs(signal))
    print(f"Nível máximo captado: {level:.3f}")
    gain = float(input("Digite fator de ganho (ex: 1.0 para manter): "))
    signal = signal * gain

    # plot no domínio do tempo
    t = np.arange(len(signal)) / FS
    plt.figure(figsize=(8,3))
    plt.plot(t, signal)
    plt.title("Sinal recebido no tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # FFT e detecção de picos
    N = len(signal)
    fft_vals = np.abs(np.fft.fft(signal))[:N//2]
    freqs = np.fft.fftfreq(N, d=1/FS)[:N//2]

    # pede sensibilidade até achar mínimo de 5 picos
    height_factor = 0.5
    peaks, props = find_peaks(fft_vals, height=np.max(fft_vals)*height_factor, distance=20)
    while len(peaks) < 5 and height_factor > 0.1:
        height_factor -= 0.1
        peaks, props = find_peaks(fft_vals, height=np.max(fft_vals)*height_factor, distance=20)

    peak_freqs = freqs[peaks]
    peak_mags = props['peak_heights']
    print("Frequências detectadas:", np.round(peak_freqs,1))

    # plot FFT recebido
    plot_fft(signal, FS, title_suffix="(recebido)")

    # identificação de acorde
    identified = None
    for name, freqs_ref in CHORDS.items():
        matches = sum(any(abs(f - ref) < 10 for f in peak_freqs) for ref in freqs_ref)
        if matches == 3:
            identified = name
            break

    if identified:
        print(f"Acorde identificado: {identified}")
    else:
        print("Não foi possível identificar o acorde com certeza.")


if __name__ == '__main__':
    receiver()
