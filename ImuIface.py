import json
import socket


# TODO -- create this class
class ImuIface:
    def __init__(self):
        # self.network = network
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port

        self.host, self.port = socket.gethostbyname(
            socket.gethostname()), 65000
        self.server_address = (self.host, self.port)
        self.sock.bind((self.host, self.port))
        self.tiltDirection = ""
        self.IMU_dict = {}

    def calibrate(self, is_calibrating: bool):
        return Exceptions.NotImplementedException

    def get_imu_info(self):
        # places info from IMU into dictionary IMU_dict
        message, address = self.sock.recvfrom(4096)
        self.IMU_dict = json.loads(message)

        gyro_x_angle = self.IMU_dict["x_gyro"]
        gyro_y_angle = self.IMU_dict["y_gyro"]
        gyro_z_angle = self.IMU_dict["z_gyro"]

        # print(self.IMU_dict)
        is_forward_tilt = 5 < gyro_x_angle < 80
        is_right_tilt = gyro_y_angle > -80 and gyro_y_angle < -5
        is_left_tilt = gyro_y_angle > 5 and gyro_y_angle < 80
        is_backward_tilt = gyro_x_angle > -80 and gyro_x_angle < -5

        self.IMU_dict['is_forward_tilt'] = is_forward_tilt
        self.IMU_dict['is_backward_tilt'] = is_backward_tilt
        self.IMU_dict['is_right_tilt'] = is_right_tilt
        self.IMU_dict['is_left_tilt'] = is_left_tilt

        return self.IMU_dict

    def get_tilt(self):
        gyro_x_angle = self.IMU_dict["x_gyro"]
        gyro_y_angle = self.IMU_dict["y_gyro"]
        gyro_z_angle = self.IMU_dict["z_gyro"]

        is_forward_tilt = 5 < gyro_x_angle < 80
        is_right_tilt = gyro_y_angle > -80 and gyro_y_angle < -5
        is_left_tilt = gyro_y_angle > 5 and gyro_y_angle < 80
        is_backward_tilt = gyro_x_angle > -80 and gyro_x_angle < -5

        tilt_string = ""
        if self.IMU_dict["is_idle"]:
            tilt_string += "idle\t"
        elif is_forward_tilt:
            if is_right_tilt:
                tilt_string += 'tilting forward-right\t'
            elif is_left_tilt:
                tilt_string += 'tilting forward-left\t'
            else:
                tilt_string += 'tilting forward\t'
        elif is_backward_tilt:
            if is_right_tilt:
                tilt_string += 'tilting backward-right\t'
            elif is_left_tilt:
                tilt_string += 'tilting backward-left\t'
            else:
                tilt_string += 'tilting backward\t'
        elif is_right_tilt:
            tilt_string += 'tilting right\t'
        elif is_left_tilt:
            tilt_string += 'tilting left\t'

        self.tiltDirection = tilt_string
        return tilt_string
