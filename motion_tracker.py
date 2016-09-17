import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
 
min_area = 3500
threshold = 20
dilation = 10
skew = 100
camera = cv2.VideoCapture(0)
time.sleep(0.25)
 

 
# initialize the first frame in the video stream
firstFrame = None


# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"


    # if the `q` key is pressed, break from the lop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("t"):
        threshold += 1
    elif key == ord("y"):
        threshold -= 1
    elif key == ord("u"):
        min_area += 100
    elif key == ord("i"):
        min_area -= 100
    elif key == ord("o"):
        dilation += 1
    elif key == ord("p"):
        dilation -= 1

 

 
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    width = frame.shape[1]
    height = frame.shape[0]
    pts1 = np.float32([[skew,0],[width-skew,0],[0,height],[width,height]])
    pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
    
    M = cv2.getPerspectiveTransform(pts1,pts2)
   
    frame = cv2.warpPerspective(frame,M,(width,height))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
    # if the first frame is None, initialize it
    if firstFrame is None or key == ord("r"):
        firstFrame = gray
        continue    
    # compute the diff
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, threshold, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image
    thresh = cv2.dilate(thresh, None, iterations=dilation)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Threshold t/y   Min area u/i Dilation o/p", (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Threshold: {}".format(threshold), (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Min area: {}".format(min_area), (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Dilation: {}".format(dilation), (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)



 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()