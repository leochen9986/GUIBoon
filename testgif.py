import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle
import time



class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
            # used to record the time when we processed last frame
            self.prev_frame_time = 0
             
            # used to record the time at which we processed current frame
            self.new_frame_time = 0
        frames = []
 
        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
 
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
 
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()
 
    def unload(self):
        self.config(image=None)
        self.frames = None
 
    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)
            self.new_frame_time = time.time()
            self.fps = 1/(self.new_frame_time-self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
         
            # converting the fps into integer
            self.fps = int(self.fps)
         
            # converting the fps to string so that we can display it on frame
            # by using putText function
            self.fps = str(self.fps)
            print("FPS: "+self.fps)
  
#demo :
root = tk.Tk()
lbl = ImageLabel(root)
lbl.pack()
lbl.load('test.gif')
root.mainloop()