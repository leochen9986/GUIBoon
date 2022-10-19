import tkinter as tk
import mpv
import time
from PIL import Image, ImageTk
import serial
import json

class GUI:
    def __init__(self, window, window_title, video_source="media/marketing_layer/event1/1.mp4"):
        
        
        self.refresh_time=300
        
        self.esp32_data_current=""
        
        if self.esp32_data_current=="":
            self.esp32_data={"Motion_detected":0,"Bottle_placed":0,"wifi_status":1,"filling_status":0,"cloud_status":1,
                  "total_water_dispensed":10200,"tds_outlet":100,"tds_inlet":200,"operational_minutes":122,
                  "ph":7.2,"tank_level":1,"trip_state":0,"error_code":0}
        else:
            self.esp32_data=self.esp32_data_current
        
        self.window = window
        self.window.attributes('-fullscreen', True)
        self.window.bind("<Escape>", lambda x:  self.window.destroy())
        self.window.geometry("768x1366")
        self.window.title(window_title)
        
        self.screen_width = self.window.winfo_screenheight()
        self.screen_height = int((self.screen_width/16)*7)
        
        # variable of event and screen counter
        self.event_counter_n = 1
        self.screen_counter_n = 1    
        self.screen_change_event=False
        
        self.canvas_icon = tk.Canvas(window, width = self.screen_height,
                         height = 20,background='white')
        
        self.canvas_icon.pack(fill=tk.BOTH,expand=1)       
        
  
        self.canvas = tk.Canvas(window, width = self.screen_height,
                         height = self.screen_width,background='white')
        
        self.canvas.pack(fill=tk.BOTH,expand=1)
        

        
        self.player = mpv.MPV(wid=str(int(self.canvas.winfo_id())), input_default_bindings=True,input_vo_keyboard=True,osc=True)

        self.player._set_property("keep-open", "always")
        self.player._set_property("video-aspect","0.633")
        self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
        
        self.update()
        self.window.mainloop()    
        
        
        
    def update(self):
        self.esp32_data_current=""
        print(self.esp32_data_current)
        
        if self.esp32_data_current!="":
            for key in self.esp32_data_current:               
                self.esp32_data[key]=self.esp32_data_current[key]
                
                
                
        if self.player._get_property("pause"):         
            self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
            self.player._set_property("pause",False)        

        self.canvas_icon.after(self.refresh_time, self.update)    
            
  
GUI(tk.Tk(), "Tkinter and OpenCV")