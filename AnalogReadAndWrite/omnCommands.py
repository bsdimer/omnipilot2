#!/usr/bin/env python3
from flask import Flask, jsonify, redirect, url_for, request
import serial  # Module needed for serial communication
import sqlite3

conn = sqlite3.connect('omnipilot.db')

# Initialize serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()

app = Flask(__name__)


@app.route('/cmd', methods=['POST'])
def start():
    slot = request.form['slot']
    key = request.form['key']
    value = request.form['value']
    command = "%s|%s|%s" % (slot, key, value)
    ser.write(command.encode('utf-8'))
    return


if __name__ == '__main__':
    app.run(debug=True)
