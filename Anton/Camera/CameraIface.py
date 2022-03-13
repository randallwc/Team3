import math
import sys

import cv2
import numpy as np
from sklearn.cluster import KMeans


class CameraIface:
    def __init__(self, n_clusters, num_levels):
        self.camera_width = 640
        self.camera_height = 480
        self.n_clusters = n_clusters
        self.img_name = "capture.png"

        # 4:3 aspect ratio
        # (self.camera_width / self.camera_height == (4/3)):
        self.xBoxMin = math.floor(self.camera_width * 0.31)
        self.xBoxMax = math.floor(self.camera_width * 0.47)
        self.yBoxMin = math.floor(self.camera_height * 0.42)
        self.yBoxMax = math.floor(self.camera_height * 0.63)

        self.num_levels = num_levels
        self.x = 0
        self.y = 0
        self.h = 0
        self.w = 0
        self.n_lines = self.num_levels - 1
        self.lv_place = list(range(1, self.num_levels + 1))
        self.y_placements = list(range(0, self.num_levels))
        self.line_placement = self.camera_height // self.num_levels
        self.is_visible = False
        self.b_min = 0
        self.g_min = 0
        self.r_min = 0
        self.b_max = 0
        self.g_max = 0
        self.r_max = 0

        # Camera Program
        self.cap1 = cv2.VideoCapture(0)
        self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)

    def calibrate(self):
        cv2.namedWindow("Calibration")
        print('press space while the object is in the bounding box. when you are happy with the image press esc')
        running = True
        while running:
            ret, frame = self.cap1.read()
            frame_raw = np.copy(frame)
            if not ret:
                print("failed to grab frame")
                running = False
            cv2.rectangle(frame, (self.xBoxMin - 3, self.yBoxMin - 3),
                          (self.xBoxMax + 2, self.yBoxMax + 2), (0, 255, 0), 4)
            cv2.imshow("Calibration", frame)

            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                cv2.imwrite(self.img_name,
                            frame_raw[self.xBoxMin:self.xBoxMax,
                                      self.yBoxMin:self.yBoxMax])
                print("{} written!".format(self.img_name))
        cv2.waitKey(1)
        cv2.destroyWindow('Calibration')

        img = cv2.imread(self.img_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # represent as row*column,channel number
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        clt = KMeans(self.n_clusters)  # cluster number
        clt.fit(img)

        # Determine BGR range (initialization)
        self.b_min = clt.cluster_centers_[0][0]
        self.g_min = clt.cluster_centers_[0][1]
        self.r_min = clt.cluster_centers_[0][2]

        self.b_max = clt.cluster_centers_[0][0]
        self.g_max = clt.cluster_centers_[0][1]
        self.r_max = clt.cluster_centers_[0][2]

        # i [0, 1, 2, ..., n_clusters - 1]; redundant to check i = 0
        for i in range(1, self.n_clusters):
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
        # Capture frame-by-frame
        ret, frame = self.cap1.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Colour Mask
        # Purple: ([130, 70, 70], [145, 255, 255])
        lower = np.array([self.b_min, self.g_min, self.r_min])
        upper = np.array([self.b_max, self.g_max, self.r_max])

        # Find colours in camera feed
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Making N lines across the screen
        for i in range(self.n_lines):
            eye1 = i + 1
            L = self.line_placement * eye1
            self.y_placements[i] = L
            cv2.line(frame, (0, L), (self.camera_width, L), (0, 0, 255), 3)

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
            self.x, self.y, self.w, self.h = cv2.boundingRect(approx)
            cv2.rectangle(frame, (self.x, self.y), (self.x +
                                                    self.w, self.y + self.h), (0, 255, 0), 4)
            self.is_visible = True
        else:
            self.is_visible = False

        # Display the resulting frame
        cv2.imshow('Tracking', cv2.bitwise_and(frame, frame))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap1.release()
            cv2.destroyAllWindows()
            sys.exit()

        x = self.x + (self.w // 2)
        y = self.y + (self.h // 2)
        return x, y

    def get_object_level(self):
        # Printing Lines on Screen
        top_lim = self.n_lines - 1
        y_center = self.y + (self.h // 2)
        curr_level = "Invalid Level"
        if y_center < self.y_placements[0]:
            curr_level = "Level 1"
        elif y_center > self.y_placements[top_lim]:
            curr_level = "Level " + str(self.num_levels)
        else:
            for i in range(self.n_lines):
                line2 = i + 1
                if (y_center > self.y_placements[i]) and (
                        y_center < self.y_placements[line2]):
                    curr_level = "Level " + str(self.lv_place[line2])

        return curr_level
