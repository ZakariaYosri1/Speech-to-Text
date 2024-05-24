# Speech-to-Text
This application provides a simple interface for recording audio, analyzing its frequency spectrum, and converting speech to text using various languages.

Features:
Record Audio: Record audio from your microphone.
Frequency Spectrum Analysis: Visualize the frequency spectrum of the recorded audio using Discrete Fourier Transform and Hilbert Transform.
Speech to Text Conversion: Convert recorded speech to text in different languages using Google Speech Recognition API.
Requirements:
Python 3.x
PyQt5
NumPy
Matplotlib
Sounddevice
SpeechRecognition
Wavio
SciPy
Installation:
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/audio-processing-app.git
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Usage:
Run the application:

bash
Copy code
python main.py
Use the "Record Audio" button to start recording audio from your microphone.

Choose the desired language from the dropdown menu.

Click the "Stop Recording" button to stop recording.

The recorded speech will be displayed as text in the interface.

You can also visualize the frequency spectrum of the recorded audio.

Contributing:
Contributions are welcome! If you have any suggestions, improvements, or bug fixes, feel free to open an issue or create a pull request.

License:
This project is licensed under the MIT License
