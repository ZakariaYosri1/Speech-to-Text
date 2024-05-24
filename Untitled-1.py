import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import speech_recognition as sr
import threading
import wavio
from scipy.signal import hilbert

recognizer = sr.Recognizer()

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Processing App")
        self.setGeometry(100, 100, 1000, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.record_audio_widget = RecordAudioWidget(self)
        self.layout.addWidget(self.record_audio_widget)
        self.freq_spectrum_widget = FreqSpectrumWidget()
        self.layout.addWidget(self.freq_spectrum_widget)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

class FreqSpectrumWidget(QWidget):
    update_spectrum_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.update_spectrum_signal.connect(self.update_spectrum)
        self.recorded_text_label = QLabel("Recorded Text: ")
        self.recorded_text_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.recorded_text_label)

    def update_spectrum(self, audio_data):
        self.ax.clear()
        xf, yf = self.discrete_fourier_transform(audio_data)
        self.ax.plot(xf, yf, label='Discrete Fourier Transform')
        self.ax.plot(xf, np.abs(hilbert(yf)), label='Hilbert Transform', linestyle='--')
        self.ax.legend()
        self.ax.set_title('Discrete Fourier Transform & Hilbert Transform')
        self.ax.set_xlabel('Frequency [Hz]')
        self.ax.set_ylabel('Amplitude')
        self.canvas.draw()
        self.display_recorded_text()

    def discrete_fourier_transform(self, audio_data):
        audio_data_mono = audio_data[:, 0]
        N = len(audio_data_mono)
        xf = np.linspace(0.0, 1.0/(2.0 * 44100), N//2)
        yf = np.fft.fft(audio_data_mono)
        return xf, 2.0/N * np.abs(yf[:N//2])

    def display_recorded_text(self):
        self.recorded_text_label.setText("Recorded Text: Analyzing Frequency...")

class RecordAudioWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recording_event = threading.Event()
        self.audio_file = "temp_audio.wav"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.welcome_label = QLabel("Project About Speech to Text")
        self.welcome_label.setFont(QFont('Arial', 16))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.welcome_label)

        self.language_selector = QComboBox()
        self.language_selector.addItem("Arabic", "ar-SA")
        self.language_selector.addItem("English", "en-US")
        self.layout.addWidget(self.language_selector)

        mic_record_layout = QHBoxLayout()
        self.record_button = QPushButton("Record Audio")
        self.record_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 18px; border-radius: 20px; padding: 10px 20px;")
        self.record_button.clicked.connect(self.record_audio)
        mic_record_layout.addWidget(self.record_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-size: 18px; border-radius: 20px; padding: 10px 20px;")
        self.stop_button.clicked.connect(self.stop_recording)
        mic_record_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton("Clear Text")
        self.clear_button.setStyleSheet("background-color: #f44336; color: white; font-size: 18px; border-radius: 20px; padding: 10px 20px;")
        self.clear_button.clicked.connect(self.clear_text)
        mic_record_layout.addWidget(self.clear_button)

        self.layout.addLayout(mic_record_layout)

        self.spectrum_display = QLabel("Text Will Appear Here")
        self.spectrum_display.setFont(QFont('Arial', 12))
        self.spectrum_display.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 10px; border: 2px solid #ccc;")
        self.layout.addWidget(self.spectrum_display)

        self.stream = None  # Initialize the stream variable

    def record_audio(self):
        if not self.recording_event.is_set():
            self.recording_event.set()
            self.record_button.setText("Recording...")
            threading.Thread(target=self.start_recording).start()

    def start_recording(self):
        audio_data = np.empty((0, 2), dtype='int16')
        silence_threshold = 500
        silence_duration = 1
        silence_samples = int(44100 * silence_duration)
        silent_chunks = 0

        def callback(indata, frames, time, status):
            nonlocal audio_data, silent_chunks
            audio_data = np.append(audio_data, indata, axis=0)
            self.parent.freq_spectrum_widget.update_spectrum_signal.emit(indata)
            if np.abs(indata).max() < silence_threshold:
                silent_chunks += frames
            else:
                silent_chunks = 0
            if silent_chunks > silence_samples:
                self.stop_recording()

        self.stream = sd.InputStream(callback=callback, channels=2, samplerate=44100, dtype='int16')
        with self.stream:
            while self.recording_event.is_set():
                sd.sleep(100)
        wavio.write(self.audio_file, audio_data, 44100, sampwidth=2)
        self.record_button.setText("Record Audio")
        threading.Thread(target=self.convert_speech_to_text).start()

    def stop_recording(self):
        if self.recording_event.is_set():
            self.recording_event.clear()
            self.record_button.setText("Record Audio")
            if self.stream is not None:
                self.stream.close()

    def convert_speech_to_text(self):
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio_data = recognizer.record(source)
                language = self.language_selector.currentData()
                text = recognizer.recognize_google(audio_data, language=language)
                self.display_text(text)
        except sr.UnknownValueError:
            self.display_text("Unable to convert speech")
        except sr.RequestError as e:
            self.display_text(f"Request error: {e}")
        except Exception as e:
            self.display_text(f"Error: {e}")

    def display_text(self, text):
        self.spectrum_display.setText(text)

    def clear_text(self):
        self.spectrum_display.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainAppWindow()
    main_window.show()
    sys.exit(app.exec_())
