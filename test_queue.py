# import the necessary packages
from threading import Thread
import sys

import numpy as np
import cv2
import time
 


# import the Queue class from Python 3
if sys.version_info >= (3, 0):
	from queue import Queue
# otherwise, import the Queue class for Python 2.7
else:
	from Queue import Queue
    

class FileVideoStream:
	def __init__(self, path, queueSize=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(path)
		self.stopped = False
		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queueSize)
        
	def start(self):
		# start a thread to read frames from the file video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self        

	def update(self):
		# keep looping infinitely
		while True:
			# if the thread indicator variable is set, stop the
			# thread
			if self.stopped:
				return
			# otherwise, ensure the queue has room in it
			if not self.Q.full():
				# read the next frame from the file
				(grabbed, frame) = self.stream.read()
				# if the `grabbed` boolean is `False`, then we have
				# reached the end of the video file
				if not grabbed:
					self.stop()
					return
				# add the frame to the queue
				self.Q.put(frame)
                
	def read(self):
		# return next frame in the queue
		return self.Q.get()
    
    
	def more(self):
		# return True if there are still frames in the queue
		return self.Q.qsize() > 0
    

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True




 
# creating the videocapture object
# and reading from the input file
# Change it to 0 if reading from webcam
background_frame=cv2.imread("media/background.jpg")
cap= FileVideoStream("media/marketing_layer/event2/1.mp4").start()
time.sleep(1.0)

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0
 
# Reading the video file until finished
while(cap.more()):
 
    # Capture frame-by-frame
 
    frame = cap.read()
 

    h, w ,_= frame.shape

    frame[:h-190, :] = frame[190:, :]
    frame[h-190:, :] = 0  
    
    overlay =frame.copy()
    #added_image = cv2.addWeighted(background_frame,overlay_valueA,overlay,overlay_valueB,0)
    added_image=background_frame.copy()
    
    overlay_hsv = cv2.cvtColor(overlay, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.split(overlay_hsv)     
    #v2=cv2.merge([v, v, v])
    #added_image[v>0]=(overlay[v>0]*20)
    
    added_image[v>=50]=overlay[v>=50]    
    
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
    cv2.putText(added_image, fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
 
    # displaying the frame with fps
    cv2.imshow('frame', added_image)
 
    # press 'Q' if you want to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 

cv2.destroyAllWindows()