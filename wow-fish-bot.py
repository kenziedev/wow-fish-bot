# -*- coding: utf-8 -*-
import webbrowser
import sys
import os
import struct
import time
#
import pyautogui
import numpy as np
import cv2
#
from win10toast import ToastNotifier
from PIL import ImageGrab, Image
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
from threading import Thread
import pystray
from pystray import MenuItem as item

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
  
def app_pause(icon, item):
    global is_stop
    is_stop = not is_stop
    if is_stop:
        icon.title = app + " - On Pause"
    else:
        icon.title = app

def app_destroy(icon, item):
    global flag_exit
    flag_exit = True
    icon.stop()
    sys.exit()
    
def app_about(icon, item):
    webbrowser.open('https://github.com/YECHEZ/wow-fish-bot')

def setup(icon):
    icon.visible = True
    toaster.show_toast(app,
                       link,
                       icon_path=app_ico,
                       duration=5)

def main_loop():
    global is_stop, flag_exit, lastx, lasty, is_block, new_cast_time, recast_time, wait_mes
    while not flag_exit:
        if not is_stop:
            if GetWindowText(GetForegroundWindow()) != "월드 오브 워크래프트":
                if wait_mes == 5:
                    wait_mes = 0
                    toaster.show_toast(app,
                                       "월드 오브 워크래프트를 기다리는 중입니다.",
                                       icon_path=app_ico,
                                       duration=5)
                wait_mes += 1
                time.sleep(2)
            else:
                wait_mes = 0
                rect = GetWindowRect(GetForegroundWindow())
                
                if not is_block:
                    lastx = 0
                    lasty = 0
                    pyautogui.press('1')
                    new_cast_time = time.time()
                    is_block = True
                    time.sleep(2)
                else:
                    fish_area = (0, rect[3] // 2, rect[2], rect[3])

                    img = ImageGrab.grab(fish_area)
                    img_np = np.array(img)

                    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    h_min = np.array((0, 0, 253), np.uint8)
                    h_max = np.array((255, 0, 255), np.uint8)

                    mask = cv2.inRange(frame_hsv, h_min, h_max)

                    moments = cv2.moments(mask, 1)
                    dM01 = moments['m01']
                    dM10 = moments['m10']
                    dArea = moments['m00']

                    b_x = 0
                    b_y = 0

                    if dArea > 0:
                        b_x = int(dM10 / dArea)
                        b_y = int(dM01 / dArea)
                    if lastx > 0 and lasty > 0:
                        if lastx != b_x and lasty != b_y:
                            is_block = False
                            if b_x < 1: b_x = lastx
                            if b_y < 1: b_y = lasty
                            pyautogui.moveTo(b_x, b_y + fish_area[1], 0.3)
                            pyautogui.mouseDown(button='right')
                            pyautogui.mouseUp(button='right')
                            time.sleep(5)
                    lastx = b_x
                    lasty = b_y

                    if time.time() - new_cast_time > recast_time:
                        is_block = False               
            if cv2.waitKey(1) == 27:
                break
        else:
            time.sleep(2)

if __name__ == "__main__":
    is_stop = True
    flag_exit = False
    lastx = 0
    lasty = 0
    is_block = False
    new_cast_time = 0
    recast_time = 40
    wait_mes = 0    
    app = "WoW Fish BOT by YECHEZ"
    link = "github.com/YECHEZ/wow-fish-bot"
    app_ico = resource_path('wow-fish-bot.ico')
    
    # 아이콘 설정
    image = Image.open(app_ico)
    
    # 메뉴 설정
    menu = (
        item('Start/Stop', app_pause),
        item(link, app_about),
        item('Quit', app_destroy)
    )
    
    # 시스템 트레이 아이콘 생성
    icon = pystray.Icon(app, image, app, menu)
    toaster = ToastNotifier()
    
    # 메인 루프를 별도의 스레드에서 실행
    Thread(target=main_loop, daemon=True).start()
    
    # 시스템 트레이 아이콘 실행
    icon.run(setup=setup)
