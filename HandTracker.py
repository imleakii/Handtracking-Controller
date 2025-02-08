import mediapipe as mp
import cv2
import os, time, math
from utils import *


class Tracker():
    def __init__(self, width: int, height: int, right_landmarks: list[int] = list(range(0,21)), left_landmarks: list[int] = []):
        """
        width: width of image/camera input
        height: height of image/camera input
        landmarks: list of hand joints to track positions of
        right hand landmarks default to tracking all joints
        left hand landmarks default to tracking no joints
        """
        self.handsMp = mp.solutions.hands
        self.hands = self.handsMp.Hands(max_num_hands=2)
        self.mpDraw = mp.solutions.drawing_utils

        self.w = width
        self.h = height

        self.left_positions = {}
        self.right_positions = {}
        for i in left_landmarks:
            self.left_positions[i] = Pos()
        for i in right_landmarks:
            self.right_positions[i] = Pos()
    
    def process(self, imgRGB):
        """
        process inputted image to detect hands and update joint positions
        returns list of hands detected
        """
        count = 0
        results = self.hands.process(imgRGB)

        if not results.multi_hand_landmarks:
            # no hands detected
            return []

        # check which hands detected (left/right/both) and update joint positions
        # TODO: fix this mess
        hands = results.multi_handedness
        print(len(hands))
        if len(hands) == 2:
            print("both")
            first_hand = hands[0].classification[0].label
            print(first_hand)
            if first_hand == 'Left':
                handLms = results.multi_hand_landmarks[0]
            else:
                handLms = results.multi_hand_landmarks[1]
            for i in list(self.left_positions.keys()):
                self.left_positions[i].x = int(handLms.landmark[i].x * self.w)
                self.left_positions[i].y = int(handLms.landmark[i].y * self.h)
                self.left_positions[i].z = handLms.landmark[i].z

            if first_hand == 'Left':
                handLms = results.multi_hand_landmarks[1]
            else:
                handLms = results.multi_hand_landmarks[0]
            for i in list(self.right_positions.keys()):
                self.right_positions[i].x = int(handLms.landmark[i].x * self.w)
                self.right_positions[i].y = int(handLms.landmark[i].y * self.h)
                self.right_positions[i].z = handLms.landmark[i].z
            return ['left', 'right']
        elif hands[0].classification[0].label == 'Right': # temporarily switched because my camera is flipped
            print('left')
            handLms = results.multi_hand_landmarks[0]
            for i in list(self.left_positions.keys()):
                self.left_positions[i].x = int(handLms.landmark[i].x * self.w)
                self.left_positions[i].y = int(handLms.landmark[i].y * self.h)
                self.left_positions[i].z = handLms.landmark[i].z
            return ['left']
        else:
            print('right')
            handLms = results.multi_hand_landmarks[0]
            for i in list(self.right_positions.keys()):
                self.right_positions[i].x = int(handLms.landmark[i].x * self.w)
                self.right_positions[i].y = int(handLms.landmark[i].y * self.h)
                self.right_positions[i].z = handLms.landmark[i].z
            return ['right']


    def get_dist(self, pos1: Pos , pos2: Pos):
        return int(math.sqrt(math.pow(pos2.x - pos1.x, 2) + math.pow(pos2.y - pos1.y, 2)))

    def get_angle(self, pos1: Pos , pos2: Pos):
        x = abs(pos2.x - pos1.x)
        y = abs(pos2.y - pos1.y)

        if x == 0 or y == 0:
            return 0

        return int(math.degrees(math.atan(x/y)))


    

