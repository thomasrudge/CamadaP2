import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

FS = 44100       # taxa de amostragem do receptor (Hz)
DURATION = 3.0   # duração de gravação (s)

CHORDS = {
    'Do maior':       [523.25, 659.25, 783.99],
    'Re menor':       [587.33, 698.46, 880.00],
    'Mi menor':       [659.25, 783.99, 987.77],
    'Fa maior':       [698.46, 880.00, 1046.50],
    'Sol maior':      [783.99, 987.77, 1174.66],
    'La menor':       [880.00, 1046.50, 1318.51],
    'Si bemol menor': [493.88, 587.33, 698.46]
}

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
    plt.axhline(y=100, color='red', linestyle='-')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return fft_vals , freqs

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

    # plot da FFT
    fft_vals , freqs = plot_fft(signal, FS, title_suffix="(recebido)")
    

    peak_freqs=[]
    indice=1
    while len(peak_freqs)< 5:

        peaks, properties = find_peaks(fft_vals, height=100*indice)  
        peak_freqs = freqs[peaks]
        indice -= 0.1
  
    #print("peak_freqs", peak_freqs)

    peak_freaqs_filt = []

    for vnf in peak_freqs:
        add = True
        for vf in peak_freaqs_filt:
            if len(peak_freaqs_filt) != 0 :
                if (vnf > vf-20) and (vnf < vf+20):
                    add=False
            if vnf < 300:
                add=False
                
        if add==True and vnf > 300:
            peak_freaqs_filt.append(vnf)

    #print("peak_freqs_filt", peak_freaqs_filt)



    
    for acorde2, refs in CHORDS.items():
        count = sum(
            any(abs(fr - ref) < 30 for fr in peak_freaqs_filt)
            for ref in refs
        )
        if count == 3:
            acorde_detectado = acorde2
            break

    print("peak_freaqs_filt" , peak_freaqs_filt)
    print("Acorde detectado foi: ",acorde_detectado)
    
        

        
# peaks é um array de índices onde há picos
# properties['peak_heights'] contém as alturas dos picos

if __name__ == '__main__':
    receiver()
