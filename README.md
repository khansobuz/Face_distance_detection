Face Distance Detection
Overview

This project detects faces in real-time using Python and OpenCV and estimates their distance from the camera. It automatically controls the microphone: the mic turns on when a face is within 50 cm and off when the face moves away.

The system provides:

Visual feedback on the video feed, showing detected faces, their distances, and microphone status (On/Off).

Logging of all distance measurements to face_distances.txt.

Support for multiple faces, with mic activation based on the closest face.

This makes it suitable for interactive robots, kiosks, or AI assistant applications.

Features

Real-time face detection using Haar cascades

Distance estimation based on known face width and camera calibration

Smooth distance readings using a frame buffer to reduce fluctuations

Automatic microphone control based on face proximity

Visual indicator for mic status on video feed

Logging distance measurements for analysis

Works with multiple faces by selecting the closest one

Requirements

Python 3.x

OpenCV (opencv-python)

SpeechRecognition (speechrecognition)

PyAudio (pyaudio)

Install dependencies using pip:

pip install opencv-python speechrecognition pyaudio

How to Run

Connect a camera and microphone.

Run the main script:

python main.py


The video window will show detected faces, distance, and mic status.

Press q to quit the program.

All distance measurements are saved in face_distances.txt.
