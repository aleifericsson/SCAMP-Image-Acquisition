##########################################################################
# SCAMP Vision Chip Development System Library
# -----------------------------------------------------------------------
# Copyright (c) 2020 The University of Manchester. All Rights Reserved.
# 
##########################################################################

import io
import time
import scamp
import os
import datetime
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import numpy as np
from PIL import Image
import colorsys
import threading

def process_packet(packet):
    global DisplayCanvas, DisplayImage, DisplayCanvasImageID
    global RGBCanvas, RGBImage, RGBCanvasImageID
    global current_color
    global red_temp, green_temp, blue_temp
    global recording_frame_num

    if packet['type']=='data':
    
        lc = packet['loopcounter']
        datatype = packet['datatype']
        
        if datatype == 'TEXT':
            print('[%d] text: %s' % (lc, repr(packet['text'])))
            extract_color(repr(packet['text']))
            # None
            
        elif datatype == 'SCAMP5_AOUT':
            w = packet['width']
            h = packet['height']

            # Load grayscale
            imgL = (
                Image.frombytes('L', (w, h), packet['buffer'])
                .transpose(Image.FLIP_LEFT_RIGHT)
                .transpose(Image.ROTATE_180)
            )

            # ---- ALWAYS PREPARE A FILTERED PREVIEW FOR DisplayCanvas ----
            imgRGB = imgL.convert("RGB")
            r, g, b = imgRGB.split()

            if current_color == "red":
                red_temp = imgL.copy()
                g = Image.new("L", (w, h), 0)
                b = Image.new("L", (w, h), 0)

            elif current_color == "green":
                green_temp = imgL.copy()
                r = Image.new("L", (w, h), 0)
                b = Image.new("L", (w, h), 0)

            elif current_color == "blue":
                blue_temp = imgL.copy()
                r = Image.new("L", (w, h), 0)
                g = Image.new("L", (w, h), 0)

            # Show the MONOCHROME filtered frame (always)
            filtered = Image.merge("RGB", (r, g, b))
            DisplayImage = ImageTk.PhotoImage(filtered)
            DisplayCanvas.itemconfig(DisplayCanvasImageID, image=DisplayImage)

            print(current_color)
            # ---- EVERY THIRD FRAME: BLUE ARRIVED → BUILD RGB COMPOSITE ----
            if current_color == "blue":
                if red_temp is not None and green_temp is not None and blue_temp is not None:
                    """
                    # ---- Gamma ----
                    r_gamma = red_temp.point(lambda p: max(0, min(255, int((p / 255.0) ** safe_gain(red_gamma_entry) * 255))))
                    g_gamma = green_temp.point(lambda p: max(0, min(255, int((p / 255.0) ** safe_gain(green_gamma_entry) * 255))))
                    b_gamma = blue_temp.point(lambda p: max(0, min(255, int((p / 255.0) ** safe_gain(blue_gamma_entry) * 255))))

                    # ---- Gain ----
                    r_gain  = r_gamma.point(lambda p: max(0, min(255, int(p * safe_gain(red_gain_entry)))))
                    g_gain  = g_gamma.point(lambda p: max(0, min(255, int(p * safe_gain(green_gain_entry)))))
                    b_gain  = b_gamma.point(lambda p: max(0, min(255, int(p * safe_gain(blue_gain_entry)))))
                    """

                    # ---- MERGE RESULT ----
                    combined = Image.merge("RGB", (red_temp, green_temp, blue_temp))

                    # ---- RGB IMAGE ----
                    RGBImage = ImageTk.PhotoImage(combined)
                    RGBCanvas.itemconfig(RGBCanvasImageID, image=RGBImage)

                    if is_recording:
                        combined.save(os.path.join(save_dir, f"{recording_frame_num}.png")) #save to png
                        if not white_cycle:
                            recording_frame_num += 1
                
            if current_color == "white":
                if is_recording:
                    filtered.save(os.path.join(save_dir_w, f"{recording_frame_num}.png")) #save to png
                    recording_frame_num += 1

        elif datatype == 'SCAMP5_DOUT':
            """
            w = packet['width']
            h = packet['height']
            print('[%d] dout %dx%d >> %d' % (lc, w, h, packet['channel']))
            img = Image.frombytes('L', (w, h), packet['buffer']).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_180)
            DisplayImage[1] = ImageTk.PhotoImage(img)
            DisplayCanvas[1].create_image(0, 0, image=DisplayImage[1], anchor=tk.NW)
            """

        elif datatype == 'INT16':
            print('[%d] int16 %dx%d >> %d' % (lc, packet['n_rows'], packet['n_cols'], packet['channel']))

        elif datatype == 'INT32':
            print('[%d] int32 %dx%d >> %d' % (lc, packet['n_rows'], packet['n_cols'], packet['channel']))
            # print(packet['data'])

        elif datatype == 'FLOAT':
            print('[%d] float %dx%d >> %d' % (lc, packet['n_rows'], packet['n_cols'], packet['channel']))

        elif datatype == 'REQUEST':
            if packet['filetype']== 'IMAGE':
                print('[%d] request image %s %d' % (lc, repr(packet['filepath']), packet['n_bits']))
                img = Image.open(packet['filepath']).transpose(Image.FLIP_TOP_BOTTOM)
                scamp.send_image(img.tobytes(), img.width, img.height, packet['n_bits'])

            elif packet['filetype']== 'FILE':
                print('[%d] request file %s' % (lc, repr(packet['filepath'])))
                with open(packet['filepath'], "rb") as f:
                    scamp.send_file(f.read())
    else:
        pass
        extract_color(packet)

