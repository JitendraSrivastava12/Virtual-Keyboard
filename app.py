import streamlit as st
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from time import sleep

st.title("✋ Virtual Hand Keyboard")

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)

class Button:
    def __init__(self, pos, text, size=[80, 80]):
        self.pos = pos
        self.size = size
        self.text = text
        self.x, self.y = self.pos
        self.h, self.w = self.size

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.x + self.h, self.y + self.w), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (self.x + 20, self.y + 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.'],
        ['Er', 'Sp', 'En']]

buttonList = [Button([100 * j + 50, 100 * i + 50], key)
              for i, row in enumerate(keys) for j, key in enumerate(row)]

typed_text = ""

stframe = st.empty()
while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img)
    for button in buttonList:
        button.draw(img)

    if hands:
        lmList = hands[0]["lmList"]
        finger_pos = lmList[8]
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            if x < finger_pos[0] < x + h and y < finger_pos[1] < y + w:
                cv2.rectangle(img, button.pos, (x + h + 5, y + w + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 50),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 3)
                l, _, _ = detector.findDistance(lmList[8][:2], lmList[12][:2], img)
                if l < 40:
                    cv2.rectangle(img, button.pos, (x + h + 5, y + w + 5), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 50),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 3)
                    if button.text == "Er":
                        typed_text = typed_text[:-1]
                    elif button.text == "Sp":
                        typed_text += " "
                    elif button.text == "En":
                        typed_text += "\n"
                    else:
                        typed_text += button.text
                    sleep(1)

    cv2.putText(img, typed_text, (50, 500), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 3)
    stframe.image(img, channels="BGR")

cap.release()
cv2.destroyAllWindows()
