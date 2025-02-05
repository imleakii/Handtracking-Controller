import mediapipe as mp
import cv2
import os, time
from HandTracker import Tracker
from AudioController import AudioController
from utils import *
from KeyboardController import KeyboardController

# mpDraw.draw_landmarks(img, handLms, handsMp.HAND_CONNECTIONS)
# z < -0.08  --> touch activation

# TODO
# add support for 2 hands at once

class Camera():
    def __init__(self):
        self.audio = AudioController("chrome.exe")
        self.keyboard = KeyboardController()
        self.cap = cv2.VideoCapture(1)
        self.cTime = 0
        self.pTime = 0
        _, self.img = self.cap.read()

        h, w, c = self.img.shape
        self.tracker = Tracker(width=w, height=h, landmarks=[4,8])

        self.max_dist = 0 # maximum recorded distance between joint 4 and 8
        self.last_angle = 0 # track when the last angle activation was
        self.angle_delay = 1 # minimum delay between angle activations
    
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
        """
        draw a line from landmark1 to landmark2
        include_info: adds distance information to img as well

        returns the distance on range [0,1]
        """
        p1 = (self.tracker.positions[landmark1].x, self.tracker.positions[landmark1].y)
        p2 = (self.tracker.positions[landmark2].x, self.tracker.positions[landmark2].y)
        cv2.line(self.img, p1, p2, (255, 255, 255), 1)

        if include_info:
            # get distance between landmark1 and 2
            dist = self.tracker.get_dist(self.tracker.positions[landmark1], self.tracker.positions[landmark2])
            if dist == 0:
                return
            
            # adjust max distance
            if dist > self.max_dist:
                self.max_dist = dist
                print(f"new max dist: {self.max_dist}")

            # interpolate and adjust distance to make it smoother
            dist = interpolate(dist, self.max_dist*0.1, self.max_dist*0.8, 0, 1)
            if dist < 0:
                dist = 0
            elif dist > 1:
                dist = 1

            # display line + distance on img
            cv2.putText(self.img, str(round(dist, 2)),
                                    (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            return dist

    def draw_angle(self, landmark1: int, landmark2: int, activation_color = (0, 0, 255), min_angle: int = 60):
        """
        calculate and display angle between landmark1 and landmark2

        returns True if angle > min_angle
        """
        activated = False
        p1 = (self.tracker.positions[landmark1].x, self.tracker.positions[landmark1].y)
        p2 = (self.tracker.positions[landmark2].x, self.tracker.positions[landmark2].y)

        # dont track angle if fingers too close
        dist = self.tracker.get_dist(self.tracker.positions[landmark1], self.tracker.positions[landmark2])
        if dist < self.max_dist*0.3:
            return False

        angle = self.tracker.get_angle(self.tracker.positions[landmark1], self.tracker.positions[landmark2])
        color = (255, 255, 255)
        if angle > min_angle:
            activated = True
            color = activation_color
        cv2.putText(self.img, "angle: "+str(angle), (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)+40), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)

        return activated

    def draw_touch(self, landmark: int):
        pos = self.tracker.positions[landmark]
        color = (255,255,255)
        if pos.z < -0.08:
            color = (0,0,255)
        cv2.circle(self.img, center=(pos.x, pos.y), radius=10, color=color, thickness=1, lineType=3)
    
    def update_volume(self, volume: float):
        """
        volume: float value between [0,1]
        """
        self.audio.set_volume(volume)

    
    def update_frame(self):
        _, self.img = self.cap.read()
        if self.update_tracker():
            d = self.draw_line(4, 8)
            self.update_volume(d)
            if self.draw_angle(4, 8) and time.time()-self.last_angle > self.angle_delay:
                self.keyboard.next_song()
                self.last_angle = time.time()
            self.draw_touch(8)
        self.update_fps()
        #print(self.tracker.positions[4].z)

        cv2.imshow("Frame", self.img)
        return cv2.waitKey(1)

    
c = Camera()
while True:
    key = c.update_frame()
    if key == 27: # s key on the keyboard
        break
c.audio.set_volume(1)
c.cap.release()