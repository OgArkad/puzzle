import sys
import tkinter as tk
from PIL import Image, ImageTk
import os
from tkinter.filedialog import askopenfilename
import random

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

parent = tk.Tk()
parent.title("Puzzle Master")
parent.configure(bg="#1e1e24")

width = parent.winfo_screenwidth()
height = parent.winfo_screenheight()
parent.geometry(f"{width}x{height}")

current_photo = None
puzzle_pieces = []  
floating_labels = []  

drag_data = {"start_x": 0, "start_y": 0, "widget_x": 0, "widget_y": 0, "item": None}

def play_snap_sound():
    if HAS_WINSOUND:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    else:
        parent.bell()

def on_drag_start(event):
    widget = event.widget
    if getattr(widget, 'locked', False):
        return
    drag_data["item"] = widget
    drag_data["start_x"] = event.x_root
    drag_data["start_y"] = event.y_root
    drag_data["widget_x"] = widget.winfo_x()
    drag_data["widget_y"] = widget.winfo_y()
    widget.lift()

def on_drag_motion(event):
    widget = drag_data.get("item")
    if widget and not getattr(widget, 'locked', False):
        delta_x = event.x_root - drag_data["start_x"]
        delta_y = event.y_root - drag_data["start_y"]
        new_x = drag_data["widget_x"] + delta_x
        new_y = drag_data["widget_y"] + delta_y
        widget.place(x=new_x, y=new_y)

def on_drag_end(event):
    widget = drag_data.get("item")
    if not widget or getattr(widget, 'locked', False):
        return
    
    label_x = image_label.winfo_x()
    label_y = image_label.winfo_y()
    
    target_x = label_x + widget.target_offset_x
    target_y = label_y + widget.target_offset_y
    
    current_x = widget.winfo_x()
    current_y = widget.winfo_y()
    
    strict_snap_distance = 15
    if abs(current_x - target_x) < strict_snap_distance and abs(current_y - target_y) < strict_snap_distance:
        widget.place(x=target_x, y=target_y)
        widget.locked = True
        widget.config(highlightthickness=0) 
        play_snap_sound()
        check_win_condition()
        
    drag_data["item"] = None

def check_win_condition():
    all_locked = all(getattr(lbl, 'locked', False) for lbl in floating_labels)
    if all_locked and floating_labels:
        win_label = tk.Label(parent, text="Собрано! Великолепно!", font=("Arial", 32, "bold"), fg="#4ade80", bg="#1e1e24")
        win_label.place(relx=0.5, rely=0.08, anchor="center")

def open_file():
    file_path = askopenfilename()
    global current_photo, puzzle_pieces, floating_labels
    
    if file_path:
        for lbl in floating_labels:
            lbl.destroy()
        floating_labels.clear()
        puzzle_pieces.clear()

        pil_image = Image.open(file_path)
        img_w, img_h = pil_image.size

        max_allowed_w = int(width * 0.55)
        max_allowed_h = int(height * 0.70)

        ratio_w = max_allowed_w / img_w
        ratio_h = max_allowed_h / img_h
        scale_factor = min(ratio_w, ratio_h)

        new_width = int(img_w * scale_factor)
        new_height = int(img_h * scale_factor)
        
        resized_pil = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        bw_pil = resized_pil.convert("L") 
        
        current_photo = ImageTk.PhotoImage(bw_pil)
        image_label.config(image=current_photo)
        
        try:
            rows = int(rows_entry.get())
            cols = int(cols_entry.get())
            if rows <= 0 or cols <= 0: raise ValueError
        except ValueError:
            rows, cols = 4, 4
            rows_entry.delete(0, tk.END); rows_entry.insert(0, "4")
            cols_entry.delete(0, tk.END); cols_entry.insert(0, "4")

        piece_w = max(1, new_width // cols)
        piece_h = max(1, new_height // rows)
        
        parent.update_idletasks()
        
        for r in range(rows):
            for c in range(cols):
                box = (c * piece_w, r * piece_h, (c + 1) * piece_w, (r + 1) * piece_h)
                piece_img = resized_pil.crop(box)
                
                tk_piece = ImageTk.PhotoImage(piece_img)
                puzzle_pieces.append(tk_piece)  
                
                piece_label = tk.Label(parent, image=tk_piece, highlightbackground="#4b5563", highlightcolor="#4b5563", highlightthickness=1, bd=0)
                floating_labels.append(piece_label)
                
                piece_label.target_offset_x = c * piece_w
                piece_label.target_offset_y = r * piece_h
                piece_label.locked = False
                
                piece_label.bind("<Button-1>", on_drag_start)
                piece_label.bind("<B1-Motion>", on_drag_motion)
                piece_label.bind("<ButtonRelease-1>", on_drag_end)
                
                left_min, left_max = 30, int(width * 0.18)
                if left_max <= left_min: left_max = left_min + 20
                
                right_min = int(width * 0.78)
                right_max = width - piece_w - 40
                if right_max <= right_min: right_max = right_min + 20
                
                y_min = controls_frame.winfo_y() + controls_frame.winfo_height() + 40
                y_max = height - piece_h - 60
                if y_max <= y_min: y_max = y_min + 20

                zone = random.choice(["left", "right"])
                if zone == "left":
                    random_x = random.randint(left_min, left_max)
                else:
                    random_x = random.randint(right_min, right_max)
                    
                random_y = random.randint(y_min, y_max)
                
                piece_label.place(x=random_x, y=random_y)

controls_frame = tk.Frame(parent, bg="#27272a", padx=20, pady=12, highlightbackground="#3f3f46", highlightthickness=1)
controls_frame.pack(anchor="nw", padx=40, pady=25)

open_button = tk.Button(
    controls_frame, 
    text="Open Image", 
    command=open_file, 
    font=("Arial", 11, "bold"),
    bg="#2563eb", 
    fg="white", 
    activebackground="#1d4ed8", 
    activeforeground="white",
    bd=0, 
    cursor="hand2",
    padx=22, 
    pady=9
)
open_button.pack(side="left")

style_font = ("Arial", 11)
label_cfg = {"bg": "#27272a", "fg": "#f4f4f5", "font": style_font}
entry_cfg = {"bg": "#09090b", "fg": "white", "insertbackground": "white", "font": style_font, "bd": 0, "highlightthickness": 1, "highlightbackground": "#52525b", "justify": "center"}

rows_label = tk.Label(controls_frame, text="Grid Rows:", **label_cfg)
rows_label.pack(side="left", padx=(30, 10))
rows_entry = tk.Entry(controls_frame, width=5, **entry_cfg)
rows_entry.insert(0, "4")
rows_entry.pack(side="left", ipady=5)

cols_label = tk.Label(controls_frame, text="Grid Cols:", **label_cfg)
cols_label.pack(side="left", padx=(25, 10))
cols_entry = tk.Entry(controls_frame, width=5, **entry_cfg)
cols_entry.insert(0, "4")
cols_entry.pack(side="left", ipady=5)

image_label = tk.Label(parent, bg="#1e1e24")
image_label.pack(expand=True, fill="both")

if os.path.exists('secret.png'):
    image = Image.open('secret.png')
    image = ImageTk.PhotoImage(image)
    image_label.config(image=image)
else:
    fallback_img = Image.new("RGB", (400, 300), "#27272a")
    image = ImageTk.PhotoImage(fallback_img)
    image_label.config(image=image)

parent.mainloop()
