import mediapipe as mp
import cv2
import os, time
from HandTracker import Tracker
from utils import *

# mpDraw.draw_landmarks(img, handLms, handsMp.HAND_CONNECTIONS)
# z < -0.1  --> touch activation

class Camera():
    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        self.cTime = 0
        self.pTime = 0
        _, self.img = self.cap.read()

        h, w, c = self.img.shape
        self.tracker = Tracker(width=w, height=h, landmarks=[4,8])

        #temp
        self.max_dist = 0
    
    def update_tracker(self):
        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        if self.tracker.process(imgRGB):
            return True
        return False

    def update_fps(self):
        self.cTime = time.time()
        fps = 1/(self.cTime-self.pTime)
        self.pTime = time.time()

        cv2.putText(self.img, str(int(fps))+" fps", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    
    def draw_line(self, landmark1: int, landmark2: int, include_info = True):
        p1 = (self.tracker.positions[landmark1].x, self.tracker.positions[landmark1].y)
        p2 = (self.tracker.positions[landmark2].x, self.tracker.positions[landmark2].y)
        cv2.line(self.img, p1, p2, (255, 255, 255), 1)

        if include_info:
            dist = self.tracker.get_dist(self.tracker.positions[landmark1], self.tracker.positions[landmark2])
            if dist == 0:
                return
            
            if dist > self.max_dist:
                self.max_dist = dist
                dist = 1
            elif dist < self.max_dist*0.1:
                dist = 0
            else:
                dist = interpolate(dist, 0, self.max_dist, 0, 1)
            cv2.putText(self.img, str(round(dist, 2)),
                                    (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

    def draw_angle(self, landmark1: int, landmark2: int, activation_color = (0, 0, 255), min_angle: int = 60):
        p1 = (self.tracker.positions[landmark1].x, self.tracker.positions[landmark1].y)
        p2 = (self.tracker.positions[landmark2].x, self.tracker.positions[landmark2].y)
        angle = self.tracker.get_angle(self.tracker.positions[landmark1], self.tracker.positions[landmark2])
        color = (255, 255, 255)
        if angle > min_angle:
            color = activation_color
        cv2.putText(self.img, "angle: "+str(angle), (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)+40), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)

    def draw_touch(self, landmark: int):
        pos = self.tracker.positions[landmark]
        color = (255,255,255)
        if pos.z < -0.1:
            color = (0,0,255)
        cv2.circle(self.img, center=(pos.x, pos.y), radius=10, color=color, thickness=1, lineType=3)
    
    def update_frame(self):
        _, self.img = self.cap.read()
        if self.update_tracker():
            self.draw_line(4, 8)
            self.draw_angle(4, 8)
            self.draw_touch(8)
        self.update_fps()
        #print(self.tracker.positions[4].z)

        cv2.imshow("Frame", self.img)
        cv2.waitKey(1)

    
c = Camera()
while True:
    c.update_frame()