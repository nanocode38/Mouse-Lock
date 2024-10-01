import shutil
import sys
import os
import pathlib
import signal
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import pyautogui
import keyboard as kb
from pynput.keyboard import Controller, Listener
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import pystray
from PIL import Image

__author__ = 'nanocode38'
__version__ = '1.2.0'

user_path = pathlib.Path().home() / 'AppData' / 'Local'
if not os.path.isdir(os.path.join(user_path, 'MouseLock')):
    os.mkdir(user_path / 'MouseLock')
    with open(user_path / 'MouseLock' / 'data.dat', 'w') as fb:
        fb.write('60\n180\n800\n545')
    shutil.copy('.\\images\\logo.ico', user_path / 'MouseLock' / 'logo.ico')
    shutil.copy('.\\blueScreen.exe', user_path / 'MouseLock' / 'blueScreen.exe')
user_path = user_path / 'MouseLock'
start_time = time.time()
is_down = False
os.chdir(user_path)
with open(os.path.join(user_path, 'data.dat'), 'r') as fb:
    read = fb.read().split('\n')
    first_seconds = int(read[0])
    second_seconds = int(read[1])
    mouse_position = (int(read[2]), int(read[3]))
is_exit = False

def reset():
    global start_time
    start_time = time.time()

# Create keyboard controller
keyboard = Controller()
# Create mouse controller
mouse = MouseController()

def down():
    global is_down
    is_down = True
    reset()

# Keyboard event listener
def on_key_press(key):
    reset()

def on_key_release(key):
    reset()

# Mouse event listener
def on_move(x, y):
    reset()

def on_click(x, y, button, pressed):
    if button == Button.middle and pressed:
        down()
    reset()

def on_scroll(x, y, dx, dy):
    reset()

# Create keyboard listener
keyboard_listener = Listener(on_press=on_key_press, on_release=on_key_release)

# Create mouse listener
mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

# Start listener threads
keyboard_thread = threading.Thread(target=keyboard_listener.start, daemon=True)
mouse_thread = threading.Thread(target=mouse_listener.start, daemon=True)

# Start threads
keyboard_thread.start()
mouse_thread.start()

def blue_screen():
    global mouse_position
    import subprocess
    # Press Win key
    pyautogui.keyDown('win')
    # Press M key
    pyautogui.press('m')
    # Release Win key
    pyautogui.keyUp('win')
    time.sleep(0.1)
    process = subprocess.Popen(".\\blueScreen.exe", shell=True)
    time.sleep(1)
    pyautogui.moveTo(*mouse_position)
    pyautogui.click()
    pyautogui.moveTo(1052,570)
    pyautogui.click()
    process.wait()


def unlock_keyboard():
    """Unlock keyboard"""
    kb.unhook_all()

def lock_keyboard():
    """Lock keyboard"""
    blocked_keys = list()

    # Block number keys on the numeric keypad
    for i in range(10):
        blocked_keys.append(f'num {i}')

    # Block other keys
    blocked_keys += ['caps lock', 'tab', 'windows', 'left arrow', 'right arrow'] + [f'f{i}' for i in range(1, 13)]
    blocked_keys += ['volume up', 'volume down',
                     'up arrow', 'down arrow', 'left arrow', 'right arrow',
                     'insert', 'home', 'page up', 'end', 'page down',
                     'pause', 'scroll lock', 'print screen']
    blocked_keys += list('abcdefghijklmnopqrstuvwxyz')

    # ... Add other keys you want to block

    for keyname in blocked_keys:
        kb.block_key(keyname)
    kb.block_key('backspace')

def main():
    global start_time, is_down, first_seconds, second_seconds
    is_unlock = False
    while True:
        if time.time() - start_time >= first_seconds:
            break
        time.sleep(0.1)
    # Set automatic failure protection to False, so the program won't stop even if the mouse moves to the top left corner of the screen
    pyautogui.FAILSAFE = False

    # Get screen resolution
    screen_width, screen_height = pyautogui.size()

    # Move mouse to the center of the screen
    center_x, center_y = screen_width // 2, screen_height // 2
    lock_keyboard()
    while not is_down:
        if pyautogui.position() != (center_x, center_y):
            pyautogui.moveTo(center_x, center_y)
        if time.time() - start_time >= second_seconds:
            is_unlock = True
            break

    if not is_unlock:
        unlock_keyboard()
        is_down = False
        pyautogui.FAILSAFE = True
        start_time = time.time()
    else:
        is_unlock = False
        unlock_keyboard()
        blue_screen()
        unlock_keyboard()

