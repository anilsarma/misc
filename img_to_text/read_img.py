import cv2
import PIL
import pytesseract


#img = cv2.imread("f2.PNG")
for i in range(1, 6):
    s = pytesseract.image_to_string(PIL.Image.open("pic"+str(i)+ ".PNG"), lang='eng')
    print ("----------------- File {} --------------- ".format(i))
    print(s)