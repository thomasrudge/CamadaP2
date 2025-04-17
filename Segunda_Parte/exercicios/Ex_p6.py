import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

# parâmetros
fs = 44100            # frequência de amostragem (Hz)
duration = 2.0        # duração (s)

# vetor de tempo de 0 até 2 s em passos de 1/fs
t = np.arange(0, duration, 1/fs)

# três senoides
x1 =  4 * np.sin(2*np.pi*3000 * t)
x2 = 20 * np.sin(2*np.pi*5000 * t)
x3 =  5 * np.sin(2*np.pi*6000 * t)

# sinal composto
x = x1 + x2 + x3

# normaliza para evitar clipping
x_norm = x / np.max(np.abs(x))

ruido = 1.5 * np.random.randn(len(x_norm))   # 0.1 controla a amplitude do ruído
x_norm = x_norm + ruido


# reproduz
sd.play(x_norm, fs)
sd.wait()

def plot_fft(sinal, fs):
    """
    Plota o gráfico da Transformada de Fourier (FFT) de um sinal.

    Parâmetros:
    - sinal: lista ou array com os valores do sinal no tempo
    - fs: taxa de amostragem em Hz
    """

    # Converter sinal para array NumPy
    sinal = np.array(sinal)

    # Número de amostras e vetor de tempo
    N = len(sinal)
    t = np.arange(N) / fs

    # FFT e cálculo da magnitude
    fft_result = np.fft.fft(sinal)
    freqs = np.fft.fftfreq(N, d=1/fs)
    magnitude = np.abs(fft_result)

    # Manter só metade do espectro (frequências positivas)
    half_N = N // 2
    freqs = freqs[:half_N]
    magnitude = magnitude[:half_N]

    # Plot do sinal no tempo (opcional)
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(t, sinal)
    plt.title("Sinal no tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    # Plot do espectro de frequência
    plt.subplot(1, 2, 2)
    plt.stem(freqs, magnitude, basefmt=" ")
    plt.title("Transformada de Fourier (FFT)")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


plot_fft(x_norm , fs)