def restart():
    global is_exit, first_seconds, second_seconds, mouse_position
    is_exit = True
    with open(os.path.join(user_path, 'data.dat'), 'w') as fb:
        fb.write(str(first_seconds) + '\n')
        fb.write(str(second_seconds) + '\n')
        fb.write(str(mouse_position[0]) + '\n')
        fb.write(str(mouse_position[1]))
    icon.stop()
    pid = os.getpid()
    os.system('Restart.exe')
    os.kill(pid, signal.SIGTERM)
    sys.exit()

def exit(icon):
    global is_exit, first_seconds, second_seconds, mouse_position
    is_exit = True
    with open(os.path.join(user_path, 'data.dat'), 'w') as fb:
        fb.write(str(first_seconds) + '\n')
        fb.write(str(second_seconds) + '\n')
        fb.write(str(mouse_position[0]) + '\n')
        fb.write(str(mouse_position[1]))
    icon.stop()
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
    sys.exit()

def show_settings(*args, **kwargs):
    global first_seconds, second_seconds, mouse_position
    def ok(finish_exit=False):
        global first_seconds, second_seconds, mouse_position
        nonlocal entry1, entry2, root, options
        entry1_answer, entry2_answer = int(entry1.get() if entry1.get() else first_seconds), int(entry2.get() if entry2.get() else second_seconds)
        first_seconds = entry1_answer if entry1_answer < entry2_answer else first_seconds
        second_seconds = entry2_answer if entry1_answer < entry2_answer else second_seconds
        mouse_position = (800, 545)
        options_answer = options.get()
        if options_answer == 'Recover':
            mouse_position = (878, 546)
        elif options_answer == 'FBI':
            mouse_position = (795, 515)
        elif options_answer == 'Collapse':
            mouse_position = (800, 572)
        elif options_answer == 'Update':
            mouse_position = (871, 514)
        elif options_answer == 'Restart':
            mouse_position = (863, 575)

        if entry1_answer >= entry2_answer:
            messagebox.showerror("Mouse Lock Settings", "Error: Unable to set First Gear Wait Time to be less than or equal to Second Gear Wait Time. Please set First Gear Wait Time to be greater than Second Gear Wait Time.")
        elif finish_exit:
            root.destroy()


    root = tk.Tk()
    root.geometry('500x500')
    root.title('Mouse Lock Settings')
    root.iconbitmap(default='.\\logo.ico')
    tk.Label(root, text='First gear wait time (s): ').place(x=2, y=2)
    tk.Label(root, text='Second gear wait time (s): ').place(x=2, y=40)
    tk.Label(root, text='Style: ').place(x=2, y=80)
    entry1 = tk.Entry(root)
    entry1.insert(0, str(first_seconds))
    entry2 = tk.Entry(root)
    entry2.insert(0, str(second_seconds))
    entry1.place(x=200, y=2)
    entry2.place(x=200, y=40)
    default = 'Blue Screen'
    if mouse_position == (878, 546):
        default = 'Recover'
    elif mouse_position == (795, 515):
        default = 'FBI'
        print(mouse_position)
    elif mouse_position == (800, 572):
        default = 'Collapse'
    elif mouse_position == (871, 514):
        default = 'Update'
    elif mouse_position == (863, 575):
        default = 'Restart'
    options = ttk.Combobox(root, values=["Blue Screen", "FBI", "Recover", "Restart", "Update", "Collapse"], state="readonly")
    options.set(default)
    options.place(x=70, y=80)
    tk.Button(root, text='  Apply  ', command=ok).place(x=430, y=460)
    tk.Button(root, text=' Cancel ', command=root.destroy).place(x=350, y=460)
    tk.Button(root, text=' Confirm ', command=lambda :ok(True)).place(x=260, y=460)
    root.mainloop()


# Create icon object
image = Image.open(".\\logo.ico")  # Open ICO image file and create an Image object
menu = (
    pystray.MenuItem('Settings', show_settings, default=True),
    pystray.MenuItem(text='Exit', action=exit), # Create menu items tuple
    pystray.MenuItem(text='Restart', action=restart)
)
icon = pystray.Icon("name", image, "Mouse Lock", menu)  # Create PyStray Icon object and pass the necessary parameters

# Display icon
_ = threading.Thread(target=icon.run, daemon=True).start()

while not is_exit:
    main()
    unlock_keyboard()