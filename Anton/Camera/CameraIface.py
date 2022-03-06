import numpy as np
import cv2
import math

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

class CameraIface:
    def __init__(self, camera_width=640, camera_height=480, num_levels=3):
        # ... initialize the class with constant values here ...
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.num_levels = num_levels
        # ... add member variables here and if you don't know what they should be set to then say
        # self.variable_name = None
        self.x = 0
        self.y = 0
        self.h = 0
        self.w = 0
        self.nLines = num_levels - 1
        self.lvPlace = list(range(1, num_levels + 1))
        self.yPlacements = list(range(0, num_levels))
        self.linePlacement = camera_height // (num_levels)
        self.is_visible = False

        self.b_min = 0
        self.g_min = 0
        self.r_min = 0
        self.b_max = 0
        self.g_max = 0
        self.r_max = 0
        
        # Camera Program
        cap = cv2.VideoCapture(0)

        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()
        
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
            # Colour Mask
            # Purple: ([130, 70, 70], [145, 255, 255])
            lower = np.array([self.b_min, self.g_min, self.r_min])
            upper = np.array([self.b_max, self.g_max, self.r_max])
            # Find colours in camera feed
            mask = cv2.inRange(hsv, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
            # Making N lines across the screen
            for i in range(self.nLines):
                eye1 = i + 1
                L = self.linePlacement * eye1
                self.yPlacements[i] = L
                cv2.line(frame, (0, L), (639, L), (0, 0, 255), 3)
                
            # Creating Bounding Box
            if contours:
                max_contour = contours[0]
                for contour in contours:
                    if cv2.contourArea(contour) > cv2.contourArea(max_contour):
                        max_contour = contour
                contour = max_contour
                approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
                self.x, self.y,self.w, self.h = cv2.boundingRect(approx)
                cv2.rectangle(frame, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), 4)
                self.is_visible = True
            else:
                self.is_visible = False
        
            # Printing Lines on Screen
            topLim = self.nLines - 1
            yCenter = self.y + (self.h // 2)
            #xCenter = self.x + (self.w // 2)
            if (yCenter < self.yPlacements[0]):
                print("Level 1 ")
            elif (yCenter > self.yPlacements[topLim]):
                print("Level " + str(self.num_levels))
            else:
                for i in range(self.nLines):
                    line2 = i + 1
                    if (yCenter > self.yPlacements[i]) and (yCenter < self.yPlacements[line2]):
                        print("Level " + str(self.lvPlace[line2]))
        
            # Display the resulting frame
            cv2.imshow('res', cv2.bitwise_and(frame, frame))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # when everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

    def calibrate(self):
        # ... create a function that enters calibration mode here ... [DONE]
        # ... then store that calibration in the class ... []

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

        n_clusters = 10
        img = cv2.imread("opencv_frame_0.png")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # represent as row*column,channel number
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        clt = KMeans(n_clusters)  # cluster number
        clt.fit(img)

        # Determine BGR range (initialization)
        self.b_min = clt.cluster_centers_[0][0]
        self.g_min = clt.cluster_centers_[0][1]
        self.r_min = clt.cluster_centers_[0][2]

        self.b_max = clt.cluster_centers_[0][0]
        self.g_max = clt.cluster_centers_[0][1]
        self.r_max = clt.cluster_centers_[0][2]

        # i [0, 1, 2, ..., n_clusters - 1]; redundant to check i = 0
        for i in range(1, n_clusters):
            if self.b_min > clt.cluster_centers_[i][0]:
                self.b_min = clt.cluster_centers_[i][0]
            if self.g_min > clt.cluster_centers_[i][1]:
                self.g_min = clt.cluster_centers_[i][1]
            if self.r_min > clt.cluster_centers_[i][2]:
                self.r_min = clt.cluster_centers_[i][2]

            if self.b_max < clt.cluster_centers_[i][0]:
                self.b_max = clt.cluster_centers_[i][0]
            if self.g_max < clt.cluster_centers_[i][1]:
                self.g_max = clt.cluster_centers_[i][1]
            if self.r_max < clt.cluster_centers_[i][2]:
                self.r_max = clt.cluster_centers_[i][2] 
        pass

    def get_object_position(self):
        # ... create a function that returns the x, y position of the ball here ...
        x = self.x + (self.w//2)
        y = self.y + (self.h//2)
        # ... write the code that takes a picture and then returns the center position of the ball ...
        return x, y

