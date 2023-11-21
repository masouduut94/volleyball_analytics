import numpy as np
import cv2

# contours = [np.array([[1, 1], [10, 50], [50, 50]], dtype=np.int32),
#             np.array([[99, 99], [99, 60], [60, 99]], dtype=np.int32)]

line1 = np.array([[100, 100], [250, 800]], dtype=np.int32)
line2 = np.array([[700, 100], [850, 800]], dtype=np.int32)

img = np.ones([1000, 1000, 3], np.uint8)
pt1 = [300, 400]
pt2 = [500, 500]
pt3 = [200, 300]
for cnt in [line1, line2]:
    cv2.drawContours(img, [cnt], 0, (255, 255, 255), 2)

cv2.circle(img, tuple(pt1), 10, (255, 0, 0), 2)
cv2.circle(img, tuple(pt2), 10, (0, 255, 0), 2)
cv2.circle(img, tuple(pt3), 10, (0, 0, 255), 2)

dist1 = cv2.pointPolygonTest(line1, tuple(pt1), True)
dist2 = cv2.pointPolygonTest(line1, tuple(pt2), True)
dist3 = cv2.pointPolygonTest(line1, tuple(pt3), True)

dist4 = cv2.pointPolygonTest(line2, tuple(pt1), True)
dist5 = cv2.pointPolygonTest(line2, tuple(pt2), True)
dist6 = cv2.pointPolygonTest(line2, tuple(pt3), True)


print(f"blue pt <-> left line distance: {dist1}")
print(f"green pt <-> left line distance: {dist2}")
print(f"red pt <-> left line distance: {dist3}")

print(f"blue pt <-> right line distance: {dist4}")
print(f"green pt <-> right line distance: {dist5}")
print(f"red pt <-> right line distance: {dist6}")

cv2.imshow('output', img)
cv2.waitKey(0)
