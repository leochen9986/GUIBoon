import numpy as np
import cv2
import time
 
 
# creating the videocapture object
# and reading from the input file
# Change it to 0 if reading from webcam

cap= cv2.VideoCapture("media/marketing_layer/event2/1.mp4")

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0
 
# Reading the video file until finished
while(cap.isOpened()):
 
    # Capture frame-by-frame
 
    ret, frame = cap.read()
 
    # if video finished or no Video Input
    if not ret:
        break
 

    
    new_frame_time = time.time()
    
 
    # Calculating the fps
 
    # fps will be number of frame processed in given time frame
    # since their will be most of time error of 0.001 second
    # we will be subtracting it to get more accurate result
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
 
    # converting the fps into integer
    fps = int(fps)
 
    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)
    print("FPS: "+fps)
 
    # putting the FPS count on the frame
    cv2.putText(frame, fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
 
    # displaying the frame with fps
    cv2.imshow('frame', frame)
 
    # press 'Q' if you want to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
# Destroy the all windows now
cv2.destroyAllWindows()