import cv2
import dlib


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

    def get_object_position(self):
        ret_val, img = self.cam.read()
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detects = self.detector(rgb_image)
        center = self.camera_width // 2, self.camera_height // 2
        for detect in detects:
            center = ((detect.right() + detect.left()) // 2,
                      (detect.top() + detect.bottom()) // 2)
            if self.show_cam:
                lt = (detect.left(), detect.top())
                rb = (detect.right(), detect.bottom())
                cv2.rectangle(img, lt, rb, self.color_green, self.line_width)
                cv2.circle(img, center, 3, self.color_green, self.line_width)
        if self.show_cam:
            cv2.imshow('webcam', img)
        return center

    def get_level(self):
        level = self.num_levels - \
            (self.num_levels /
             self.camera_height *
             self.get_object_position()[1])
        return int(level)
