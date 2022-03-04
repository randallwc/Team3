import matplotlib.pyplot as plt
import csv
import pandas as pd

#data = pd.read_csv('forward_tilt.csv')
#data = pd.read_csv('backwards_tilt.csv')
#data = pd.read_csv('right_tilt.csv')
#data = pd.read_csv('left_tilt.csv')
#data = pd.read_csv('forward_right_tilt.csv')
#data = pd.read_csv('forward_left_tilt.csv')
#data = pd.read_csv('backwards_right_tilt.csv')
#data = pd.read_csv('backwards_left_tilt.csv')

data = pd.read_csv('forward_tilt_gyro.csv')
#data = pd.read_csv('right_tilt_gyro.csv')
#data = pd.read_csv('left_tilt_gyro.csv')
#data = pd.read_csv('back_tilt_gyro.csv')


x = range(len(data['xG']))
y = range(len(data['yG']))
z = range(len(data['zG']))

plt.plot(x, data['gyroXangle'], color='r', label='x-axis')
plt.plot(y, data['gyroYangle'], color='g', label='y-axis')
plt.plot(z, data['gyroZangle'], color='b', label='z-axis')

plt.xlabel('Intervals')
plt.ylabel('Gyro Angle')
plt.title('Forward Tilt Gyro Angle for IMU')
plt.legend()
plt.show()

