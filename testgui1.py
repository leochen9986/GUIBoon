import tkinter as tk
import mpv
  
root=tk.Tk()
root.geometry("768x1366")
player = mpv.MPV(wid=str(int(root.winfo_id())), input_default_bindings=True,input_vo_keyboard=True,osc=True)
player.play("media/marketing_layer/event1/1.mp4")
  
tk.mainloop()