#!/usr/bin/env python3

import serial  # Module needed for serial communication

# Initialize serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()

# Infinite loop
while 1:

    # If there is data available
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
