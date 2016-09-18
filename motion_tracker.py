import argparse
import datetime
import imutils
import time
from time import strftime, gmtime
import cv2
import uuid
import numpy as np
from firebase import firebase
import urllib2
import json
import threading
 



min_area = 3500
threshold = 20
dilation = 8
skewtop = 0
skewbottom = 0
foot_radius = 40
upload_interval = 0.25
last_upload_time = 0
uploading = False
camera = cv2.VideoCapture(0)
time.sleep(0.25)
roughtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

skew = False
skewed_rect = [[50,50],[200,50],[200,200],[50,200]]

current_point = 0
 


positions = []
positions.append([])
positions.append([])
positions.append([])


 
# initialize the first frame in the video stream
avg = None

#initilise firebase
firebase = firebase.FirebaseApplication('https://mithack2016-a7c0c.firebaseio.com', None)

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
    elif key == ord("l"):
        uploading != uploading
    elif key == ord("w"):
         skewed_rect[current_point][1] -= 10
    elif key == ord("s"):
         skewed_rect[current_point][1] += 10
    elif key == ord("a"):
         skewed_rect[current_point][0] -= 10
    elif key == ord("d"):
         skewed_rect[current_point][0] += 10
    elif key == ord("f"):
        if current_point<3:
            current_point += 1
        else:
            view_skew_rect = skewed_rect
            skew = True



    

 

 
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    width = frame.shape[1]
    height = frame.shape[0]
    if skew:
        
        pts1 = np.float32(skewed_rect)
        pts2 = np.float32([[0,0],[width,0],[width,height],[0,height]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        frame = cv2.warpPerspective(frame,M,(width,height))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    # if the first frame is None, initialize it
    if avg is None or key == ord("r"):
        squares = None
        current_point = 0
        avg = gray.copy().astype("float")
        continue    
    # compute the diff
    cv2.accumulateWeighted(gray,avg,0.002)
    
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frameDelta, threshold, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT,(dilation,dilation)))
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)


    #floor plan
    floor = np.zeros((height,width,3), np.uint8)






    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        feetpos = (x+w/2 , y+h-foot_radius , uuid.uuid4().int , time.time())
        
        
        

        for past_poss in positions[-14:]:
            for past_pos in past_poss:
                dist = ( (feetpos[0] - past_pos[0])**2 + (feetpos[1] - feetpos[1])**2 )** 0.5
                
                if dist < foot_radius:
                    feetpos = (feetpos[0],feetpos[1],past_pos[2],feetpos[3])
                    break

        positions[-0].append(feetpos)

        cv2.circle(floor,(feetpos[0],feetpos[1]), foot_radius, (int(feetpos[2]%244),int(feetpos[2]%244),int(feetpos[2]%244)), -1)



    # draw the text and timestamp on the frame
    cv2.putText(frame, "Threshold t/y   Min area u/i Dilation o/p Uploading l Sqew g/h/j/k", (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Threshold: {}".format(threshold), (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Min area: {}".format(min_area), (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Dilation: {}".format(dilation), (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Uploading: {}".format(uploading), (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    #Drawing the squed_rectangle
    if not skew:
        pts = np.array(skewed_rect, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(frame,[pts],True,(0,255,255))

    # show the frame and record if the user presses a key
    
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", cv2.convertScaleAbs(avg))
    cv2.imshow("2D Plan",floor)
    cv2.imshow("Feed", frame)

    #Upload to firebase
    def post_positions(): 
        data = {}
        for pos in positions[-0]:
            data[pos[2]]= {'x': pos[0], 'y': pos[1], 'time': pos[2]}
        result = firebase.post('/{}'.format(roughtime), json.dumps(data))
        print(result)
    if uploading:
        if  time.time() - last_upload_time > upload_interval:
            t = threading.Thread(target=post_positions)
            t.start()
            last_upload_time = time.time()
    

    

    
    



 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()


