import mediapipe as mp
import cv2
import os, time
from HandTracker import *
from AudioController import AudioController
from utils import *
from KeyboardController import KeyboardController

# mpDraw.draw_landmarks(img, handLms, handsMp.HAND_CONNECTIONS)
# z < -0.08  --> touch activation

# TODO
# add support for 2 hands at once

class Camera():
    def __init__(self, camera: int):
        self.audio = AudioController("chrome.exe")
        self.keyboard = KeyboardController()
        self.cap = cv2.VideoCapture(camera)
        self.cTime = 0
        self.pTime = 0
        _, self.img = self.cap.read()

        h, w, c = self.img.shape
        self.tracker = Tracker(width=w, height=h, left_landmarks=[4,8], right_landmarks=[4,8])

        self.max_dist = 0 # maximum recorded distance between joint 4 and 8
        self.last_angle = 0 # track when the last angle activation was
        self.angle_delay = 1 # minimum delay between angle activations
    
    def update_tracker(self):
        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        return self.tracker.process(imgRGB)
        

    def update_fps(self):
        self.cTime = time.time()
        fps = 1/(self.cTime-self.pTime)
        self.pTime = time.time()

        cv2.putText(self.img, str(int(fps))+" fps", (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    
    def draw_line(self, hand: str, landmark1: int, landmark2: int, include_info = True):
        """
        draw a line from landmark1 to landmark2
        include_info: adds distance information to img as well

        returns the distance on range [0,1]
        """

        if hand == 'left':
            positions = self.tracker.left_positions
        else:
            positions = self.tracker.right_positions

        p1 = (positions[landmark1].x, positions[landmark1].y)
        p2 = (positions[landmark2].x, positions[landmark2].y)
        cv2.line(self.img, p1, p2, (255, 255, 255), 1)

        if include_info:
            # get distance between landmark1 and 2
            dist = self.tracker.get_dist(positions[landmark1], positions[landmark2])
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

            # display distance on img
            cv2.putText(self.img, str(round(dist, 2)),
                                    (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            return dist

    def draw_angle(self, hand: str, landmark1: int, landmark2: int, activation_color = (0, 0, 255), min_angle: int = 60):
        """
        calculate and display angle between landmark1 and landmark2

        returns True if angle > min_angle
        """
        activated = False

        if hand == 'left':
            positions = self.tracker.left_positions
        else:
            positions = self.tracker.right_positions
        
        p1 = (positions[landmark1].x, positions[landmark1].y)
        p2 = (positions[landmark2].x, positions[landmark2].y)

        # dont track angle if fingers too close
        dist = self.tracker.get_dist(positions[landmark1], positions[landmark2])
        if dist < self.max_dist*0.3:
            return False

        angle = self.tracker.get_angle(positions[landmark1], positions[landmark2])
        color = (255, 255, 255)
        if angle > min_angle:
            activated = True
            color = activation_color
        cv2.putText(self.img, "angle: "+str(angle), (int((p2[0]+p1[0])/2), int((p2[1]+p1[1])/2)+40), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
        cv2.line(self.img, p1, p2, (255, 255, 255), 1)

        return activated

    def draw_touch(self, hand: str, landmark: int):
        if hand == 'left':
            positions = self.tracker.left_positions
        else:
            positions = self.tracker.right_positions
        
        pos = positions[landmark]
        color = (255,255,255)
        if pos.z < -0.08:
            color = (0,0,255)
        cv2.circle(self.img, center=(pos.x, pos.y), radius=10, color=color, thickness=1, lineType=3)
    
    def update_volume(self, volume: float):
        """
        volume: float value between [0,1]
        """
        self.audio.set_volume(volume)
    
    def draw_handedness(self, hand: str):
        """
        temp
        """
        if hand == 'left':
            pos = self.tracker.left_positions[4]
            cv2.putText(self.img, hand, pos.x, pos.y, cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)
        elif hand == 'right':
            pos = self.tracker.right_positions[4]
            cv2.putText(self.img, hand, pos.x, pos.y, cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)

    
    def update_frame(self):
        _, self.img = self.cap.read()
        hands = self.update_tracker()
        if 'left' in hands:
            d = self.draw_line("left", 4, 8)
            self.update_volume(d)

            self.draw_handedness('left')
        if 'right' in hands:
            if self.draw_angle("right", 4, 8) and time.time()-self.last_angle > self.angle_delay:
                self.keyboard.next_song()
                self.last_angle = time.time()
            self.draw_touch("right", 8)

            self.draw_handedness('right')

        self.update_fps()

        cv2.imshow("Frame", self.img)
        return cv2.waitKey(1)

    
c = Camera(0)
while True:
    key = c.update_frame()
    if key == 27: # s key on the keyboard
        break
c.audio.set_volume(1)
c.cap.release()