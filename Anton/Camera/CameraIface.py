import cv2
import dlib
import numpy as np

class CameraIface:
    def __init__(self, num_levels, show_cam=True):
        self.show_cam = show_cam
        self.camera_width = 640
        self.camera_height = 480
        self.num_levels = num_levels
        self.detector = dlib.get_frontal_face_detector()
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.color_green = (0, 255, 0)
        self.line_width = 3
        self.counter_max = 200
        self.counter = self.counter_max
        self.previous_center = (
            self.camera_width // 2,
            self.camera_height // 2)
        self.directions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.top_level = 2
        self.mid_level = 1
        self.bot_level = 0

        self.left_vertical_line_x = int((self.camera_width // 2) - (self.camera_width*0.05))
        self.right_vertical_line_x = int((self.camera_width // 2) + (self.camera_width*0.05))
        self.upper_horizontal_line_y = int((self.camera_height // 2) - (self.camera_height*0.05))
        self.lower_horizontal_line_y = int((self.camera_height // 2) + (self.camera_height*0.05))



    def get_object_position(self):
        # only run every self.counter frames
        if self.counter > 0:
            self.counter -= 1
            return self.previous_center
        else:
            self.counter = self.counter_max

        # find face in screen
        _, img = self.cam.read()
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detects = self.detector(rgb_image)
        center = self.camera_width // 2, self.camera_height // 2
        for detect in detects:
            center = ((detect.right() + detect.left()) // 2,
                      (detect.top() + detect.bottom()) // 2)
            # only draw box if showing camera
            if self.show_cam:
                lt = (detect.left(), detect.top())
                rb = (detect.right(), detect.bottom())
                cv2.rectangle(img, lt, rb, self.color_green, self.line_width)
                cv2.circle(img, center, 3, self.color_green, self.line_width)

        # show camera
        if self.show_cam:
            cv2.line(img, (self.left_vertical_line_x, 0), (self.left_vertical_line_x, self.camera_height), self.color_green, self.line_width)
            cv2.line(img, (self.right_vertical_line_x, 0), (self.right_vertical_line_x, self.camera_height), self.color_green, self.line_width)
            cv2.line(img, (0, self.upper_horizontal_line_y), (self.camera_width, self.upper_horizontal_line_y), self.color_green, self.line_width)
            cv2.line(img, (0, self.lower_horizontal_line_y), (self.camera_width, self.lower_horizontal_line_y), self.color_green, self.line_width)
            cv2.imshow('webcam', cv2.flip(img, 1))

        # update previous center
        self.previous_center = center
        return center

    def get_level(self):
        level = self.num_levels - \
            (self.num_levels /
             self.camera_height *
             self.get_object_position()[1])
        return int(level)

    def get_xy_level(self):
        object_pos = self.get_object_position()
        if object_pos[0] < self.left_vertical_line_x:
            level_x = self.top_level
        elif object_pos[0] > self.right_vertical_line_x:
            level_x = self.bot_level
        else:
            level_x = self.mid_level

        if object_pos[1] < self.upper_horizontal_line_y:
            level_y = self.top_level
        elif object_pos[1] > self.lower_horizontal_line_y:
            level_y = self.bot_level
        else:
            level_y = self.mid_level
        return [int(level_x), int(level_y)]

    def get_directions(self):
        # set the directions in the dictionary
        # For the first row of movements (make opposite direction false first for smoother transition)
        xy_level = self.get_xy_level()
        curr_y = xy_level[1]
        curr_x = xy_level[0]
        # setting the direction in y
        if curr_y == self.top_level:
            self.directions['down'] = False
            self.directions['up'] = True
        elif curr_y == self.mid_level:
            self.directions['down'] = False
            self.directions['up'] = False
        # if curr_y == self.bot_level:
        else:
            self.directions['up'] = False
            self.directions['down'] = True

        # setting the direction in x
        if curr_x == self.top_level:
            self.directions['left'] = False
            self.directions['right'] = True
        elif curr_x == self.mid_level:
            self.directions['right'] = False
            self.directions['left'] = False
        # if curr_x == self.bot_level:
        else:
            self.directions['right'] = False
            self.directions['left'] = True

        return self.directions
