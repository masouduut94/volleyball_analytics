import cv2

# load the input image
img = cv2.imread('/home/masoud/Desktop/p.png')
print('img: ', img.shape)
# convert the input image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# apply thresholding to convert grayscale to binary image
ret, thresh = cv2.threshold(gray, 150, 255, 0)

# find the contours
contours, hierarchy = cv2.findContours(thresh,
                                       cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("Number of contours detected:", len(contours))

# select the first contour
cnt = contours[1]
# print(cnt, cnt.shape)
# find the shortest distance from point[250,250]
dist1 = cv2.pointPolygonTest(cnt, (50, 50), True)

# print the shortest distance between the point 1 and contour detected.
print('Shortest distance of Point 1 from contour:', dist1)
dist2 = cv2.pointPolygonTest(cnt, (70, 70), True)

# print the shortest distance between the point 2 and contour detected.
print('Shortest distance of Point 2 from contour:', dist2)

# draw the point [250,250] on the image
cv2.circle(img, (250, 250), 4, (0, 0, 255), -1)
cv2.putText(img, "Point 1", (255, 255),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
cv2.circle(img, (350, 250), 4, (0, 0, 255), -1)
cv2.putText(img, "Point 2", (355, 255),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# draw contour on the input image
cv2.drawContours(img, [cnt], -1, (0, 255, 255), 3)

# display the image with drawn extreme points
while True:
    cv2.imshow("Extreme Points", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cv2.destroyAllWindows()