def extract_color(text):
    global current_color
    if "RED" in text:
        current_color = "red"
        color_label.config(text="RED", fg="red")
    if "GREEN" in text:
        current_color = "green"
        color_label.config(text="GREEN", fg="green")
    if "BLUE" in text:
        current_color = "blue"
        color_label.config(text="BLUE", fg="blue")
    if "WHITE" in text:
        current_color = "white"
        color_label.config(text="WHITE", fg="ivory3")

def start_switching():
    global switching_var
    global Send_Msg_On_Quit
    global current_color
    global vs_on
    vs_on = not vs_on
    print(vs_on)
    if switching_var.get():
        scamp.send_message(scamp.VS_MSG_HOST_ON, 0, 0)
        send_gpio(5, 1) #switching
        send_gpio(3, int(rgb_fps))
        send_gpio(4, int(delay))
        send_gpio(6, int(frame_gain))
        
        Send_Msg_On_Quit = True
    else:
        scamp.send_message(scamp.VS_MSG_HOST_DC, 0, 0)
        send_gpio(5, 0) #not switching
        send_gpio(3, int(rgb_fps))
        send_gpio(4, int(delay))
        send_gpio(6, int(frame_gain))
        Send_Msg_On_Quit = False
        

def start_recording():
    global save_dir
    global save_dir_w
    global is_recording
    global recording_frame_num
    is_recording = not is_recording
    if is_recording:
        recording_frame_num = 0
        session_start = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_dir = os.path.join("captured_frames", session_start)
        os.makedirs(save_dir, exist_ok=True)
        save_dir_w = os.path.join("captured_frames", session_start, "W")
        os.makedirs(save_dir_w, exist_ok=True)

def main_process():
    # process scamp interface
    scamp.routine()

    # process all packets until there is no packet queued
    while True:
        packet = scamp.get_packet()
        if packet is None:
            break
        else:
            process_packet(packet)

    # process tk
    tk_root.update_idletasks()

    tk_root.after(1, main_process)


def send_gpio(some_id, the_value):
    #scamp.send_message(scamp.VS_MSG_USER_VALUE, some_id, the_value)
    #scamp.send_message(scamp.VS_MSG_USER_VALUE, some_id, the_value)
    scamp.send_gui_value(some_id, the_value)
    print("sent")

def fps_slider_callback(value):
    global rgb_fps
    rgb_fps = int(value)
    send_gpio(3, int(rgb_fps))
    fps_value.config(text=value)

def delay_slider_callback(value):
    global delay
    delay = value
    delay_value.config(text=value)
    send_gpio(4, int(value))

def frame_gain_callback(value):
    global frame_gain
    frame_gain = value
    frame_gain_value.config(text=value)
    send_gpio(6, int(value))

def safe_gain(entry_widget):
    try:
        text = entry_widget.get().strip()
        return float(text) if text != "" else 0.0
    except ValueError:
        return 0.0

def white_cycle_callback():
    send_gpio(8, int(white_cycle.get()))

################################################################################
# Script Entry Point

Connection_Type = 'USB'

tk_root = tk.Tk()
tk_root.title('Scamp5d Python App')

W = 256
H = 256
rgb_fps = 1
current_color = "red"
delay = 0
frame_gain = 1
vs_on = False
is_recording = False
recording_frame_num = 0
red_temp = []
green_temp = []
blue_temp = []
save_dir = ""
save_dir_w = ""

# --- Container frame for displays (so they don't affect widgets below) ---
DisplayFrame = tk.Frame(tk_root)
DisplayFrame.pack()   # pack only the frame; contents are arranged inside it

# --- Container frame for displays ---
DisplayFrame = tk.Frame(tk_root)
DisplayFrame.pack()  # only packs the frame; widgets inside are arranged within

# --- First display (left) ---
DisplayImage = ImageTk.PhotoImage(Image.frombytes('L', (W, H), bytes(W * H)))
DisplayCanvas = tk.Canvas(DisplayFrame, width=W, height=H, bd=0)
DisplayCanvas.pack(side="left")
DisplayCanvasImageID = DisplayCanvas.create_image(0, 0, image=DisplayImage, anchor=tk.NW)

# --- Second display (middle) ---
RGBImage = ImageTk.PhotoImage(Image.frombytes('L', (W, H), bytes(W * H))) 
RGBCanvas = tk.Canvas(DisplayFrame, width=W, height=H, bd=0)
RGBCanvas.pack(side="left")
RGBCanvasImageID = RGBCanvas.create_image(0, 0, image=RGBImage, anchor=tk.NW)

