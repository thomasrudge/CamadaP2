import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

# dicionário de acordes: nome → lista de 3 frequências (Hz)
CHORDS = {
    'Do maior':       [523.25, 659.25, 783.99],
    'Re menor':       [587.33, 698.46, 880.00],
    'Mi menor':       [659.25, 783.99, 987.77],
    'Fa maior':       [698.46, 880.00, 1046.50],
    'Sol maior':      [783.99, 987.77, 1174.66],
    'La menor':       [880.00, 1046.50, 1318.51],
    'Si bemol menor': [493.88, 587.33, 698.46]
}

FS = 44100  # taxa de amostragem (Hz)
DURATION = 3.0  # duração da emissão (segundos)


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


def emitter():
    # lista de acordes
    print("Acordes disponíveis:")
    for i, name in enumerate(CHORDS, start=1):
        print(f"{i}. {name}")
    idx = int(input("Escolha o número do acorde: ")) - 1

    


    nome = list(CHORDS.keys())[idx]
    freqs = CHORDS[nome]

    

    # gera sinal
    t = np.linspace(0, DURATION, int(FS*DURATION), endpoint=False)
    signal = sum(np.sin(2*np.pi*f*t) for f in freqs)
    signal /= np.max(np.abs(signal))

    # reproduz sinal
    print(f"Tocando acorde: {nome}")
    sd.play(signal, FS)
    sd.wait()

    # plot no domínio do tempo (duas senoides)
    plt.figure(figsize=(8,3))
    plt.plot(t[:1000], signal[:1000])
    plt.title(f"Sinal no tempo ({nome})")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # plot FFT
    plot_fft(signal, FS, title_suffix=f"(emitido: {nome})")

    


if __name__ == '__main__':
    emitter()
