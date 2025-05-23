import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz , lfilter
from scipy.io import wavfile
import sounddevice as sd


frequencias = [20, 32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000, 20000]
ganhos_exemplo = [10, 10, 10, 10, 10, 10, -10, -10, -10, -10, -10, -10]

def peaking_eq(f0, gain_db, Q, fs):
    """
    Design a peaking EQ filter.
    
    Parameters:
        f0 : float      # center frequency in Hz
        gain_db : float # gain in dB (+boost, -cut)
        Q : float       # quality factor
        fs : float      # sampling rate in Hz
        
    Returns:
        b, a : filter coefficients
    """
    A = 10**(gain_db / 40)  # amplitude
    omega = 2 * np.pi * f0 / fs
    alpha = np.sin(omega) / (2 * Q)

    b0 = 1 + alpha * A
    b1 = -2 * np.cos(omega)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(omega)
    a2 = 1 - alpha / A

    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return b, a

def plot_filter_response(b, a, fs, title="Filter Response"):
    w, h = freqz(b, a, fs=fs)
    plt.figure(figsize=(8, 4))
    plt.plot(w, 20 * np.log10(abs(h)))
    plt.title(title)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain [dB]')
    plt.grid()
    plt.ylim(-15, 15)
    plt.show()

# Parameters
fs = 44100         # Sampling rate (Hz)
f0 = 1000          # Center frequency (Hz)
       # Gain in dB
Q = 5

while True:
    print("Atualmente, a lista de ganhos esta assim: \n " \
    f"Ganhos: {ganhos_exemplo} \n" \
    f"Para as frequencias: {frequencias}" )
    cond = input("Gostaria de alterar algum ganho? (Y | N)")
    if cond == "N":
        break
    elif cond == "Y":
        indice = int(input("Qual indice? (0 - 11)"))
        valor = int(input("Qual valor? (-10 ate 10)"))
        ganhos_exemplo[indice] = valor


parametros = []

for f , g in zip(frequencias , ganhos_exemplo):
    parametros.append(peaking_eq(f , g , Q , fs))



fs, audio = wavfile.read('Segunda_Parte/Audio_P7.wav')
audio = audio.astype('float64')

y = audio.copy()
for b, a in parametros:
    y = lfilter(b, a, y, axis=0)

# 2) Normalize para [-1, +1]
y_norm = y / np.max(np.abs(y))

# 3) Toque original e equalizado em sequência
print("Tocando original...")
sd.play(audio/np.max(np.abs(audio)), fs)
sd.wait()

print("Tocando equalizado...")
sd.play(y_norm, fs)
sd.wait()

def bode_plot(parametros, fs):
    """
    Plota o diagrama de Bode do filtro resultante da cascata de todos os filtros em 'parametros'.
    
    Parâmetros:
        parametros: list of (b, a) tuples, coeficientes de cada banda.
        fs: int, taxa de amostragem em Hz.
    """
    # Define o número de pontos de frequência
    worN = 2048
    # Calcula a resposta do primeiro filtro
    b0, a0 = parametros[0]
    w, h_total = freqz(b0, a0, worN=worN)
    # Multiplica pelas respostas dos filtros seguintes
    for b, a in parametros[1:]:
        _, h_i = freqz(b, a, worN=w)
        h_total *= h_i

    # Converte frequência angular para Hz
    freq = w * fs / (2 * np.pi)
    mag_db = 20 * np.log10(np.abs(h_total))
    phase_deg = np.unwrap(np.angle(h_total)) * (180 / np.pi)

    # Plota magnitude
    plt.figure(figsize=(8, 4))
    plt.semilogx(freq, mag_db)
    plt.title('Diagrama de Bode - Magnitude')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Ganho (dB)')
    plt.xlim([20, fs / 2])
    plt.ylim([-12, 12])
    plt.grid(which='both', linestyle='--')
    plt.show()


bode_plot(parametros, fs)
