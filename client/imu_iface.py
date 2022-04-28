import json
import time

import paho.mqtt.client as mqtt


class ImuIface:
    def __init__(self, username):
        self.tilt_direction = ""
        self.imu_dict = {}
        self.is_idle = False
        self.is_upward_push = False
        self.is_downward_push = False
        self.is_shooting = False
        self.room = f'team3/controller/{username}'
        self.server = 'test.mosquitto.org'
        self.qos = 0
        self.previous_time = 0
        self.new_time = 0
        print(self.server, self.room)

        def on_connect(client, userdata, flags, rc):
            # print("\nConnection returned result: " + str(rc))
            client.subscribe(self.room, qos=self.qos)

        def on_message(client, userdata, message):
            self.new_time = time.time()
            self.imu_dict = json.loads(message.payload)
            self.is_idle = self.imu_dict['is_idle']
            self.is_upward_push = self.imu_dict['is_upward_push']
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
