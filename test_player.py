import tkinter as tk
import mpv

root=tk.Tk()
root.geometry("720x1280")

canvas = tk.Canvas(root, width = 720,
                 height = 1280,background='white')

canvas.pack()

volume_var = tk.StringVar()
volume_var.set("Volume:0")
volume_label = tk.Label(root, textvariable=volume_var, width=15 ,font=("Arial", 15),bg="white")
volume_label.update_idletasks()
volume_label.place(x=int(100),y=int(100))

player = mpv.MPV(wid=str(int(canvas.winfo_id())), vo='x11')
player.play("media/marketing_layer/event2/2.mp4")



tk.mainloop()

print('calling player.terminate.')
player.quit()
print('terminate player.returned.')