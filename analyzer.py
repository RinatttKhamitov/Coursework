import numpy as np
import wave

class AudioAnalyzer:
    def __init__(self):
        self.samples = np.array([])
        self.frame_size = 1024
        self.hop_size = 512
        self.index = 0
        self.samplerate = 0  # Частота дискретизации по умолчанию (можно извлечь из файла)

    def load_audio(self, filename):
        with wave.open(filename, 'rb') as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            self.samplerate = wav.getframerate()  # Чтение частоты дискретизации
            print(self.samplerate)
            n_frames = wav.getnframes()
            raw_data = wav.readframes(n_frames)
            
            audio = np.frombuffer(raw_data, dtype=np.int16)
            if n_channels > 1:
                audio = audio[::n_channels]  # downmix to mono
            self.samples = audio.astype(np.float32) / np.iinfo(np.int16).max
            self.index = 0
            self.total_time = n_frames / self.samplerate  # Время в секундах

    def data_ready(self):
        return self.index + self.frame_size <= len(self.samples)

    def get_next_frame(self):
        frame = self.samples[self.index:self.index+self.frame_size]
        self.index += self.hop_size
        windowed = frame * np.hanning(len(frame))
        spectrum = np.abs(np.fft.fft(windowed))[:len(frame)//2]
        spectrum = spectrum / np.max(spectrum + 1e-6)
        return spectrum.tolist()

    def get_total_time(self):
        return self.total_time
