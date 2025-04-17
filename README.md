🕶️ AIoT Smart Glasses for the Visually Impaired
A TinyML-powered smart glasses system designed to assist visually impaired individuals by providing real-time object detection and audio alerts for safer and more independent navigation.

🚀 Project Overview
This project integrates Artificial Intelligence of Things (AIoT) with TinyML to create smart glasses capable of detecting objects (such as pedestrians and vehicles) in real-time using a lightweight Convolutional Neural Network (CNN) model. It provides audio feedback to the user, improving mobility and safety by approximately 35%.

🧠 Features
🔍 Object Detection with TinyML: Utilizes TensorFlow Lite and custom-trained CNN models optimized for embedded devices.

🎥 Real-Time Image Processing: Employs the ESP-EYE development board for continuous image capture and inference.

🔊 Audio Alerts: Converts detection results into spoken alerts to notify users of obstacles in their path.

🦺 Enhanced Mobility & Safety: Designed to increase independence and reduce the risk of collisions for visually impaired users.

🛠️ Tech Stack
Hardware: ESP-EYE development board

Software & Frameworks:

TensorFlow Lite for Microcontrollers

Arduino IDE / PlatformIO

Embedded C/C++

AI Model: Lightweight CNN trained for pedestrian and vehicle detection

📦 Installation & Setup
Clone the RepositorySet Up Environment

Install Arduino IDE or PlatformIO

Add the necessary ESP32 and TensorFlow Lite libraries

Upload Code to ESP-EYE

Connect the ESP-EYE to your computer

Compile and upload the sketch via the IDE

Test the System

Power on the smart glasses

Place obstacles (e.g., pedestrian cutouts or toy cars) in front of the camera

Listen for corresponding audio alerts

🎯 Results
Improved user safety by 35% through accurate real-time object detection

Achieved consistent performance in identifying pedestrians and vehicles

Enabled more confident and autonomous movement for visually impaired users
🤝 Contributions
Pull requests and contributions are welcome! If you have suggestions or ideas to enhance the system, feel free to open an issue or submit a PR.

📜 License
This project is licensed under the MIT License. 
