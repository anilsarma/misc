import pyautogui
import time

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


    def get_idle_duration():
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
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
while True:
    try:
        time.sleep(1)
        duration = get_idle_duration()
        print(duration)
        if duration < 120:
            continue
        win = pyautogui.getActiveWindow()
        title = pyautogui.getActiveWindowTitle()
        if win is None:
            continue

        #print(title)
        now = pyautogui.position()
        if point is None:
            point = now
        print(title)
        if True:
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


