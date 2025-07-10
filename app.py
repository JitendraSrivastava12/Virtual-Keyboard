# Patch asyncio for Python 3.10+ issues with event loop
import asyncio
import sys

if sys.version_info >= (3, 10):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import av
from time import time

# Streamlit page config
st.set_page_config(page_title="Virtual Gesture Keyboard", layout="wide")
st.title("🖐️ Virtual Keyboard with Hand Gestures")

# STUN config
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False},
)

# Button class
class Button:
    def __init__(self, pos, text, size=[80, 80]):
        self.pos = pos
        self.size = size
        self.text = text
        self.x, self.y = self.pos
        self.h, self.w = self.size

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.x + self.h, self.y + self.w),
                      (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (self.x + 20, self.y + 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

# Keys layout
keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.'],
    ['Er', 'Sp', 'En']
]
buttonList = [Button([100 * j + 50, 100 * i + 50], key)
              for i, row in enumerate(keys) for j, key in enumerate(row)]

detector = HandDetector(detectionCon=0.8, maxHands=1)
typed_text = ""
last_press_time = 0

# Main video callback
def video_frame_callback(frame):
    global typed_text, last_press_time

    img = frame.to_ndarray(format="bgr24")
    hands, img = detector.findHands(img)

    # Draw buttons
    for button in buttonList:
        button.draw(img)

    # Process gestures
    if hands:
        lmList = hands[0]["lmList"]
        index_finger = lmList[8]
        middle_finger = lmList[12]

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < index_finger[0] < x + h and y < index_finger[1] < y + w:
                cv2.rectangle(img, button.pos, (x + h+5, y + w+5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 50),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 3)

                distance, _, _ = detector.findDistance(index_finger, middle_finger, img)
                if distance < 40 and time() - last_press_time > 1:
                    cv2.rectangle(img, button.pos, (x + h+5, y + w+5), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 50),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 3)
                    key = button.text
                    if key == "Er":
                        typed_text = typed_text[:-1]
                    elif key == "Sp":
                        typed_text += " "
                    elif key == "En":
                        typed_text += "\n"
                    else:
                        typed_text += key
                    last_press_time = time()

    # Display typed text
    cv2.putText(img, typed_text, (50, 500),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    return av.VideoFrame.from_ndarray(img, format="bgr24")


# Launch webcam stream
webrtc_streamer(
    key="virtual-keyboard",
    mode=WebRtcMode.SENDRECV,
    client_settings=WEBRTC_CLIENT_SETTINGS,
    video_frame_callback=video_frame_callback,
    async_processing=True
)
