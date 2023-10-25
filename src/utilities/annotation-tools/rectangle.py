import numpy as np
import cv2
rect = (0,0,0,0)
startPoint = False
endPoint = False
def on_mouse(event,x,y,flags,params):
    global rect,startPoint,endPoint
    # get mouse click
    if event == cv2.EVENT_LBUTTONDOWN:
        if startPoint == True and endPoint == True:
            startPoint = False
            endPoint = False
            rect = (0, 0, 0, 0)
        if startPoint == False:
            rect = (x, y, 0, 0)
            startPoint = True
        elif endPoint == False:
            rect = (rect[0], rect[1], x, y)
            endPoint = True
cap = cv2.VideoCapture(0)
waitTime = 50
#Reading the first frame
(grabbed, frame) = cap.read()
while(cap.isOpened()):
    (grabbed, frame) = cap.read()
    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)    
    #drawing rectangle
    if startPoint == True and endPoint == True:
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 255), 2)
    cv2.imshow('frame',frame)
    key = cv2.waitKey(waitTime) 
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()