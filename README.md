# Autonomous Operation Robot

This repository contains code to play the board game Operation autonomously using a robotic arm controlled by a Raspberry Pi Pico. The project leverages the DroidCam app for iPhone to capture the game board.

## Components

- **main.py**: This script runs on the Raspberry Pi Pico and controls the robotic arm. It establishes a connection to Wi-Fi, subscribes to MQTT topics, and uses inverse kinematics to move the arm to specific positions based on the game board's state. It also handles the communication between the Raspberry Pi Pico and the PC.

- **imageprocessing.py**: This script runs on the PC and performs image processing on the captured frames from the iPhone camera. It detects the game board, calculates the position and orientation of the game piece, and communicates this information to the Raspberry Pi Pico through MQTT.

## Requirements

### Raspberry Pi Pico

Ensure the following libraries are installed on your Raspberry Pi Pico:

- `mqtt`: MQTT client library for MicroPython.
- `machine`: Basic hardware control library for MicroPython.

### PC

Ensure the following libraries are installed on your PC:

- `cv2`: OpenCV for image processing.
- `numpy`: Library for numerical operations.
- `paho.mqtt`: MQTT client library for Python.

## Setup

1. Connect the robotic arm to the Raspberry Pi Pico.

2. Install the necessary libraries on the Raspberry Pi Pico and PC.

3. Connect the Raspberry Pi Pico to Wi-Fi by providing the appropriate SSID and password in the `main.py` script.

4. Update the `broker_address` variable in both scripts with the address of your MQTT broker.

5. Install the DroidCam app on your iPhone and connect it to your PC. Update the `url` variable in `main.py` with the correct DroidCam address.

6. Run the `main.py` script on the Raspberry Pi Pico.

7. Run the `imageprocessing.py` script on your PC.

8. Enjoy watching the robotic arm autonomously play Operation!

## Usage

1. Execute the scripts as mentioned in the setup section.

2. The system will initialize and connect to the game board.

3. The robotic arm will move to the specified positions, controlled by the image processing script.

4. The game piece will be picked up and placed at a designated location.

5. The system will check if the operation was successful. If not, it will retry.

6. Repeat the process until the game is completed.

Note: Make sure the lighting conditions and camera positioning are optimal for accurate image processing.

Feel free to customize and extend the code to suit your specific setup and requirements.
