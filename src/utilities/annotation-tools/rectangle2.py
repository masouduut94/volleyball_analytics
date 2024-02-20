import cv2
import pandas as pd

ref_pt = []
drag = 0

data = {
    'frame': [0], 'x1': [None], 'y1': [None], 'x2': [None], 'y2': [None]
}

df = pd.DataFrame(data=data)


def click_and_crop(event, x, y, flags, param):
    global ref_pt, image, drag
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_pt = [(x, y)]
        drag = 1

    elif event == cv2.EVENT_LBUTTONUP:
        drag = 0

        ref_pt.append((x, y))
        cv2.rectangle(image, ref_pt[0], ref_pt[-1], (0, 255, 0), 2)
        cv2.imshow("image", image)
    elif event == cv2.EVENT_MOUSEMOVE and drag == 1:
        image = cv2.imread("a.jpg")
        cv2.rectangle(image, ref_pt[0], (x, y), (0, 255, 0), 2)


if __name__ == '__main__':

    cap = cv2.VideoCapture('data/videos/5.mp4')

    image = cv2.imread("a.jpg")
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    while True:
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            image = clone.copy()
        elif key == ord("q"):
            break

    cv2.destroyAllWindows()
