import pyautogui
import time
import keyboard
import pandas as pd
#pyautogui.moveTo(100, 150)
#pyautogui.moveRel(0, 10)  # move mouse 10 pixels down
#pyautogui.dragTo(100, 150)
#pyautogui.dragRel(0, 10)  # drag mouse 10 pixels down

import screeninfo

from screeninfo import get_monitors
x = 0
y = 0
x1 = 0
y1 = 0
for m in get_monitors():
    x1 = m.x + m.width
    y1 = m.y + m.width
    print(str(m))


print(x,y, x1, y1)

import random
import sys
import traceback
if sys.platform == 'win32':
    from ctypes import *


    class LASTINPUTINFO(Structure):
        _fields_ = [
            ('cbSize', c_uint),
            ('dwTime', c_int),
        ]


    import win32api


    # def get_idle_duration():
    #     return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

    last = 0
    last_post = None
    last_event = 0
    def get_idle_duration():
        global last
        global last_post
        global last_event
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        if True:
            now = time.time_ns()
            # if (now - last_event) < 60*1e9:
            #     print("here ")
            #     return last

            now = pyautogui.position()

            if last_post == None:
                last_post = now

            #print (last_post == now)
            if last_post != now:
                last = 0
            last_post = now

            last = last +1
            if last > 125:
                last = 0
            return last
        if windll.user32.GetLastInputInfo(byref(lastInputInfo)):
            millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
        else:
            return 0
else:
    def get_idle_duration():
        return 0
#
# print(pyautogui.getAllWindows())
# for x in pyautogui.getAllWindows():
#    title = str(x.title)
#    if title == "MKTDEVPC0402 - Remote Desktop":
#        print(title)
#        #pyautogui.getActiveWindow().maximize()
#        x.maximize()

def is_point_inside(win, point):
    if point.x >=win.left and point.x <=win.left + win.width:
        if point.y >= win.top and point.y <= win.top + win.height:
            return True
    return False
print(pyautogui.position())
point = None
TIMEOUT=120
def get_now():
    return pd.Timestamp.utcnow().tz_convert("US/Eastern").tz_localize(None).strftime("%Y%m%d %H:%M:%S.%f")#

def key_pressed(e):
    global last_event, last
    print(get_now(), "something happened", e)
    last_event = time.time_ns()
    last = 1
keyboard.on_press(key_pressed)

while True:
    open_time = pd.to_datetime("07:00:00")
    close_time = pd.to_datetime("17:00:00")
    try:
        time.sleep(1)
        duration = get_idle_duration()
        title = pyautogui.getActiveWindowTitle()
        now = pd.to_datetime('now')
        now = now.tz_localize('US/Eastern')#.tz_convert('US/Eastern')
        print(get_now(), " open=", open_time, "close=", close_time)
        if now.hour < open_time.hour or now.hour >= close_time.hour:
            print(get_now(), "out side working hours")
            continue

        # if now.hour >16 and now.hour < 17:
        #     print("doctor appt with anika out side working hours -- xray")
        #     continue

        # if duration > 1:
        #     print(f"Win {title} duration {int(duration)}/{TIMEOUT} ")
        if duration < TIMEOUT:
            #print("timeout", duration)
            continue


        win = pyautogui.getActiveWindow()
        if win is None:
            continue

        print(title)
        now = pyautogui.position()
        if point is None:
            point = now
        print(title)
        if True: #title == "MKTDEVPC0402 - Remote Desktop":
            print(point, now)
            if point == now: #nothing moved for a while
                print("match did not move", point,  now)
                #print("found ", title, str(win))
               # win.
                x1  = win.width
                y1 = win.width
                x0 = int(random.random() * x1 + win.top)
                y0 = int(random.random() * y1 + win.left)
                print(x0, y0)
                #pyautogui.moveTo(x0, y0)
                if(is_point_inside(win, point)):
                    try:
                        pyautogui.rightClick()
                        key_pressed(point)
                    except:
                        traceback.print_exc()
                        continue
                else:
                   # pyautogui.moveTo(pyautogui.po
                    print("not inside window")
            else:
                print("moved ", point, now)
        else:
            print("not active ", title, dir(win))
            print(win.size, win.left, win.top)
    except:
        traceback.print_exc()


    point = now


