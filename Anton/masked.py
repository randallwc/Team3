import numpy as np
import cv2
import math

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def get_pos(xPos, yPos):
    xPosPercent = xPos / 640
    yPosPercent = yPos / 480
    return xPosPercent, yPosPercent


# Start of program
cap = cv2.VideoCapture(0)

# Takes a screenshot with SPACE
cv2.namedWindow("Calibration")

while True:
    ret, frame = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.rectangle(frame, (197, 197), (302, 302), (0, 255, 0), 4)
    cv2.imshow("Calibration", frame)

    k = cv2.waitKey(1)
    if k % 256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k % 256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_0.png"
        cv2.imwrite(img_name, frame[200:300, 200:300])
        print("{} written!".format(img_name))
cv2.waitKey(1)
cv2.destroyWindow('Calibration')

# Take the KMeans of image
# Method 1
#kmeansimg = cv2.imread('opencv_frame_0.png')
#Z = kmeansimg.reshape((-1,3))
#Z = np.float32(Z)
#criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
#K = 1
# ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
# Now convert back into uint8, and make original image
#center = np.uint8(center)
#res = center[label.flatten()]
#res2 = res.reshape((kmeansimg.shape))
# cv2.imshow('res2',res2)

# Method 2
n_clusters = 10
img = cv2.imread("opencv_frame_0.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# represent 	as row*column,channel number
img = img.reshape((img.shape[0] * img.shape[1], 3))
clt = KMeans(n_clusters)  # cluster number
clt.fit(img)


# Setting constants
x = 0
y = 0
h = 0
nLevels = 4  # change this to adjust the total number of Levels
nLines = nLevels - 1
lvPlace = list(range(1, nLevels + 1))
yPlacements = list(range(0, nLevels))
ylim = 479
linePlacement = ylim // (nLevels)
is_visible = False

# Determine BGR range (initialization)
b_min = clt.cluster_centers_[0][0]
g_min = clt.cluster_centers_[0][1]
r_min = clt.cluster_centers_[0][2]

b_max = clt.cluster_centers_[0][0]
g_max = clt.cluster_centers_[0][1]
r_max = clt.cluster_centers_[0][2]

# i [0, 1, 2, ..., n_clusters - 1]; redundant to check i = 0
for i in range(1, n_clusters):
    if b_min > clt.cluster_centers_[i][0]:
        b_min = clt.cluster_centers_[i][0]
    if g_min > clt.cluster_centers_[i][1]:
        g_min = clt.cluster_centers_[i][1]
    if r_min > clt.cluster_centers_[i][2]:
        r_min = clt.cluster_centers_[i][2]

    if b_max < clt.cluster_centers_[i][0]:
        b_max = clt.cluster_centers_[i][0]
    if g_max < clt.cluster_centers_[i][1]:
        g_max = clt.cluster_centers_[i][1]
    if r_max < clt.cluster_centers_[i][2]:
        r_max = clt.cluster_centers_[i][2]

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Colour Mask
    # Purple: ([130, 70, 70], [145, 255, 255])
    lower = np.array([b_min, g_min, r_min])
    upper = np.array([b_max, g_max, r_max])
    # Find colours in camera feed
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Making N lines across the screen
    for i in range(nLines):
        eye1 = i + 1
        L = linePlacement * eye1
        yPlacements[i] = L
        cv2.line(frame, (0, L), (639, L), (0, 0, 255), 3)

    # Template Matching
    # template = cv2.imread("opencv_frame_0.png", 0)
    #template = res2
    # w,h = template.shape[::-1]
    #template_match_result = cv2.matchTemplate(grayFrame, template, cv2.TM_CCOEFF_NORMED)

        # Method 1
    #threshold = 0.8
    #loc = np.where(template_match_result >= threshold)
    # for pt in zip(*loc[::-1]):
    #    cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)

        # Method 2
    #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_match_result)
    #top_left = max_loc
    #bottom_right = (top_left[0] + w, top_left[1] + h)
    #cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 4)

    # Creating Bounding Box
    if contours:
        max_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour) > cv2.contourArea(max_contour):
                max_contour = contour
        contour = max_contour
        approx = cv2.approxPolyDP(
            contour,
            0.01 *
            cv2.arcLength(
                contour,
                True),
            True)
        x, y, w, h = cv2.boundingRect(approx)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
        is_visible = True
    else:
        is_visible = False

    # Printing Lines on Screen
    topLim = nLines - 1
    yCenter = y + (h // 2)
    xCenter = x + (w // 2)
    posPer = get_pos(xCenter, yCenter)
    if (yCenter < yPlacements[0]):
        print("Level 1 " + str(posPer))
    elif (yCenter > yPlacements[topLim]):
        print("Level " + str(nLevels) + " " + str(posPer))
    else:
        for i in range(nLines):
            line2 = i + 1
            if (yCenter > yPlacements[i]) and (yCenter < yPlacements[line2]):
                print("Level " + str(lvPlace[line2]) + " " + str(posPer))

    # Display the resulting frame
    cv2.imshow('res', cv2.bitwise_and(frame, frame))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# when everything done, release the capture
cap.release()
cv2.destroyAllWindows()
