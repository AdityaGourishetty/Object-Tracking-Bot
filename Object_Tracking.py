import cv2 as cv
import numpy as np
import serial
import time
Arduino = serial.Serial('com5',9600) #Create Serial port object called arduinoSerialData
time.sleep(2) #wait for 2 seconds for the communication to get established

cam = cv.VideoCapture(0)

lower_yellow=np.array([155,100,100])
upper_yellow=np.array([175,200,255])

while(1):
    ret, frame = cam.read()
    frame = cv.flip(frame,1)

    w = frame.shape[1]
    h = frame.shape[0]

    # Smoothen the Image
    image_smooth = cv.GaussianBlur(frame,(7,7),0)

    # Define ROI
    mask = np.zeros_like(frame)

    mask[50:350, 50:350] = [255,255,255]

    image_roi = cv.bitwise_and(image_smooth, mask)
    cv.rectangle(frame, (50,50), (350,350), (0,0,255), 2)
    cv.line(frame, (150,50), (150,350), (0,0,255), 1)
    cv.line(frame, (250,50), (250,350), (0,0,255), 1)
    cv.line(frame, (50,150), (350,150), (0,0,255), 1)
    cv.line(frame, (50,250), (350,250), (0,0,255), 1)

    # Threshold the Image for Yellow Color
    image_hsv = cv.cvtColor(image_roi, cv.COLOR_BGR2HSV)
    image_threshold = cv.inRange(image_hsv, lower_yellow, upper_yellow)

    # Find contours
    contours, heirarchy = cv.findContours(image_threshold, cv.RETR_TREE,cv.CHAIN_APPROX_NONE)

    # Find the index of the largest contour
    if (len(contours)!=0):
        areas = [cv.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]

        # Pointer on Video
        M = cv.moments(cnt)
        if (M['m00'] != 0):
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv.circle(frame, (cx, cy), 4, (0,255,0), -1)

            # Object Motion
            if cx in range(150,250):
                if cy < 150:
                    Arduino.write(b'f')
                    print("Forward")
                    time.sleep(1)
                elif cy > 250:
                    Arduino.write(b'b')
                    print("Backward")
                    time.sleep(1)
                else:
                    Arduino.write(b's')
                    print("Stop")
                    time.sleep(1)

            if cy in range(150,250):
                if cx < 150:
                    Arduino.write(b'l')
                    print("Left")
                    time.sleep(1)
                elif cx > 250:
                    Arduino.write(b'r')
                    print("Right")
                    time.sleep(1)
                else:
                    Arduino.write(b's')
                    print("Stop")
                    time.sleep(1)
            
    cv.imshow('Frame', frame)

    key = cv.waitKey(10)
    if key == 113:
        break

cv.destroyAllWindows()
