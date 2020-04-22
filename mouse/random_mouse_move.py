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

#
# print(pyautogui.getAllWindows())
# for x in pyautogui.getAllWindows():
#    title = str(x.title)
#    if title == "MKTDEVPC0402 - Remote Desktop":
#        print(title)
#        #pyautogui.getActiveWindow().maximize()
#        x.maximize()


print(pyautogui.position())
point = None
while True:
    time.sleep(60)
    win = pyautogui.getActiveWindow()
    title = pyautogui.getActiveWindowTitle()

    #print(title)
    now = pyautogui.position()
    if point is None:
        point = now
    print(title)
    if title == "<some name>":
        print(point, now)
        if point == now: #nothing moved for a while
            print("match did not move", point,  now)
            #print("found ", title, str(win))
            x1  = win.width
            y1 = win.width
            x0 = int(random.random() * x1 + win.top)
            y0 = int(random.random() * y1 + win.left)
            print(x0, y0)
            #pyautogui.moveTo(x0, y0)
            pyautogui.rightClick()
        else:
            print("moved ", point, now)
    else:
        print("not active ", title, dir(win))
        print(win.size, win.left, win.top)



    point = now


