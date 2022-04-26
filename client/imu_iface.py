import json
import time

import paho.mqtt.client as mqtt


class ImuIface:
    def __init__(self):
        self.tilt_direction = ""
        self.imu_dict = {}
        self.is_idle = False
        self.is_upward_push = False
        self.is_downward_push = False
        self.is_shooting = False
        self.x_gyro = 0.0
        self.y_gyro = 0.0
        self.room = 'team3/controller/will'
        self.server = 'test.mosquitto.org'
        self.qos = 0
        self.previous_time = 0
        self.new_time = 0

        def on_connect(client, userdata, flags, rc):
            print("Connection returned result: " + str(rc))
            client.subscribe(self.room, qos=self.qos)

        def on_message(client, userdata, message):
            self.new_time = time.time()
            self.imu_dict = json.loads(message.payload)
            self.x_gyro = self.imu_dict['x_gyro']
            self.y_gyro = self.imu_dict['y_gyro']
            self.is_idle = self.imu_dict['is_idle']
            self.is_upward_push = self.imu_dict['is_forward_push']
            self.is_downward_push = self.imu_dict['is_downward_push']
            self.is_shooting = self.imu_dict['is_shooting']

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print('Unexpected Disconnect')
            else:
                print('Expected Disconnect')

        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.connect_async(self.server)
        self.client.loop_start()

    # def update_imu_info(self):
    #     # places info from IMU into dictionary IMU_dict
    #     message, address = self.sock.recvfrom(4096)
    #     self.IMU_dict = json.loads(message)
    #
    #     self.is_forward_tilt = 5 < self.IMU_dict["x_gyro"] < 80
    #     self.is_backward_tilt = -80 < self.IMU_dict["x_gyro"] < -5
    #     self.is_right_tilt = -80 < self.IMU_dict["y_gyro"] < -5
    #     self.is_left_tilt = 5 < self.IMU_dict["y_gyro"] < 80
    #     self.is_idle = self.IMU_dict['is_idle']
    #     self.is_pushing = self.IMU_dict['is_pushing']

    # def get_tilt(self):
    #     is_forward_tilt = 5 < self.IMU_dict["x_gyro"] < 80
    #     is_right_tilt = -80 < self.IMU_dict["y_gyro"] < -5
    #     is_left_tilt = 5 < self.IMU_dict["y_gyro"] < 80
    #     is_backward_tilt = -80 < self.IMU_dict["x_gyro"] < -5
    #
    #     tilt_string = ""
    #     if self.IMU_dict["is_idle"]:
    #         tilt_string += "idle\t"
    #     elif is_forward_tilt:
    #         if is_right_tilt:
    #             tilt_string += 'tilting forward-right\t'
    #         elif is_left_tilt:
    #             tilt_string += 'tilting forward-left\t'
    #         else:
    #             tilt_string += 'tilting forward\t'
    #     elif is_backward_tilt:
    #         if is_right_tilt:
    #             tilt_string += 'tilting backward-right\t'
    #         elif is_left_tilt:
    #             tilt_string += 'tilting backward-left\t'
    #         else:
    #             tilt_string += 'tilting backward\t'
    #     elif is_right_tilt:
    #         tilt_string += 'tilting right\t'
    #     elif is_left_tilt:
    #         tilt_string += 'tilting left\t'
    #
    #     self.tiltDirection = tilt_string
    #     return tilt_string