# --- Third display (right) ---
HSVImage = ImageTk.PhotoImage(Image.frombytes('L', (W, H), bytes(W * H))) 
HSVCanvas = tk.Canvas(DisplayFrame, width=W, height=H, bd=0)
HSVCanvas.pack(side="left")
HSVCanvasImageID = HSVCanvas.create_image(0, 0, image=HSVImage, anchor=tk.NW)

# Create a horizontal container for left + right columns
main_frame = tk.Frame(tk_root)
main_frame.pack(fill="both", expand=True)

# Left column (sliders + checkboxes)
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", anchor="nw")

# Middle column (gain text fields)
middle_frame = tk.Frame(main_frame)
middle_frame.pack(side="left", padx=20, anchor="nw")

# Right column (gamma text fields)
right_frame = tk.Frame(main_frame)
right_frame.pack(side="left", padx=20, anchor="nw")

# ---- LEFT SIDE ----
# ---- FPS slider ----
row1 = tk.Frame(left_frame)
row1.pack(anchor="w")

fps_value = tk.Label(row1, text="1", font=("Arial", 11))
fps_value.pack(side=tk.RIGHT)


Slider_1 = tk.Scale(
    row1,
    from_=1,
    to=30,
    orient=tk.HORIZONTAL,
    label="FPS Slider:",
    showvalue=False,
    font=("Arial", 10),
    command=fps_slider_callback
)
Slider_1.set(1)
Slider_1.pack(side=tk.LEFT)


# ---- Delay slider ----
row2 = tk.Frame(left_frame)
row2.pack(anchor="w")

delay_value = tk.Label(row2, text="0", font=("Arial", 11))
delay_value.pack(side=tk.RIGHT)

Slider_2 = tk.Scale(
    row2,
    from_=0,
    to=10000,
    orient=tk.HORIZONTAL,
    label="Delay (us):",
    showvalue=False,
    font=("Arial", 10),
    command=delay_slider_callback
)
Slider_2.set(0)
Slider_2.pack(side=tk.LEFT)

# ---- Frame Gain slider ----
row3 = tk.Frame(left_frame)
row3.pack(anchor="w")

frame_gain_value = tk.Label(row3, text="0", font=("Arial", 11))
frame_gain_value.pack(side=tk.RIGHT)

Slider_3 = tk.Scale(
    row3,
    from_=1,
    to=5,
    orient=tk.HORIZONTAL,
    label="Frame Gain:",
    showvalue=False,
    font=("Arial", 10),
    command=frame_gain_callback
)
Slider_3.set(1)
Slider_3.pack(side=tk.LEFT)

"""
rgb_row = tk.Frame(left_frame) #CHANGE FROM LEFT_FRAME
rgb_row.pack(anchor="w")

red_var = tk.BooleanVar()
green_var = tk.BooleanVar()
blue_var = tk.BooleanVar()

tk.Label(rgb_row, text="R:").pack(side=tk.LEFT)
tk.Checkbutton(
    rgb_row,
    variable=red_var,
    command=lambda: send_gpio(0, red_var.get())
).pack(side=tk.LEFT)

tk.Label(rgb_row, text="G:").pack(side=tk.LEFT)
tk.Checkbutton(
    rgb_row,
    variable=green_var,
    command=lambda: send_gpio(1, green_var.get())
).pack(side=tk.LEFT)

tk.Label(rgb_row, text="B:").pack(side=tk.LEFT)
tk.Checkbutton(
    rgb_row,
    variable=blue_var,
    command=lambda: send_gpio(2, blue_var.get())
).pack(side=tk.LEFT)
"""

color_label = tk.Label(tk_root, text="RED", font=("Arial", 18), fg = "red")

# setup the connect to the SCAMP vision system
Send_Msg_On_Quit = False
if Connection_Type == 'USB':
    #BOTTOM BAR TKINTER
    bold_font = tkFont.Font(size=11, weight="bold")
    switching_var = tk.IntVar()
    switching_checkbox = tk.Checkbutton(tk_root, text="vs_gui_is_on()", variable=switching_var, command=start_switching, font = bold_font)
    switching_checkbox.pack()
    recording = tk.BooleanVar()
    recording_checkbox = tk.Checkbutton(tk_root, text="Start Recording", variable=recording, command=start_recording, font = bold_font)
    recording_checkbox.pack()    
    white_cycle = tk.BooleanVar()
    white_cycle_checkbox = tk.Checkbutton(tk_root, text="White Cycle", variable=white_cycle, command=white_cycle_callback, font = bold_font)
    white_cycle_checkbox.pack()
    color_label.pack()
    print('open USB connection...')
    scamp.open_usb('0')
else:
    print('open TCP connection...')
    scamp.open_tcp('127.0.0.1',27888)

# main loop
tk_root.after(10, main_process)
tk_root.mainloop()

# exiting
if Send_Msg_On_Quit:
    start_switching(False)
    white_cycle_callback(False)
    scamp.send_message(scamp.VS_MSG_HOST_DC, 0, 0)

time.sleep(0.1)
scamp.close()
print('End.')

exit()
