#!/usr/bin/env python3
import serial  # Module needed for serial communication
import time
from datetime import datetime


# Initialize serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()

while 1:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        parts = line.split("|")
        running = parts[0]
        power1 = parts[1]
        power2 = parts[2]
        power3 = parts[3]
        print(datetime.now(), parts)
        # ToDo: save data into database
        time.sleep(1)
