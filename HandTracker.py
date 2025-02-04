import mediapipe as mp
import cv2
import os, time, math

# TODO:
# swipe motion detection using z coordinate

class Pos():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

class Tracker():
    def __init__(self, width: int, height: int, landmarks: list[int] = list(range(0,21))):
        self.handsMp = mp.solutions.hands
        self.hands = self.handsMp.Hands()
        self.mpDraw = mp.solutions.drawing_utils

        self.w = width
        self.h = height

        self.positions = {}
        for i in landmarks:
            self.positions[i] = Pos()
    
    def process(self, imgRGB):
        results = self.hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for i in list(self.positions.keys()):
                    self.positions[i].x = int(handLms.landmark[i].x * self.w)
                    self.positions[i].y = int(handLms.landmark[i].y * self.h)
                    self.positions[i].z = handLms.landmark[i].z
            return True
        return False


    def get_dist(self, pos1: Pos , pos2: Pos):
        return int(math.sqrt(math.pow(pos2.x - pos1.x, 2) + math.pow(pos2.y - pos1.y, 2)))

    def get_angle(self, pos1: Pos , pos2: Pos):
        x = abs(pos2.x - pos1.x)
        y = abs(pos2.y - pos1.y)

        if x == 0 or y == 0:
            return 0

        return int(math.degrees(math.atan(x/y)))


    

