import tkinter as tk
import mpv
import time
from PIL import Image, ImageTk
import serial
import json

'''   
def get_json_data():

    try:

        data=""


        ser = serial.Serial('/dev/ttyUSB0', 9600,timeout=1)
        ser.reset_input_buffer()
        #line = ser.readline().decode('utf-8').rstrip()
        timer=time.time()

        while True:
            
            if ser.in_waiting > 0:
               
                line = ser.readline().decode('utf-8').rstrip()

                
                if line.strip()!="":
                    data+=line
                    #print(line)
                else:
                    data=""
                    return data
                    
                
                if "}" in line.strip():
                    break
           
            else:
                if time.time()-timer > 3:
                    return ""
            
        print(data)
        data = json.loads(data.strip().replace("}{",","))
            
        return data
    except Exception as e:
        print(e)
        return ""
'''

class GUI:
    def __init__(self, window, window_title, video_source="media/1.mp4"):
        
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
         
        
  
        self.canvas = tk.Canvas(window, width = self.screen_height,
                         height = self.screen_width,background='white')
        
        self.canvas.pack(fill=tk.BOTH,expand=1)
        

        
        self.player = mpv.MPV(wid=str(int(self.canvas.winfo_id())), vo='x11')

        self.player._set_property("keep-open", "always")
        self.player._set_property("video-aspect","0.633")
        self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
        self.player._set_property("pause",True)        

        #proximitysensorcheck
        self.is_Proximity = False
        
        #bottlecheck
        self.is_Bottle = False
        
        #curentstate
        self.state= "default"
        

        
        #set bottle delay 3sec timer
        self.bottle_delayed=time.time()
        
    

        
        self.update()
        self.window.mainloop()
        
        
    def update(self):


        #Screen1
        if self.esp32_data["Motion_detected"]==0 and (self.state=="default" or self.state=="bottleplaced"):
            if self.player._get_property("pause") or self.state!="default":
                
                

                    self.state="default"
                    self.screen_counter_n=1
                    
                    if self.screen_change_event:
                        self.event_counter_n+=1
                        if self.event_counter_n>7:
                            self.event_counter_n=1
                        self.screen_change_event=False
                        
                        
                    self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                    self.player._set_property("pause",False)


            
            
        self.canvas_icon.after(self.refresh_time, self.update)        

        

GUI(tk.Tk(), "Tkinter and OpenCV")
