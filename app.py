import cv2
import numpy as np
import av
import streamlit as st
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer
from cvzone.HandTrackingModule import HandDetector
from time import time

# Initialize hand detector outside class
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Define keyboard layout
keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.'],
    ['Er', 'Sp', 'En']
]

# Define button layout
class Button:
    def __init__(self, pos, text, size=(80, 80)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (x + 15, y + 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

button_list = [Button((100 * j + 50, 100 * i + 50), key) for i, row in enumerate(keys) for j, key in enumerate(row)]

# Video processing class
class VirtualKeyboard(VideoTransformerBase):
    def __init__(self):
        self.typed_text = ""
        self.last_click_time = 0

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        hands, img = detector.findHands(img, draw=True)

        # Draw keyboard
        for button in button_list:
            button.draw(img)

        if hands:
            lmList = hands[0]["lmList"]
            if lmList:
                x8, y8 = lmList[8][0], lmList[8][1]
                x12, y12 = lmList[12][0], lmList[12][1]
                for button in button_list:
                    bx, by = button.pos
                    bw, bh = button.size
                    if bx < x8 < bx + bw and by < y8 < by + bh:
                        cv2.rectangle(img, button.pos, (bx + bw, by + bh), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (bx + 15, by + 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

                        # Distance between index and middle finger tips
                        distance = ((x8 - x12) ** 2 + (y8 - y12) ** 2) ** 0.5

                        if distance < 40 and (time() - self.last_click_time) > 1:
                            if button.text == "Er":
                                self.typed_text = self.typed_text[:-1]
                            elif button.text == "Sp":
                                self.typed_text += " "
                            elif button.text == "En":
                                self.typed_text += "\n"
                            else:
                                self.typed_text += button.text
                            self.last_click_time = time()

        # Show typed text
        cv2.rectangle(img, (50, 400), (700, 500), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, self.typed_text, (60, 470), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

        return img

# Streamlit App UI
st.title("✋ Virtual Keyboard - Gesture Typing")
st.markdown("Use your fingers to type by pointing and pinching!")

webrtc_streamer(
    key="keyboard",
    video_transformer_factory=VirtualKeyboard,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
