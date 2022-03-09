import Exceptions
import Network
import socket
import sys
import json


# TODO -- create this class
class ImuIface:
    def __init__(self):
        #self.network = network
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        self.host, self.port = '172.20.10.2', 65000
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

        # print(self.IMU_dict)

    def get_tilt(self):
        gyroXangle = self.IMU_dict["x_gyro"]
        gyroYangle = self.IMU_dict["y_gyro"]
        gyroZangle = self.IMU_dict["z_gyro"]

        isForwardTilt = gyroXangle > 5 and gyroXangle < 80
        isRightTilt = gyroYangle > -80 and gyroYangle < -5
        isLeftTilt = gyroYangle > 5 and gyroYangle < 80
        isBackwardTilt = gyroXangle > -80 and gyroXangle < -5

        tiltString = ""
        if self.IMU_dict["is_idle"]:
            tiltString += "idle\t"
        elif isForwardTilt:
            if isRightTilt:
                tiltString += 'tilting forward-right\t'
            elif isLeftTilt:
                tiltString += 'tilting forward-left\t'
            else:
                tiltString += 'tilting forward\t'
        elif isBackwardTilt:
            if isRightTilt:
                tiltString += 'tilting backward-right\t'
            elif isLeftTilt:
                tiltString += 'tilting backward-left\t'
            else:
                tiltString += 'tilting backward\t'
        elif isRightTilt:
            tiltString += 'tilting right\t'
        elif isLeftTilt:
            tiltString += 'tilting left\t'

        self.tiltDirection = tiltString
        print(self.tiltDirection)
