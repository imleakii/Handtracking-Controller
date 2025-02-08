import cv2

cap = cv2.VideoCapture(0)


while True:
    _, img = cap.read()

    cv2.imshow("Frame", img)
    cv2.waitKey(1)