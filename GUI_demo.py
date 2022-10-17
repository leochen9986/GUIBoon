# import tkinter
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import time
from PIL import Image, ImageTk
import serial
import json
import os
from natsort import natsorted
import cv2
import numpy as np




replay=False

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            if ".png" in fullPath:
                allFiles.append(fullPath)
                
    return allFiles 

def get_json_data():
    '''
    ser = serial.Serial('COM5', 115200, timeout=1)
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
    '''
    data={"Motion_detected":0,"Bottle_placed":0,"wifi_status":1,"filling_status":0,"cloud_status":1,
          "total_water_dispensed":10200,"tds_outlet":100,"tds_inlet":200,"operational_minutes":122,
          "ph":7.2,"tank_level":1,"trip_state":0}
    
    return data



class GUI:
    def __init__(self, window, window_title, video_source="media/1.mp4"):
        
        self.refresh_time=3
        
        self.esp32_data=get_json_data()
        
        self.window = window
        #self.window.attributes('-fullscreen', True)
        self.window.bind("<Escape>", lambda x:  self.window.destroy())
        self.window.geometry("768x1366")
        self.window.title(window_title)
        
        self.screen_width = self.window.winfo_screenheight()
        self.screen_height = int((self.screen_width/16)*9)
        
        
        
        self.canvas = tk.Canvas(window, width = self.screen_height,
                         height = self.screen_width,background='white')
        
        self.canvas.pack(fill=tk.BOTH,expand=1)
        
        
        # variable of event and screen counter
        self.event_counter_n = 1
        self.screen_counter_n = 1
        self.total_event=len(os.listdir("media/marketing_layer"))
        self.cap_event7=cv2.VideoCapture("media/marketing_layer/event7/1_back.mp4")
        
        #proximitysensorcheck
        self.is_Proximity = False
        
        #bottlecheck
        self.is_Bottle = False
        
        #curentstate
        self.state= "default"
        
        #variable for bottleplaced delay
        self.bottle_delayed=0
        

        
        
        self.background_frame=cv2.imread("media/background.jpg")
        self.photo =  tk.PhotoImage(file = "media/background.png")
        self.container=self.canvas.create_image( 0, 0, image = self.photo, 
                             anchor = "nw")  
        
        
        #overlay ranges
        self.overlay_valueA=0.0
        self.overlay_valueB=1.0
    
        #delta slide up distance
        self.dis_delta=0
        
        #main video
        self.cap= cv2.VideoCapture("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
        self.ret, self.frame=self.cap.read()
        
    


        
        
        ###############production layer#############################
        
            #production instruction layer video
        self.cap_production_instr= cv2.VideoCapture("media/instruction.mp4")
        self.ret_production_instr, self.frame_production_instr=self.cap_production_instr.read()            
        self.idle_howto=time.time()
        self.playedvidintr=False
        self.temp_frame=self.frame_production_instr.copy()
        
        
            #loading animation
        self.cap_production_load= cv2.VideoCapture("media/Loader_Animation_Seg_03.mp4")
        self.ret_production_load, self.frame_production_load=self.cap_production_load.read()            
        self.off_bottletimer=time.time()
        
            #volume and tds label
        self.volume_var = tk.StringVar()
        self.volume_var.set("Volume:0")
        self.volume_label = tk.Label(self.canvas, textvariable=self.volume_var, width=15 ,font=("Arial", 15),bg="white")
        self.volume_label.update_idletasks()
        self.volume_label.place(x=int(self.screen_height*0.2),y=int(self.screen_width*0.75))
        self.volume_label.place_forget()
        
        
        self.tds_var = tk.StringVar()
        self.tds_var.set("TDS:0")
        self.tds_label = tk.Label(self.canvas, textvariable=self.tds_var, width=15 ,font=("Arial", 15),bg="white")
        self.tds_label.update_idletasks()
        self.tds_label.place(x=int(self.screen_height*0.2)+150,y=int(self.screen_width*0.75))
        self.tds_label.place_forget()        
        
        ###############production layer#############################
            
        
        
        ############icon layers#####################
         #wifi
        self.current_wifi="media/icons/wifi.png"
        self.wifiIMG=Image.open(self.current_wifi).resize((50, 50))
        self.wifiImage = ImageTk.PhotoImage(self.wifiIMG)
        self.wifiImage_container = self.canvas.create_image(500, 25, image=self.wifiImage)        

         #cloud
        self.current_cloud="media/icons/cloud.png"
        self.cloudIMG=Image.open(self.current_cloud).resize((50, 50))
        self.cloudImage = ImageTk.PhotoImage(self.cloudIMG)
        self.cloudImage_container = self.canvas.create_image(450, 25, image=self.cloudImage)  
        ############icon layers#####################
        
        
        #set bottle delay 3sec timer
        self.bottle_delayed=time.time()
        
        
        #testbuttons
        self.testproximity=tk.Button(self.canvas, text ="Motion", command = self.proximitytoggle)
        self.testproximitybool=False    
        self.testproximity.place(x=0,y=0)


        self.testbottle=tk.Button(self.canvas, text ="Bottle", command = self.bottletoggle)
        self.testbottlebool=False    
        self.testbottle.place(x=50,y=0)
        
        # start update
        self.update()
        self.window.mainloop()

    def update(self):

        """ refresh the content of the label every second """
        
        self.esp32_data=get_json_data()
        self.refresh_time=3
        #check wifi
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
        
        

            
        if (self.esp32_data["Motion_detected"]==0 and self.testproximitybool==False) or self.state=="bottleplaced" or self.state=="bottledelayed" or self.state=="bottleremoved":
            self.ret, self.frame=self.cap.read()
            self.ret7, self.frame7=self.cap_event7.read()
            
            
        if self.ret:
            h, w ,_= self.frame.shape
            
            #Screen 1a
            if self.esp32_data["Motion_detected"]==1 or self.testproximitybool==True or self.state=="bottleplaced":
                
                if self.state=="default":
                    #print("Motion_detected")
                    if self.overlay_valueA<=0.5:
                        self.overlay_valueA+=0.01
                        
                    if self.overlay_valueB>=0.5:
                        self.overlay_valueB-=0.01  
                        
                    else:
                        if self.dis_delta <20:
                            
                            self.dis_delta+=1
                            self.frame[:h-self.dis_delta, :] = self.frame[self.dis_delta:, :]
                            self.frame[h-self.dis_delta:, :] = 0
                        elif self.state=="default":
                            self.state="proximity"
                            #self.idle_howto=time.time()
                            
                        #read production layer instruction video

                            
                            
                            
                
                #Screen 2            
                elif (self.esp32_data["Bottle_placed"]==1 or self.testbottlebool==True or self.state=="bottleplaced") and not self.state=="bottleremoved":
                    
                    '''
                    self.overlay_valueA=0.0
                    self.overlay_valueA=1.0
                    self.dis_delta=20
                    
                    
                    if self.overlay_valueA>0.0:
                        self.overlay_valueA-=0.01
                        
                    if self.overlay_valueB<1.0:
                        self.overlay_valueB+=0.01                      

                    else:
                        if self.dis_delta <20:
                            
                            self.dis_delta+=1

                        else:
                            '''
                            
                    if self.state=="proximity":
                        self.state="bottleplaced"
                        self.cap.release()
                        self.screen_counter_n=2
                        self.cap= cv2.VideoCapture("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                        self.ret, self.frame=self.cap.read()
                        self.bottle_delayed=time.time()
                        
                        #release instuction vid
                        self.cap_production_instr.release()
                        self.cap_production_instr= cv2.VideoCapture("media/instruction.mp4")
                        self.ret_production_instr, self.frame_production_instr=self.cap_production_instr.read()
                            
                                
                                
                        
                    self.refresh_time=33        
                    #parameter values
                    self.volume_var.set("Volume:"+str(self.esp32_data["total_water_dispensed"]))
                    self.volume_label.update_idletasks()

                    self.tds_var.set("TDS:"+str(self.esp32_data["tds_outlet"]))
                    self.tds_label.update_idletasks()

                    self.volume_label.place(x=int(self.screen_height*0.2),y=int(self.screen_width*0.75))
                    self.tds_label.place(x=int(self.screen_height*0.2)+200,y=int(self.screen_width*0.75))
                    
                    

                    if self.esp32_data["Bottle_placed"]==1 or self.testbottlebool==True:
                        self.off_bottletimer=time.time()
                    else:
                        if time.time()-self.off_bottletimer > 5:
                            self.state="bottledelayed" 
                            self.refresh_time=3                                   
                                            
                            
 
                        
                        
                if self.state=="bottleplaced":
                    self.added_image=self.frame.copy()
                    
                elif self.state=="proximity":
                    self.added_image=self.temp_frame.copy()                        
                    
                else :
                    self.overlay =self.frame.copy()
                    #self.added_image = cv2.addWeighted(self.background_frame,self.overlay_valueA,self.overlay,self.overlay_valueB,0)
                    self.added_image=self.background_frame.copy()
                    
                    self.overlay_hsv = cv2.cvtColor(self.overlay, cv2.COLOR_BGR2HSV)
                    self.h,self.s,self.v = cv2.split(self.overlay_hsv)     
                    #self.v2=cv2.merge([self.v, self.v, self.v])
                    #self.added_image[self.v>0]=(self.overlay[self.v>0]*20)

                    self.added_image[self.v>=50]=self.overlay[self.v>=50]
                    self.added_image = cv2.addWeighted(self.background_frame,self.overlay_valueA,self.added_image,self.overlay_valueB,0)
                    self.temp_frame=self.added_image.copy()
                    

                    
                
                
                #production instruction video
                if self.state=="proximity":
                    self.ret_production_instr, self.frame_production_instr=self.cap_production_instr.read()
                    
                    if self.ret_production_instr ==False:
                        self.idle_howto=time.time()
                        self.cap_production_instr.release()
                        self.cap_production_instr= cv2.VideoCapture("media/instruction.mp4")
                        self.ret_production_instr, self.frame_production_instr=self.cap_production_instr.read()   
                        self.playedvidintr=True
                    
                    
                    self.overlay_instruc =self.frame_production_instr.copy()
                    self.overlay_hsv_instruc = cv2.cvtColor(self.overlay_instruc, cv2.COLOR_BGR2HSV)
                    self.h_i,self.s_i,self.v_i = cv2.split(self.overlay_hsv_instruc)   
                    self.added_image[self.v_i>=50]=self.overlay_instruc[self.v_i>=50]
                    
                    self.added_image = cv2.addWeighted(self.added_image,self.overlay_valueA,self.frame_production_instr,0.9,0)
                    
                    #if idle for more than 20sec
                    if self.playedvidintr:
                        if time.time()-self.idle_howto>2:
                            self.state="default"
                            self.idle_howto=time.time()
                            self.cap_production_instr.release()
                            self.cap_production_instr= cv2.VideoCapture("media/instruction.mp4")
                            self.ret_production_instr, self.frame_production_instr=self.cap_production_instr.read()     
                            #reset all status
                            self.testproximitybool=False
                            self.testbottlebool=False
                            self.playedvidintr=False
                            
               
                        
                
                
                self.added_image=cv2.resize(self.added_image,(self.screen_height,self.screen_width))
                self.cv2image= cv2.cvtColor(self.added_image,cv2.COLOR_BGR2RGB)
                self.img = Image.fromarray(self.cv2image)
                self.imgtk = ImageTk.PhotoImage(image = self.img)
                self.canvas.itemconfig( self.container,image =self.imgtk) 
                
                
            else:
          
                #Screen3
                if self.state=="bottledelayed":
                    self.state="bottleremoved"
                    self.cap.release()
                    self.screen_counter_n=3
                    self.cap= cv2.VideoCapture("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
                    self.ret, self.frame=self.cap.read()
                    
                    #release loading video
                    self.cap_production_load.release()
                    self.cap_production_load= cv2.VideoCapture("media/Loader_Animation_Seg_03.mp4")
                    self.ret_production_load, self.frame_production_load=self.cap_production_load.read() 
                    self.added_image=self.background_frame.copy()
                    
                    #hide the volume tds label
                    self.tds_label.place_forget() 
                    self.volume_label.place_forget()
                    

                #Screen3
                elif self.state=="bottleremoved":
                    self.frame[:h-190, :] = self.frame[190:, :]
                    self.frame[h-190:, :] = 0   
                    
                    self.overlay =self.frame.copy()
                    #self.added_image = cv2.addWeighted(self.background_frame,self.overlay_valueA,self.overlay,self.overlay_valueB,0)
                    self.added_image=self.background_frame.copy()
                    
                    self.overlay_hsv = cv2.cvtColor(self.overlay, cv2.COLOR_BGR2HSV)
                    self.h,self.s,self.v = cv2.split(self.overlay_hsv)     
                    #self.v2=cv2.merge([self.v, self.v, self.v])
                    #self.added_image[self.v>0]=(self.overlay[self.v>0]*20)

                    self.added_image[self.v>=50]=self.overlay[self.v>=50]                            
                    
                    
                    #self.overlay =self.frame.copy()
                    #self.added_image = cv2.addWeighted(self.background_frame,self.overlay_valueA,self.overlay,self.overlay_valueB,0)
                    self.added_image=cv2.resize(self.added_image,(self.screen_height,self.screen_width))
                    self.cv2image= cv2.cvtColor(self.added_image,cv2.COLOR_BGR2RGB)
                    self.img = Image.fromarray(self.cv2image)
                    self.imgtk = ImageTk.PhotoImage(image = self.img)
                    self.canvas.itemconfig( self.container,image =self.imgtk)                         
                    
                else:
                    #Screen1
                    
                    self.overlay =self.frame.copy()
                    #self.added_image = cv2.addWeighted(self.background_frame,self.overlay_valueA,self.overlay,self.overlay_valueB,0)
                    self.added_image=self.background_frame.copy()
                    
                    self.overlay_hsv = cv2.cvtColor(self.overlay, cv2.COLOR_BGR2HSV)
                    self.h,self.s,self.v = cv2.split(self.overlay_hsv)     
                    #self.v2=cv2.merge([self.v, self.v, self.v])
                    #self.added_image[self.v>0]=(self.overlay[self.v>0]*20)
                    
                    if self.event_counter_n==7:
                        self.added_image[self.v>=8]=self.frame7[self.v>=8]   
                    else:
                        self.added_image[self.v>=50]=self.overlay[self.v>=50]   
                                         
                    
                    
                    self.resized_frame=cv2.resize(self.added_image,(self.screen_height,self.screen_width))
                    self.cv2image= cv2.cvtColor(self.resized_frame,cv2.COLOR_BGR2RGB)
                    self.img = Image.fromarray(self.cv2image)
                    self.imgtk = ImageTk.PhotoImage(image = self.img)
                    self.canvas.itemconfig( self.container,image =self.imgtk)
        
        else:
            self.cap.release()
            self.cap_event7.release()
            self.cap_event7=cv2.VideoCapture("media/marketing_layer/event7/1_back.mp4")
            #return screen1
            if self.state=="bottleremoved":
                self.state="default"
                self.cap.release()
                self.cap_event7.release()
                self.cap_event7=cv2.VideoCapture("media/marketing_layer/event7/1_back.mp4")                
                self.screen_counter_n=1
                self.dis_delta=0
                self.refresh_time=20000
                
            
            #change Screen 1 video
            if self.event_counter_n==self.total_event and self.state=="default":
                self.event_counter_n=0
            
            if self.esp32_data["Bottle_placed"]==0 and self.state=="default":
                self.event_counter_n+=1
                
            self.cap= cv2.VideoCapture("media/marketing_layer/event{}/{}.mp4".format(self.event_counter_n,self.screen_counter_n))
          
            
        self.window.after(self.refresh_time, self.update)
        

    
    def proximitytoggle(self):
        if self.testproximitybool==False:
            self.testproximitybool=True
        else:
            self.testproximitybool=False
        return

    def bottletoggle(self):
        if self.testbottlebool==False:
            self.testbottlebool=True
            self.testproximitybool=True
        else:
            self.testbottlebool=False
            self.testproximitybool=False
        return


GUI(tk.Tk(), "Tkinter and OpenCV")
