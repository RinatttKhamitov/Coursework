import numpy as np
import matplotlib.pyplot as plt
import wave
from analyzer import AudioAnalyzer  # Используем тот же анализатор

def plot_audio_analysis(filename):
    analyzer = AudioAnalyzer()
    analyzer.load_audio(filename, duration_limit=5)

    samples = analyzer.samples
    time = np.linspace(0, len(samples) / analyzer.samplerate, len(samples))

    # Временной сигнал
    plt.figure(figsize=(12, 4))
    plt.plot(time, samples)
    plt.title("Временная область")
    plt.xlabel("Время (с)")
    plt.ylabel("Амплитуда")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Анализ по кадрам
    rms_vals = []
    centroids = []
    zcr_vals = []
    dom_freqs = []

    idx = 0
    while idx + analyzer.frame_size <= len(samples):
        frame = samples[idx:idx + analyzer.frame_size]
        rms_vals.append(analyzer.get_rms(frame))
        centroids.append(analyzer.get_centroid(frame))
        zcr_vals.append(analyzer.get_zero_crossing_rate(frame))
        dom_freqs.append(analyzer.get_dominant_freq(frame))
        idx += analyzer.hop_size

    times = np.arange(len(rms_vals)) * (analyzer.hop_size / analyzer.samplerate)

    # RMS
    plt.figure(figsize=(12, 3))
    plt.plot(times, rms_vals)
    plt.title("RMS (Энергия)")
    plt.xlabel("Время (с)")
    plt.ylabel("RMS")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Спектральный центроид
    plt.figure(figsize=(12, 3))
    plt.plot(times, centroids)
    plt.title("Спектральный центроид")
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ZCR
    plt.figure(figsize=(12, 3))
    plt.plot(times, zcr_vals)
    plt.title("Частота пересечения нуля (ZCR)")
    plt.xlabel("Время (с)")
    plt.ylabel("Относительное значение")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Доминирующая частота
    plt.figure(figsize=(12, 3))
    plt.plot(times, dom_freqs)
    plt.title("Доминирующая частота")
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Спектрограмма
    spec = analyzer.get_spectrogram()
    plt.figure(figsize=(12, 5))
    plt.imshow(10 * np.log10(spec + 1e-6), aspect='auto', origin='lower',
               extent=[0, analyzer.get_total_time(), 0, analyzer.samplerate / 2])
    plt.title("Спектрограмма (логарифмическая шкала)")
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.colorbar(label="Амплитуда (dB)")
    plt.tight_layout()
    plt.show()

# Пример запуска
if __name__ == "__main__":
    plot_audio_analysis("assets/music/Frank.wav")  # Замените на путь к вашему файлу
