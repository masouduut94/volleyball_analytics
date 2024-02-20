import cv2

rect = (0, 0, 0, 0)
start_point = False
end_point = False


def on_mouse(event, x, y, flags, params):
    global rect, start_point, end_point
    # get mouse click
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point and end_point:
            start_point = False
            end_point = False
            rect = (0, 0, 0, 0)
        if not start_point:
            rect = (x, y, 0, 0)
            start_point = True
        elif not end_point:
            rect = (rect[0], rect[1], x, y)
            end_point = True


cap = cv2.VideoCapture(0)
waitTime = 50
(grabbed, frame) = cap.read()
while cap.isOpened():
    (grabbed, frame) = cap.read()
    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)
    # drawing rectangle
    if start_point and end_point:
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 255), 2)
    cv2.imshow('frame', frame)
    key = cv2.waitKey(waitTime)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()
