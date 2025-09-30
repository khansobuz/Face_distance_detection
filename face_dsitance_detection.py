import cv2
import speech_recognition as sr
import time
import pyaudio

KNOWN_FACE_WIDTH_CM = 14.3
FOCAL_LENGTH = 615  # Calibrate: Add 'print(f"Face width: {w}")' in loop, place face at 50cm, compute FOCAL_LENGTH = (w * 50) / 14.3
DISTANCE_THRESHOLD_CM = 50
DEBOUNCE_TIME_S = 1.0  # Minimum time between microphone state changes

def speech_callback(recognizer, audio):
    print(f"[{time.strftime('%H:%M:%S')}] Audio detected (mic active)")

def initialize_microphone():
    recognizer = sr.Recognizer()
    p = pyaudio.PyAudio()
    print("Available audio devices:")
    device_indices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"Input Device {i}: {dev['name']}")
            device_indices.append(i)
    p.terminate()

    # Try listed device indices
    for index in device_indices:
        try:
            microphone = sr.Microphone(device_index=index)
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"Microphone initialized (Device index {index}).")
            return recognizer, microphone
        except Exception as e:
            print(f"Failed to initialize microphone (index {index}): {e}")
    
    # Fallback to default microphone
    try:
        microphone = sr.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Microphone initialized (default device).")
        return recognizer, microphone
    except Exception as e:
        print(f"Failed to initialize default microphone: {e}")
        return None, None

def main():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    recognizer, microphone = initialize_microphone()
    microphone_available = recognizer is not None and microphone is not None
    if not microphone_available:
        print("Error: Could not initialize any microphone. Running face detection only.")

    stop_listening = None
    listening = False
    last_state_change = time.time()

    # Initialize distance log file
    distance_log_file = open("face_distances.txt", "w")
    distance_log_file.write("Timestamp,Distance (cm)\n")

    print("Starting face distance detection. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        min_distance = float('inf')
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            distance = (KNOWN_FACE_WIDTH_CM * FOCAL_LENGTH) / w if w > 0 else float('inf')
            cv2.putText(frame, f"Dist: {distance:.2f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            if distance < min_distance:
                min_distance = distance
            
            # Log distance to file and console
            timestamp = time.strftime('%H:%M:%S')
            distance_log_file.write(f"{timestamp},{distance:.2f}\n")
            print(f"[{timestamp}] Face detected, Distance: {distance:.2f} cm")

        # Microphone control with debouncing
        if microphone_available:
            current_time = time.time()
            if min_distance < DISTANCE_THRESHOLD_CM and not listening and (current_time - last_state_change) > DEBOUNCE_TIME_S:
                print("Face within 50cm. Starting microphone...")
                try:
                    # Ensure any previous listening is stopped
                    if stop_listening is not None:
                        stop_listening(wait_for_stop=True)
                        stop_listening = None
                    stop_listening = recognizer.listen_in_background(microphone, speech_callback)
                    listening = True
                    last_state_change = current_time
                except Exception as e:
                    print(f"Error starting microphone: {e}")
            elif min_distance >= DISTANCE_THRESHOLD_CM and listening and (current_time - last_state_change) > DEBOUNCE_TIME_S:
                print("Face beyond 50cm. Stopping microphone...")
                try:
                    if stop_listening is not None:
                        stop_listening(wait_for_stop=True)
                        listening = False
                        stop_listening = None
                        last_state_change = current_time
                except Exception as e:
                    print(f"Error stopping microphone: {e}")

        cv2.imshow('Face Distance Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    if listening and stop_listening is not None:
        stop_listening(wait_for_stop=True)
        
    cap.release()
    cv2.destroyAllWindows()
    distance_log_file.close()
    print("Distance log saved to face_distances.txt")

if __name__ == "__main__":
    main()