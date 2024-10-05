import shutil
import sys
import os
import pathlib
import signal
import time
import threading
import json
import subprocess
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
__version__ = '2.1.2'


def unlock_keyboard():
    """Unlock keyboard"""
    kb.unhook_all()


def lock_keyboard():
    """Lock keyboard"""
    blocked_keys = []
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

    for keyname in blocked_keys:
        kb.block_key(keyname)
    kb.block_key('backspace')

class Main:
    def __init__(self):
        # Initialize vars and paths
        self.user_path = pathlib.Path().home() / 'AppData' / 'Local'
        if not os.path.isdir(os.path.join(self.user_path, 'MouseLock')):
            os.mkdir(self.user_path / 'MouseLock')
            with open(self.user_path / 'MouseLock' / 'data.dat', 'w') as fb:
                fb.write('60\n180\n800\n545\nEnglish\n0')
            shutil.copy('.\\program\\logo.ico', self.user_path / 'MouseLock' / 'logo.ico')
            shutil.copy('.\\program\\blueScreen.exe', self.user_path / 'MouseLock' / 'blueScreen.exe')
            shutil.copy('.\\program\\Mouse Lock.exe', self.user_path / 'MouseLock')
            shutil.copy('.\\program\\Mouse Lock1.exe', self.user_path / 'MouseLock')
            shutil.copytree('.\\Language', self.user_path / 'MouseLock' / 'Language')
        self.user_path = self.user_path / 'MouseLock'
        os.chdir(self.user_path)
        with open(os.path.join(self.user_path, 'data.dat'), 'r') as fb:
            read = fb.read().split('\n')
            self.first_seconds = int(read[0])
            self.second_seconds = int(read[1])
            self.mouse_position = (int(read[2]), int(read[3]))
            self.language_name = read[4]
            self.pos = int(read[5])
        with open(pathlib.Path().cwd() / 'Language' / f'{self.language_name}.json', 'r', encoding='utf-8') as f:
            self.language = json.load(f)

        # Create icon object
        image = Image.open(".\\logo.ico")  # Open ICO image file and create an Image object
        self.start_menu = (
            pystray.MenuItem(self.language['Menu']['Settings'], self.show_settings),
            pystray.MenuItem(self.language['Menu']['Exit'], action=self.exit_program),  # Create menu items tuple
            pystray.MenuItem(self.language['Menu']['Restart'], action=self.restart),
            pystray.MenuItem(self.language['Menu']['Pause'], action=self.pause_or_start)
        )
        self.pause_menu = (
            pystray.MenuItem(self.language['Menu']['Settings'], self.show_settings),
            pystray.MenuItem(self.language['Menu']['Exit'], action=self.exit_program),  # Create menu items tuple
            pystray.MenuItem(self.language['Menu']['Restart'], action=self.restart),
            pystray.MenuItem(self.language['Menu']['Start'], action=self.pause_or_start)
        )
        # Create PyStray Icon object and pass the necessary parameters
        self.icon = pystray.Icon("name", image, self.language['name'], self.start_menu)

        self.is_exit = False
        self.is_pause = False
        self.is_down = False
        self.start_time = time.time()
        # Create keyboard controller
        self.keyboard = Controller()
        # Create mouse controller
        self.mouse = MouseController()

        # Create keyboard listener
        keyboard_listener = Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        # Create mouse listener
        mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)

        # Start listener threads
        threading.Thread(target=keyboard_listener.start, daemon=True).start()
        threading.Thread(target=mouse_listener.start, daemon=True).start()
        # Display icon
        threading.Thread(target=self.icon.run, daemon=True).start()

    def update(self):
        # global start_time, is_down, first_seconds, second_seconds
        is_unlock = False
        while True:
            if time.time() - self.start_time >= self.first_seconds and not self.is_pause:
                break
            time.sleep(0.1)
        # Set automatic failure protection to False, so the program won't stop even if the mouse moves to the top left corner of the screen
        pyautogui.FAILSAFE = False

        # Get screen resolution
        screen_width, screen_height = pyautogui.size()

        # Move mouse to the center of the screen
        center_x, center_y = screen_width // 2, screen_height // 2
        lock_keyboard()
        while not self.is_down:
            if pyautogui.position() != (center_x, center_y):
                pyautogui.moveTo(center_x, center_y)
            if time.time() - self.start_time >= self.second_seconds:
                is_unlock = True
                break

        if not is_unlock:
            unlock_keyboard()
            self.is_down = False
            pyautogui.FAILSAFE = True
            self.start_time = time.time()
        else:
            is_unlock = False
            unlock_keyboard()
            self.blue_screen()
            unlock_keyboard()

    def reset(self):
        self.start_time = time.time()

    def down(self):
        self.is_down = True
        self.reset()

    def on_key_press(self, key):
        """Keyboard event listener"""
        self.reset()

    def on_key_release(self, key):
        self.reset()

    def on_move(self, x, y):
        """Mouse event listener"""
        self.reset()

    def on_click(self, x, y, button, pressed):
        if button == Button.middle and pressed:
            self.down()
        self.reset()

    def on_scroll(self, x, y, dx, dy):
        self.reset()


    def blue_screen(self):
        if self.is_pause:
            return
        # Press Win key
        pyautogui.keyDown('win')
        # Press M key
        pyautogui.press('m')
        # Release Win key
        pyautogui.keyUp('win')
        time.sleep(0.1)
        process = subprocess.Popen(".\\blueScreen.exe", shell=True)
        time.sleep(1)
        pyautogui.moveTo(*self.mouse_position)
        pyautogui.click()
        pyautogui.moveTo(1052,570)
        pyautogui.click()
        process.wait()

    def restart(self):
        self.is_exit = True
        with open(os.path.join(self.user_path, 'data.dat'), 'w') as fb:
            fb.write(str(self.first_seconds) + '\n')
            fb.write(str(self.second_seconds) + '\n')
            fb.write(str(self.mouse_position[0]) + '\n')
            fb.write(str(self.mouse_position[1]) + '\n')
            fb.write(self.language_name + '\n')
            fb.write('0' if self.pos else '1')
        self.icon.stop()
        pid = os.getpid()
        if self.pos:
            subprocess.Popen('.\\Mouse Lock.exe')
        else:
            subprocess.Popen('.\\Mouse Lock1.exe')
        os.kill(pid, signal.SIGTERM)
        sys.exit()

    def exit_program(self):
        self.is_exit = True
        with open(os.path.join(self.user_path, 'data.dat'), 'w') as fb:
            fb.write(str(self.first_seconds) + '\n')
            fb.write(str(self.second_seconds) + '\n')
            fb.write(str(self.mouse_position[0]) + '\n')
            fb.write(str(self.mouse_position[1]) + '\n')
            fb.write(self.language_name + '\n')
            fb.write('0' if self.pos else '1')
        self.icon.stop()
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)
        sys.exit()

    def show_settings(self):
        def ok(finish_exit=False):
            nonlocal entry1, entry2, root, options, language_combobox, self
            entry1_answer, entry2_answer = int(entry1.get() if entry1.get() else self.first_seconds), int(entry2.get() if entry2.get() else self.second_seconds)
            self.first_seconds = entry1_answer if entry1_answer < entry2_answer else self.first_seconds
            self.second_seconds = entry2_answer if entry1_answer < entry2_answer else self.second_seconds
            self.mouse_position = (800, 545)
            options_answer = options.get()
            if options_answer == self.language["Styles"]['Recover']:
                self.mouse_position = (878, 546)
            elif options_answer == self.language["Styles"]['FBI']:
                self.mouse_position = (795, 515)
            elif options_answer == self.language["Styles"]['Collapse']:
                self.mouse_position = (800, 572)
            elif options_answer == self.language["Styles"]['Update']:
                self.mouse_position = (871, 514)
            elif options_answer == self.language["Styles"]['Restart']:
                self.mouse_position = (863, 575)

            if entry1_answer >= entry2_answer:
                messagebox.showerror(self.language['title'], self.language['Error'])
            elif self.language_name != language_combobox.get():
                self.language_name = language_combobox.get()
                if messagebox.askyesno(self.language['title'], self.language['Info']):
                    self.restart()
            elif finish_exit:
                root.destroy()


        root = tk.Tk()
        root.geometry('500x500')
        root.title(self.language['title'])
        root.iconbitmap(default='.\\logo.ico')
        ttk.Label(root, text=self.language['First gear wait time']).place(x=2, y=2)
        ttk.Label(root, text=self.language['Second gear wait time']).place(x=2, y=40)
        ttk.Label(root, text=self.language['Style']).place(x=2, y=80)
        ttk.Label(root, text=self.language['Language']).place(x=2, y=120)
        entry1 = ttk.Spinbox(root, from_=0, to=114514, increment=1)
        entry1.insert(0, str(self.first_seconds))
        entry2 = ttk.Spinbox(root, from_=0, to=114514, increment=1)
        entry2.insert(0, str(self.second_seconds))
        entry1.place(x=200, y=2)
        entry2.place(x=200, y=40)
        default = self.language['Styles']['Blue Screen']
        if self.mouse_position == (878, 546):
            default = self.language['Styles']['Recover']
        elif self.mouse_position == (795, 515):
            default = self.language['Styles']['FBI']
        elif self.mouse_position == (800, 572):
            default = self.language['Styles']['Collapse']
        elif self.mouse_position == (871, 514):
            default = self.language['Styles']['Update']
        elif self.mouse_position == (863, 575):
            default = self.language['Styles']['Restart']
        values = []
        for k, v in self.language['Styles'].items():
            values.append(v)
        options = ttk.Combobox(root, values=values, state="readonly")
        options.set(default)
        options.place(x=70, y=80)
        values = []
        for name in os.listdir(os.path.join('.', 'Language')):
            if isinstance(name, str) and name.endswith('.json'):
                values.append(name[:-5])
        language_combobox = ttk.Combobox(root, values=values, state="readonly")
        language_combobox.set(self.language_name)
        language_combobox.place(x=80, y=120)
        ttk.Button(root, text=self.language['Buttons']['Apply'], command=ok).place(x=380, y=460)
        ttk.Button(root, text=self.language['Buttons']['Cancel'], command=root.destroy).place(x=260, y=460)
        ttk.Button(root, text=self.language['Buttons']['Confirm'], command=lambda :ok(True)).place(x=140, y=460)
        root.mainloop()

    def pause_or_start(self):
        self.is_pause = not self.is_pause
        if self.is_pause:
            self.icon.menu = self.pause_menu
        else:
            self.icon.menu = self.start_menu

    def start_mainloop(self):
        while not self.is_exit:
            self.update()
            unlock_keyboard()

if __name__ == '__main__':
    Main().start_mainloop()