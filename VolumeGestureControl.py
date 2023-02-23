import cv2 as cv
import mediapipe as mp
import numpy as np
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volBar = 400
volPer = 0
volMin, volMax = volume.GetVolumeRange()[:2]

while True:
    success, img = cap.read()
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmlist = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmlist.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    
    if lmlist!= []:
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]

        cv.circle(img, (x1, y1), 10, (0,0,255), cv.FILLED)
        cv.circle(img, (x2, y2), 10, (0,0,255), cv.FILLED)
        cv.line(img, (x1, y1), (x2, y2), (0,0,255), 2)
        length = hypot(x2-x1, y2-y1)

        vol = np.interp(length, [20,150], [volMin, volMax])
        volBar = np.interp(length, [30,350], [400,150])
        volPer = np.interp(length, [30,350], [0,100])
        print(vol, int(length))

        volume.SetMasterVolumeLevel(vol, None)
        cv.rectangle(img, (50,150), (85, 400), (0,0,255), 2)
        cv.rectangle(img, (50, int(volBar)), (85, 400), (0,0,255), cv.FILLED)
        cv.putText(img, f'{int(volPer)}%', (30, 120), cv.FONT_HERSHEY_PLAIN, 3, (0,0,255), 3)

    cv.imshow('Image', img)
    k = cv.waitKey(1)
    if k == ord('q'):
        break