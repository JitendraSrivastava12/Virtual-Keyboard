import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from time import sleep

# Streamlit UI
st.title("🖐️ Virtual Hand Keyboard")

# WebRTC setup
RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class VirtualKeyboard(VideoProcessorBase):
    def __init__(self):
        self.detector = HandDetector(detectionCon=0.8)
        self.buttonList = []
        self.typed_text = ""
        keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.'],
                ['Er', 'Sp', 'En']]
        for i, row in enumerate(keys):
            for j, key in enumerate(row):
                self.buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        hands, img = self.detector.findHands(img)

        for button in self.buttonList:
            button.draw(img)

        if hands:
            lmList = hands[0]["lmList"]
            finger_pos = lmList[8]
            for button in self.buttonList:
                x, y = button.pos
                w, h = button.size
                if x < finger_pos[0] < x + w and y < finger_pos[1] < y + h:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 3)
                    l, _, _ = self.detector.findDistance(lmList[8], lmList[12], img)
                    if l < 40:
                        if button.text == "Er":
                            self.typed_text = self.typed_text[:-1]
                        elif button.text == "Sp":
                            self.typed_text += " "
                        elif button.text == "En":
                            self.typed_text += "\n"
                        else:
                            self.typed_text += button.text
                        sleep(1)

        cv2.putText(img, self.typed_text, (50, 500), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 3)
        return img

# Button class
class Button:
    def __init__(self, pos, text, size=[80, 80]):
        self.pos = pos
        self.size = size
        self.text = text
        self.x, self.y = self.pos
        self.w, self.h = self.size

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.x + self.w, self.y + self.h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (self.x + 20, self.y + 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

# Stream from webcam
webrtc_streamer(key="virtual_keyboard",
                video_processor_factory=VirtualKeyboard,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False})
