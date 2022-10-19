import tkinter as tk
import mpv
import time
from PIL import Image, ImageTk
import serial
import json

    
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
        self.player._set_property("pause",True)        

        #proximitysensorcheck
        self.is_Proximity = False
        
        #bottlecheck
        self.is_Bottle = False
        
        #curentstate
        self.state= "default"
        
        #variable for bottleplaced delay
        self.bottle_delayed=0
        #self.photo =  tk.PhotoImage(file = "media/background.png")
        #self.container=self.canvas.create_image( 0, 0, image = self.photo, 
                             #anchor = "nw")  
        
        
        ###############production layer#############################
        
            #production instruction layer video
        self.idle_howto=time.time()
        self.playedvidintr=False

        
        
            #loading animation
        self.off_bottletimer=time.time()
        
            #volume and tds label
        self.volume_var = tk.StringVar()
        self.volume_var.set("Volume:0")
        self.volume_label = tk.Label(self.window, textvariable=self.volume_var, width=12 ,font=("Arial", 12),bg="white")
        self.volume_label.update_idletasks()
        self.volume_label.place(x=int(self.screen_height*0.35),y=int(self.screen_width*0.73))
        self.volume_label.place_forget()
        
        
        self.tds_var = tk.StringVar()
        self.tds_var.set("TDS:0")
        self.tds_label = tk.Label(self.window, textvariable=self.tds_var, width=15 ,font=("Arial", 35),bg="white")
        self.tds_label.update_idletasks()
        self.tds_label.place(x=int(self.screen_height*0.35)+160,y=int(self.screen_width*0.73))
        self.tds_label.place_forget()        

	
        self.ph_var = tk.StringVar()
        self.ph_var.set("pH:0")
        self.ph_label = tk.Label(self.window, textvariable=self.ph_var, width=15 ,font=("Arial", 35),bg="white")
        self.ph_label.update_idletasks()
        self.ph_label.place(x=int(self.screen_height*0.35)+160,y=int(self.screen_width*0.73))
        self.ph_label.place_forget()  
        
        ###############production layer#############################        
        

        ############icon layers#####################
         #wifi
        self.current_wifi="media/icons/wifi.png"
        self.wifiIMG=Image.open(self.current_wifi).resize((20, 20))
        self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
        self.wifiImage_container = self.canvas_icon.create_image(1150, 10, image=self.wifiImage)        

         #cloud
        self.current_cloud="media/icons/cloud.png"
        self.cloudIMG=Image.open(self.current_cloud).resize((20, 20))
        self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
        self.cloudImage_container = self.canvas_icon.create_image(1120, 10, image=self.cloudImage)  

        #alert
        self.alert_var = tk.StringVar()
        self.alert_var.set("0")
        self.alert_label = tk.Label(self.canvas_icon, textvariable=self.alert_var, width=5 ,font=("Arial", 10),bg="white")
        self.alert_label.update_idletasks()
        self.alert_label.place(x=1070,y=1)              
        #treated water
        self.treatedvolume_var = tk.StringVar()
        self.treatedvolume_var.set("Treated Water: 0")
        self.treatedvolume_label = tk.Label(self.canvas_icon, textvariable=self.treatedvolume_var, width=20 ,font=("Arial", 10),bg="white")
        self.treatedvolume_label.update_idletasks()
        self.treatedvolume_label.place(x=10,y=1)  

        ############icon layers#####################
        
        
        #set bottle delay 3sec timer
        self.bottle_delayed=time.time()
        
    

        
        self.update()
        self.window.mainloop()
        
        
    def update(self):

        """ refresh the content of the label every second """
        
        
        self.esp32_data_current=get_json_data()
        print(self.esp32_data_current)
        
        if self.esp32_data_current!="":
            for key in self.esp32_data_current:               
                self.esp32_data[key]=self.esp32_data_current[key]

        
        
        
        if self.esp32_data["wifi_status"]==1 and self.current_wifi=="media/icons/nowifi.png":
            self.current_wifi="media/icons/wifi.png"
            self.wifiIMG=Image.open(self.current_wifi).resize((20, 20))
            self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
            self.canvas_icon.itemconfig( self.wifiImage_container,image =self.wifiImage)  
            
        elif self.esp32_data["wifi_status"]==0 and self.current_wifi=="media/icons/wifi.png":
            self.current_wifi="media/icons/nowifi.png"
            self.wifiIMG=Image.open(self.current_wifi).resize((20, 20))
            self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
            self.canvas_icon.itemconfig( self.wifiImage_container,image =self.wifiImage)             

        #check cloud
        if self.esp32_data["cloud_status"]==1 and self.current_cloud=="media/icons/nocloud.png":
            self.current_cloud="media/icons/cloud.png"
            self.cloudIMG=Image.open(self.current_cloud).resize((20, 20))
            self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
            self.canvas_icon.itemconfig( self.cloudImage_container,image =self.cloudImage)  
            
        elif self.esp32_data["cloud_status"]==0 and self.current_cloud=="media/icons/cloud.png":
            self.current_cloud="media/icons/nocloud.png"
            self.cloudIMG=Image.open(self.current_cloud).resize((20, 20))
            self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
            self.canvas_icon.itemconfig( self.cloudImage_container,image =self.cloudImage)  

        #update alert icon
        self.alert_var.set(str(self.esp32_data["error_code"]))
        self.alert_label.update_idletasks()
        
        #update treated volume
        self.treatedvolume_var.set("Treated Water: "+str(self.esp32_data["total_water_dispensed"]))
        self.treatedvolume_label.update_idletasks()

        
        #print(self.testproximitybool)
        #Screen1
        if self.esp32_data["Motion_detected"]==0 and (self.state=="default" or self.state=="bottleplaced"):
            if self.player._get_property("pause") or self.state!="default":
                
                #screen 3
                if self.state=="bottleplaced":
                    
                    if self.esp32_data["filling_status"]!=0:
                        self.off_bottletimer=time.time()
                        
                    if time.time()-self.off_bottletimer>5:
                        self.state="default"
                        self.screen_counter_n=3
                        self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                        self.player._set_property("pause",False)
                        self.volume_label.place_forget()
                        self.tds_label.place_forget()
                        self.ph_label.place_forget()
                        self.screen_change_event=True
                
                else:
                    self.state="default"
                    self.screen_counter_n=1
                    
                    if self.screen_change_event:
                        self.event_counter_n+=1
                        if self.event_counter_n>7:
                            self.event_counter_n=1
                        self.screen_change_event=False
                        
                        
                    self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                    self.player._set_property("pause",False)

        #Screen Instrcution
        elif (self.esp32_data["Motion_detected"]==1 or  self.state=="proximity") and (self.esp32_data["Bottle_placed"]==0) :
            
            if self.player._get_property("pause") or self.state=="default":
                self.player.play("media/instruction.mp4")
                self.player._set_property("pause",False)
                
                if self.state=="default":
                    self.state="proximity"
                    self.idle_howto=time.time()
                    
                    
            #print(self.state=="bottleplaced")         
            if self.state=="proximity":
   
                if time.time()-self.idle_howto>20:
                    self.state="default"


        #Screen 2
        elif self.esp32_data["Bottle_placed"]==1:
            #parameter values
            #self.volume_var.set("Volume:"+str(self.esp32_data["total_water_dispensed"]))
            #self.volume_label.update_idletasks()

            self.tds_var.set("TDS:"+str(self.esp32_data["tds_inlet"])+"~"+str(self.esp32_data["tds_outlet"]))
            self.tds_label.update_idletasks()

            #self.volume_label.place(x=int(self.screen_height*0.35),y=int(self.screen_width*0.73))
            self.tds_label.place(x=int(self.screen_height*0.35)-100,y=int(self.screen_width*0.75))
            self.ph_label.place(x=int(self.screen_height*0.35)+300,y=int(self.screen_width*0.75))
            
            if self.player._get_property("pause") or self.state=="proximity":
                self.screen_counter_n=2
                self.player.play("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                self.player._set_property("pause",False)
                
                
                if self.state=="proximity":
                    self.state="bottleplaced"
                    self.off_bottletimer=time.time()
                    
                          
            
            
            
        self.canvas_icon.after(self.refresh_time, self.update)        

        

GUI(tk.Tk(), "Tkinter and OpenCV")
