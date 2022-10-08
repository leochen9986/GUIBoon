import tkinter as tk
import mpv
import time
from time import sleep
from PIL import Image, ImageTk
import serial
import json
def get_json_data():

    data=""


    ser = serial.Serial('/dev/ttyUSB1', 9600,timeout=1)
        

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
            if time.time()-timer > 1.5:
                return ""
        
    data = json.loads(data)
        

    '''
    if ser.in_waiting == 0:
        for i in "hello":
            ser.write(i.encode())
            print("write")
            time.sleep(2)
    '''

    return data

while True:
        print(get_json_data())




{"Motion_detected":0,"Bottle_placed":0,"wifi_status":1,"filling_status":0,"cloud_status":1,"total_water_dispensed":10200,"tds_outlet":100,"tds_inlet":200,"operational_minutes":122,"ph":7.2,"tank_level":1,"trip_state":0}
