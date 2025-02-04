import mediapipe as mp
import cv2
import os, time
from HandTracker import Tracker

# mpDraw.draw_landmarks(img, handLms, handsMp.HAND_CONNECTIONS)

cap = cv2.VideoCapture(1)

cTime = 0
pTime = 0

_, img = cap.read()
h, w, c = img.shape
t = Tracker(width=w, height=h, landmarks=[4,8])

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    t.process(imgRGB)
    
    p1 = (t.positions[4].x, t.positions[4].y)
    p2 = (t.positions[8].x, t.positions[8].y)
    cv2.line(img, p1, p2, (255, 255, 255), 1)
    cv2.putText(img, str(t.get_dist(t.positions[4], t.positions[8])), (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
    col = (255,255,255)
    angle = t.get_angle(t.positions[4], t.positions[8])
    if angle > 60:
        col = (0, 0, 255)
    cv2.putText(img, "angle: "+str(angle), (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)+40), cv2.FONT_HERSHEY_PLAIN, 2, col, 3)

            
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = time.time()

    cv2.putText(img, str(int(fps))+" fps", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)


    cv2.imshow("Frame", img)
    cv2.waitKey(1)
    