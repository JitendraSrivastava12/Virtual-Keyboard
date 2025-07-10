import cv2
import numpy as np
import av
import time
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from cvzone.HandTrackingModule import HandDetector

# Global hand detector to avoid reinitialization
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Define keyboard layout
keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.'],
    ['Er', 'Sp', 'En']
]

# Define button class
class Button:
    def __init__(self, pos, text, size=(60, 60)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (x + 10, y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

# Create button grid (smaller spacing and size)
button_list = [
    Button((70 * j + 30, 70 * i + 30), key)
    for i, row in enumerate(keys)
    for j, key in enumerate(row)
]

# Video processor class
class VirtualKeyboard(VideoTransformerBase):
    def __init__(self):
        self.typed_text = ""
        self.last_click_time = 0
        self.prev_frame_time = time.time()

    def transform(self, frame):
        curr_time = time.time()
        # Limit FPS to reduce CPU/RAM usage
        if curr_time - self.prev_frame_time < 0.15:  # ~6 FPS
            return frame.to_ndarray(format="bgr24")

        self.prev_frame_time = curr_time
        img = frame.to_ndarray(format="bgr24")
        hands, _ = detector.findHands(img, draw=False)

        for button in button_list:
            button.draw(img)

        if hands:
            lmList = hands[0]["lmList"]
            if lmList:
                x8, y8 = lmList[8][0], lmList[8][1]   # Index tip
                x12, y12 = lmList[12][0], lmList[12][1]  # Middle tip
                for button in button_list:
                    bx, by = button.pos
                    bw, bh = button.size
                    if bx < x8 < bx + bw and by < y8 < by + bh:
                        cv2.rectangle(img, button.pos, (bx + bw, by + bh), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (bx + 10, by + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                        dist = ((x8 - x12) ** 2 + (y8 - y12) ** 2) ** 0.5
                        if dist < 40 and (time.time() - self.last_click_time) > 1:
                            if button.text == "Er":
                                self.typed_text = self.typed_text[:-1]
                            elif button.text == "Sp":
                                self.typed_text += " "
                            elif button.text == "En":
                                self.typed_text += "\n"
                            else:
                                self.typed_text += button.text
                            self.last_click_time = time.time()

        # Show typed text
        cv2.rectangle(img, (30, 400), (600, 460), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, self.typed_text[-30:], (40, 440), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 2)

        return img

# Streamlit App UI
st.title("✋ Virtual Keyboard (Streamlit Version)")
st.caption("Use your finger to point and pinch to type.")

webrtc_streamer(
    key="keyboard",
    video_transformer_factory=VirtualKeyboard,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 480},
            "height": {"ideal": 360}
        },
        "audio": False
    },
    async_processing=True,
)
