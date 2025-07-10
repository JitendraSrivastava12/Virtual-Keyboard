<h1>🖐️ Virtual Keyboard (Hand Gesture Based)</h1>
A virtual keyboard that uses hand gestures to type text, leveraging computer vision techniques. The system uses your webcam to detect hand landmarks in real time and maps finger positions to virtual keys, allowing you to type without touching a physical keyboard.

   <h3>  [Link To Webside](https://virtual-keyboard-jituji.streamlit.app/)</h3>

<h3>🚀 Features</h3>
1.🖐️ Hand gesture-based typing using a webcam
2.🎯 Real-time finger tracking using OpenCV and cvzone
3.🧠 Smart key selection using gesture detection (index tip + thumb tip distance)
4.📱 Web-based UI with Streamlit and streamlit-webrtc
5.🔊 Optional text-to-speech for typed output

<h3>📦 Tech Stack</h3>
<h4>Frontend</h4>: Streamlit, streamlit-webrtc
<h4>Backend</h4>: OpenCV, cvzone, MediaPipe
<h4>Language</h4>: Python

<h3>🔧 Installation</h3>
git clone https://github.com/yourusername/virtual-keyboard.git
cd virtual-keyboard
pip install -r requirements.txt

<h3>▶️ Run the App</h3>
streamlit run app.py

<h3>🛠 Deployment</h3>
.✅ Compatible with Render, Streamlit Cloud, etc.
.If deploying on Render:
1.Use streamlit run app.py as start command
2.Use Docker or ensure apt packages for opencv-python-headless are installed
3.Enable camera access (WebRTC will handle video)

<h3>❗ Known Issues</h3>
Streamlit + WebRTC may not work in all browsers (use Chrome or Firefox for best compatibility)
Latency may occur on low-end devices or slow internet

<h3>🙌 Acknowledgements</h3>
1.cvzone
2.OpenCV
3.MediaPipe
4.Streamlit
5.streamlit-webrtc

<h3>📄 License</h3>
This project is licensed under the MIT License - see the LICENSE file for details.


