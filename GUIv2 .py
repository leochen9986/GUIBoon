import tkinter as tk
import mpv
import time
from PIL import Image, ImageTk
import serial
import json
def get_json_data():

    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.reset_input_buffer()
    data=""
    while True:
        
        if ser.in_waiting > 0:
           
            line = ser.readline().decode('utf-8').rstrip()
            if line.strip()!="":
                data+=line
                
            
            if line.strip()=="}":
                break
    data = json.loads(data)

    return data


class GUI:
    def __init__(self, window, window_title, video_source="media/1.mp4"):
        
        self.refresh_time=300
        
        self.esp32_data=get_json_data()        
        
        self.window = window
        #self.window.attributes('-fullscreen', True)
        self.window.bind("<Escape>", lambda x:  self.window.destroy())
        self.window.geometry("768x1366")
        self.window.title(window_title)
        
        self.screen_width = self.window.winfo_screenheight()
        self.screen_height = int((self.screen_width/16)*8.5)
        
        # variable of event and screen counter
        self.event_counter_n = 1
        self.screen_counter_n = 1        
        
        self.canvas_icon = tk.Canvas(window, width = self.screen_height,
                         height = 50,background='white')
        
        self.canvas_icon.pack()       
        
  
        self.canvas = tk.Canvas(window, width = self.screen_height,
                         height = self.screen_width,background='white')
        
        self.canvas.pack()
        

        
        self.player = mpv.MPV(wid=str(int(self.canvas.winfo_id())), vo='x11')

        self.player._set_property("keep-open", "always")
        self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
        self.player._set_property("pause",True)        

        #proximitysensorcheck
        self.is_Proximity = False
        
        #bottlecheck
        self.is_Bottle = False
        
        #curentstate
        self.state= "default"
        
        #variable for bottleplaced delay
        self.bottle_delayed=0
        self.photo =  tk.PhotoImage(file = "media/background.png")
        self.container=self.canvas.create_image( 0, 0, image = self.photo, 
                             anchor = "nw")  
        
        
        ###############production layer#############################
        
            #production instruction layer video
        self.idle_howto=time.time()
        self.playedvidintr=False

        
        
            #loading animation
        self.off_bottletimer=time.time()
        
            #volume and tds label
        self.volume_var = tk.StringVar()
        self.volume_var.set("Volume:0")
        self.volume_label = tk.Label(self.window, textvariable=self.volume_var, width=15 ,font=("Arial", 15),bg="white")
        self.volume_label.update_idletasks()
        self.volume_label.place(x=int(self.screen_height*0.35),y=int(self.screen_width*0.73))
        self.volume_label.place_forget()
        
        
        self.tds_var = tk.StringVar()
        self.tds_var.set("TDS:0")
        self.tds_label = tk.Label(self.window, textvariable=self.tds_var, width=15 ,font=("Arial", 15),bg="white")
        self.tds_label.update_idletasks()
        self.tds_label.place(x=int(self.screen_height*0.35)+160,y=int(self.screen_width*0.73))
        self.tds_label.place_forget()        
        
        ###############production layer#############################        
        

        ############icon layers#####################
         #wifi
        self.current_wifi="media/icons/wifi.png"
        self.wifiIMG=Image.open(self.current_wifi).resize((50, 50))
        self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
        self.wifiImage_container = self.canvas_icon.create_image(500, 25, image=self.wifiImage)        

         #cloud
        self.current_cloud="media/icons/cloud.png"
        self.cloudIMG=Image.open(self.current_cloud).resize((50, 50))
        self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
        self.cloudImage_container = self.canvas_icon.create_image(450, 25, image=self.cloudImage)  
        ############icon layers#####################
        
        
        #set bottle delay 3sec timer
        self.bottle_delayed=time.time()
        
    

        
        self.update()
        self.window.mainloop()
        
        
    def update(self):

        """ refresh the content of the label every second """
        self.esp32_data=get_json_data()
        if self.esp32_data["wifi_status"]==1 and self.current_wifi=="media/icons/nowifi.png":
            self.current_wifi="media/icons/wifi.png"
            self.wifiIMG=Image.open(self.current_wifi).resize((50, 50))
            self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
            self.canvas.itemconfig( self.wifiImage_container,image =self.wifiImage)  
            
        elif self.esp32_data["wifi_status"]==0 and self.current_wifi=="media/icons/wifi.png":
            self.current_wifi="media/icons/nowifi.png"
            self.wifiIMG=Image.open(self.current_wifi).resize((50, 50))
            self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
            self.canvas.itemconfig( self.wifiImage_container,image =self.wifiImage)             

        #check cloud
        if self.esp32_data["cloud_status"]==1 and self.current_wifi=="media/icons/nocloud.png":
            self.current_cloud="media/icons/cloud.png"
            self.cloudIMG=Image.open(self.current_cloud).resize((50, 50))
            self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
            self.canvas.itemconfig( self.cloudImage_container,image =self.cloudImage)  
            
        elif self.esp32_data["cloud_status"]==0 and self.current_wifi=="media/icons/cloud.png":
            self.current_wifi="media/icons/nocloud.png"
            self.wifiIMG=Image.open(self.current_cloud).resize((50, 50))
            self.wifiImage = ImageTk.PhotoImage(self.cloudIMG)
            self.canvas.itemconfig( self.cloudImage_container,image =self.cloudImage)  



        
        #print(self.testproximitybool)
        #Screen1
        if self.esp32_data["Motion_detected"]==0:
            if self.player._get_property("pause") or self.state!="default":
                
                #screen 3
                if self.state=="bottleplaced":
                    if time.time()-self.off_bottletimer>5:
                        self.state="default"
                        self.screen_counter_n=3
                        self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                        self.player._set_property("pause",False)
                        self.volume_label.place_forget()
                        self.tds_label.place_forget()
                
                else:
                    self.state="default"
                    self.screen_counter_n=1
                    self.event_counter_n+=1
                    if self.event_counter_n>7:
                        self.event_counter_n=1
                        
                    self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                    self.player._set_property("pause",False)

        #Screen Instrcution
        elif (self.esp32_data["Motion_detected"]==1 ) and (self.esp32_data["Bottle_placed"]==0) :
            
            if self.player._get_property("pause") or self.state=="default":
                self.player.play("media/instruction.mp4")
                self.player._set_property("pause",False)
                
                if self.state=="default":
                    self.state="proximity"
                    self.idle_howto=time.time()
                    
                    
            #print(self.state=="bottleplaced")         
            if self.state=="proximity":
   
                if time.time()-self.idle_howto>20:
                    self.testproximitybool=False 


        #Screen 2
        elif self.esp32_data["Bottle_placed"]==1:
            #parameter values
            self.volume_var.set("Volume:"+str(self.esp32_data["total_water_dispensed"]))
            self.volume_label.update_idletasks()

            self.tds_var.set("TDS:"+str(self.esp32_data["tds_outlet"]))
            self.tds_label.update_idletasks()

            self.volume_label.place(x=int(self.screen_height*0.35),y=int(self.screen_width*0.73))
            self.tds_label.place(x=int(self.screen_height*0.35)+200,y=int(self.screen_width*0.73))
            
            if self.player._get_property("pause") or self.state=="proximity":
                self.screen_counter_n=2
                self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                self.player._set_property("pause",False)
                
                
                if self.state=="proximity":
                    self.state="bottleplaced"
                    self.off_bottletimer
                    
                          
            
            
            
        self.canvas_icon.after(self.refresh_time, self.update)        

        

GUI(tk.Tk(), "Tkinter and OpenCV")
