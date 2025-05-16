import numpy as np
import wave

class AudioAnalyzer:
    def __init__(self, frame_size=2048, hop_size=512):
        self.frame_size = frame_size
        self.hop_size = hop_size
        self.samplerate = None
        self.samples = None
        self.index = 0
        self.total_time = 0

    def load_audio(self, filename):
        with wave.open(filename, 'rb') as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            self.samplerate = wav.getframerate()
            n_frames = wav.getnframes()
            raw_data = wav.readframes(n_frames)

            audio = np.frombuffer(raw_data, dtype=np.int16)
            if n_channels > 1:
                audio = audio[::n_channels]  # downmix to mono
            self.samples = audio.astype(np.float32) / np.iinfo(np.int16).max
            self.index = 0
            self.total_time = n_frames / self.samplerate

    def data_ready(self):
        return self.samples is not None and self.index + self.frame_size <= len(self.samples)


    def get_next_frame(self):
        frame = self.samples[self.index:self.index + self.frame_size]
        self.index += self.hop_size

        windowed = frame * np.hanning(len(frame))
        spectrum = np.abs(np.fft.fft(windowed))[:len(frame)//2]
        spectrum = spectrum / (np.max(spectrum) + 1e-6)

        return {
            "rms": self.get_rms(frame),
            "centroid": self.get_centroid(windowed),
            "zcr": self.get_zero_crossing_rate(frame),
            "dominant_freq": self.get_dominant_freq(windowed),
            "spectrum": spectrum.tolist(),
            "frame": frame.tolist()
        }

    def get_rms(self, frame):
        return np.sqrt(np.mean(frame ** 2))

    def get_centroid(self, frame):
        spectrum = np.abs(np.fft.fft(frame))[:len(frame)//2]
        freqs = np.fft.fftfreq(len(frame), d=1.0/self.samplerate)[:len(frame)//2]
        if np.sum(spectrum) == 0:
            return 0
        return np.sum(freqs * spectrum) / np.sum(spectrum)

    def get_zero_crossing_rate(self, frame):
        return ((frame[:-1] * frame[1:]) < 0).sum() / len(frame)

    def get_dominant_freq(self, frame):
        spectrum = np.abs(np.fft.fft(frame))[:len(frame)//2]
        freqs = np.fft.fftfreq(len(frame), d=1.0/self.samplerate)[:len(frame)//2]
        idx = np.argmax(spectrum)
        return freqs[idx]

    def get_total_time(self):
        return self.total_time

    def get_spectrogram(self):
        spectrogram = []
        idx = 0
        while idx + self.frame_size <= len(self.samples):
            frame = self.samples[idx:idx+self.frame_size] * np.hanning(self.frame_size)
            spectrum = np.abs(np.fft.fft(frame))[:self.frame_size // 2]
            spectrum /= np.max(spectrum + 1e-6)
            spectrogram.append(spectrum)
            idx += self.hop_size
        return np.array(spectrogram).T
