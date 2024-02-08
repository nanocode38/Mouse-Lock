import time
import threading

import pyautogui
import keyboard as kb
from pynput.keyboard import Key, Controller, Listener
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener


start_time = time.time()
is_down = False


def reset():
    global start_time
    start_time = time.time()

# 创建键盘控制器
keyboard = Controller()
# 创建鼠标控制器
mouse = MouseController()

def down():
    global is_down
    is_down = True
    reset()

# 键盘事件监听器
def on_key_press(key):
    reset()

def on_key_release(key):
    reset()

# 鼠标事件监听器
def on_move(x, y):
    reset()

def on_click(x, y, button, pressed):
    if button == Button.middle and pressed:
        down()
    reset()

def on_scroll(x, y, dx, dy):
    reset()

# 创建键盘监听器
keyboard_listener = Listener(on_press=on_key_press, on_release=on_key_release)

# 创建鼠标监听器
mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

# 启动监听器的线程
keyboard_thread = threading.Thread(target=keyboard_listener.start)
mouse_thread = threading.Thread(target=mouse_listener.start)

# 开始线程
keyboard_thread.start()
mouse_thread.start()

def blue_screen():
    import subprocess
    # 按下Win键
    pyautogui.keyDown('win')
    # 按下M键
    pyautogui.press('m')
    # 释放Win键
    pyautogui.keyUp('win')
    time.sleep(0.1)
    process = subprocess.Popen(".\\blueScreen.exe", shell=True)
    time.sleep(1)
    pyautogui.moveTo(766, 545)
    pyautogui.click()
    pyautogui.moveTo(1052,570)
    pyautogui.click()
    process.wait()


def unlock_keyboard():
    """解锁锁🔒键盘"""
    kb.unhook_all()

def lock_keyboard():
    """锁定🔒键盘"""
    blocked_keys = list()

    # 锁定数字键盘上的数字键
    for i in range(10):
        blocked_keys.append(f'num {i}')

    # 锁定其他按键
    blocked_keys += ['caps lock', 'tab', 'windows', 'left arrow', 'right arrow'] + [f'f{i}' for i in range(1, 13)]
    blocked_keys += ['volume up', 'volume down',
                     'up arrow', 'down arrow', 'left arrow', 'right arrow',
                     'insert', 'home', 'page up', 'end', 'page down',
                     'pause', 'scroll lock', 'print screen']
    blocked_keys += list('abcdefghijklmnopqrstuvwxyz')

    # ... 添加其他你想锁定的按键

    for keyname in blocked_keys:
        kb.block_key(keyname)
    kb.block_key('backspace')

def main():
    global start_time, is_down
    is_unlock = False
    while True:
        if time.time() - start_time >= 60:
            break
        time.sleep(0.1)
    # 设置自动故障保护功能为False，这样即使鼠标移动到屏幕左上角也不会停止程序
    pyautogui.FAILSAFE = False

    # 获取屏幕分辨率
    screen_width, screen_height = pyautogui.size()

    # 移动鼠标到屏幕中心
    center_x, center_y = screen_width // 2, screen_height // 2
    lock_keyboard()
    while not is_down:
        if pyautogui.position() != (center_x, center_y):
            pyautogui.moveTo(center_x, center_y)
        if time.time() - start_time >= 180:
            is_unlock = True
            break

    if not is_unlock:
        unlock_keyboard()
        is_down = False
        pyautogui.FAILSAFE = True
        start_time = time.time()
    else:
        is_unlock = False
        blue_screen()
        unlock_keyboard()

while True:
    main()
    unlock_keyboard()