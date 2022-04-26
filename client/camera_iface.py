import cv2
import dlib


class CameraIface:
    def __init__(self, num_levels, use_camera: bool, show_cam=True):
        self.show_cam = show_cam
        self.camera_width = 640
        self.camera_height = 480
        self.num_levels = num_levels
        self.detector = dlib.get_frontal_face_detector()
        self.use_camera = use_camera
        self.cam = None
        self.toggle_camera()
        self.color_green = (0, 255, 0)
        self.line_width = 3
        self.counter_max = 60
        self.counter = self.counter_max
        self.previous_center = (
            self.camera_width // 2,
            self.camera_height // 2)

    def toggle_camera(self):
        if self.use_camera and self.cam is None:
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        elif not self.use_camera and self.cam is not None:
            self.cam.release()
            self.cam = None
            cv2.destroyAllWindows()

    def get_object_position(self):
        # only run every self.counter frames
        if self.counter > 0:
            self.counter -= 1
            return self.previous_center
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
                left_top = (detect.left(), detect.top())
                right_bottom = (detect.right(), detect.bottom())
                cv2.rectangle(
                    img,
                    left_top,
                    right_bottom,
                    self.color_green,
                    self.line_width)
                cv2.circle(img, center, 3, self.color_green, self.line_width)

        # show camera
        if self.show_cam:
            cv2.imshow('webcam', img)

        # update previous center
        self.previous_center = center
        return center

    def get_level(self):
        level = self.num_levels - \
            (self.num_levels /
             self.camera_height *
             self.get_object_position()[1])
        return int(level)
