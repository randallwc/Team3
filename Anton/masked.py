import numpy as np
import cv2

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def find_histogram(clt):
	numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
	(hist, _) = np.histogram(clt.labels_, bins=numLabels)

	hist = hist.astype("float")
	hist /= hist.sum()

	return hist

def plot_colors2(hist, centroids):
	bar = np.zeros((50, 300, 3), dtype="uint8")
	startX = 0

	for (percent, color) in zip(hist, centroids):
		# plot the relative percentage of each cluster
		endX = startX + (percent * 300)
		cv2.rectangle(bar, (int(startX), 0), (int(endX), 50), color.astype("uint8").tolist(), -1)
		startX = endX
	
	# return the bar chart
	return bar

cap = cv2.VideoCapture(0)
y = 0
h = 0

nLevels = 6 # change this to adjust the total number of Levels
nLines = nLevels - 1
lvPlace = list(range(1, nLevels+1))
yPlacements = list(range(0, nLevels))
ylim = 479
linePlacement = ylim//(nLevels)

while(True):
    #Capture frame-by-frame
    ret, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #picks out the colour "red"
    # red under white light: ([0, 10, 10], [4, 255, 255])
    lower = np.array([0,10,10])
    upper = np.array([4,255,255])
    mask = cv2.inRange(hsv, lower, upper)

    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # red horizontal line
    #cv2.line(frame, (0, 157), (639, 157), (0, 0, 255), 3)
    # blue horizontal line
    #cv2.line(frame, (0, 314), (639, 314), (255, 0, 0), 3)

    # MAKING N lines across the screen
    for i in range(nLines):
        eye1 = i+1
        L = linePlacement*eye1
        yPlacements[i] = L
        cv2.line(frame, (0, L), (639, L), (0,0, 255), 3)

    if contours:
        max_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour)>cv2.contourArea(max_contour):
                max_contour=contour  
        contour=max_contour
        approx=cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True),True)
        x,y,w,h=cv2.boundingRect(approx)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)
#    if ((y+(h/2)) < 157):
#        print("Top")
#    elif ((y+(h/2)) > 314):
#        print("Bottom")
#    else:
#        print("Middle")
    topLim = nLines - 1
    yCenter = y + (h//2)
    if (yCenter < yPlacements[0]):
        print("Level 1")
    elif (yCenter > yPlacements[topLim]):
        print("Level " + str(nLevels))
    else:
        for i in range(nLines):
            line2 = i+1
            if (yCenter > yPlacements[i]) and (yCenter < yPlacements[line2]):
                print("Level " + str(lvPlace[line2]))



    #Display the resulting frame
    cv2.imshow('res', cv2.bitwise_and(frame, frame))
    #Focuses on object in box
    #if contours:
    #    cv2.imshow('section', frame[y:y+h, x:x+w])

    #img = frame[y+4:y+h-4,x+4:x+w-4]
    #img = img.reshape((img.shape[0] * img.shape[1],3)) #represent 	as row*column,channel number
    #clt = KMeans(n_clusters=3) #cluster number
    #clt.fit(img)
    #hist = find_histogram(clt)
    #bar = plot_colors2(hist, clt.cluster_centers_)
    #cv2.imshow('dominant', bar)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#when everything done, release the capture
cap.release()
cv2.destroyAllWindows()
