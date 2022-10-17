import tkinter as tk
import mpv
  
root=tk.Tk()
root.geometry("500x280")
player = mpv.MPV(wid=str(int(root.winfo_id())), input_default_bindings=True,input_vo_keyboard=True,osc=True)
player.play('/home/rainer/Videos/Garage62-2021-02-06__09-16-51.mkv')
  
tk.mainloop()