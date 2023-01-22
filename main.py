#!/usr/bin/python3
import os
import sys
import time
import logging
import RPi.GPIO as GPIO
import requests
import board
import busio
import adafruit_ltr390
import spidev as SPI
import sqlite3

# sys.path.append("..")
sys.path.append('/opt/lib')
from lib import LCD_1inch8
from PIL import Image, ImageDraw, ImageFont

# Initial parameters
enableLogging = False
timetick = 5  # ticktime in seconds
pwmstart = 0  # pwm is the value in percent of the starting energy for the dimmer
pwmstep = 10  # step in percents for increase or decrease the value depending on the input readings
uvweight = 2  # the weight constant which applies a weight on the UV sensor data. For example when the senser is under the glass his readings will be less than the normal values

# Initialize display
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

# Initialize logging
logging.basicConfig(filename='/var/log/omnipilot.log', encoding='utf-8', level=logging.DEBUG)

# Initialize DB
try:
    conn = sqlite3.connect('sensors.db')
    conn.execute('''CREATE TABLE measurements
             (id INT PRIMARY KEY     NOT NULL,
             created        TEXT     NOT NULL,
             uvlight        REAL,
             amblight       REAL,
             acpower            REAL,
             feedinpower        REAL ,
             solaxapifails  INT,
             pwm            REAL);''')
except Exception as e:
    logging.error(e)

try:
    disp = LCD_1inch8.LCD_1inch8()
    Lcd_ScanDir = LCD_1inch8.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    # Initialize library.
    disp.Init()
    # Clear display.
except IOError as e:
    logging.error(e)
except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    exit()

# Initialize PWM pin
pwmpin = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwmpin, GPIO.OUT)
pi_pwm = GPIO.PWM(pwmpin, 1000)
pi_pwm.start(pwmstart)
pwmcurrent = 0.0

# Initialize I2C communication for the UV sensor
i2c = busio.I2C(board.SCL, board.SDA)
ltr = adafruit_ltr390.LTR390(i2c)
solaxurl = 'https://www.solaxcloud.com/proxyApp/proxy/api/getRealtimeInfo.do?tokenId=20221009183929844546800&sn=SVZ77J5ZL5'

# Initialize input variables
acpower = 0
solaxApiFails = 0
feedinpower = 0


def gatherSolaxData():
    global solaxApiFails
    global acpower
    global feedinpower
    request = requests.get(solaxurl)
    result = request.json()
    try:
        acpower = result['result']['acpower']
        feedinpower = result['result']['feedinpower']
    except:
        solaxApiFails = solaxApiFails + 1
        print("Error getting data from Solax API. Using previous values")
    return feedinpower


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def calculatePwmPercent():
    global pwmcurrent
    global uvweight
    if feedinpower > 0:
        pwmcurrent = 100
    if 0 > feedinpower > -100:
        pwmcurrent = pwmcurrent + pwmstep * (ltr.uvs * uvweight / 100)
    elif feedinpower < -100:
        pwmcurrent = pwmcurrent - (feedinpower * -1)
    else:
        pwmcurrent = pwmcurrent - pwmstep
    if pwmcurrent < 0:
        pwmcurrent = 0
    if pwmcurrent > 100:
        pwmcurrent = 100


def log():
    if enableLogging:
        logging.info("UV:%s \tAmb light:%s", ltr.uvs, ltr.light)
        logging.info("acp:%s feedinp: %s", acpower, feedinpower)
        logging.info("cmp: %s", acpower + feedinpower)
        logging.info("solax api fails: %s", solaxApiFails)
        logging.info("PWM %%: %s", pwmcurrent)
        logging.info("=========================")

    print("UV:", ltr.uvs, "\t\tAmb light:", ltr.light)
    print("acp:", acpower, " feedinp:", feedinpower)
    print("cmp:", acpower + feedinpower)
    print("solax api fails:", solaxApiFails)
    print("PWM %:", pwmcurrent)
    print("=========================")
    disp.clear()

    # Create blank image for drawing.
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("../Font/Font00.ttf", 12)
    text = "UV: {0} \tAmb light: {1}\nacp: {2} \nfeedinp: {3}\nconsumption: {4}\n solax api fails: {5}\nPWM %:{6}".format(
        ltr.uvs, ltr.light, acpower, feedinpower, (acpower + feedinpower), solaxApiFails, pwmcurrent)
    draw.text((0, 0), text, fill="WHITE", font=font)
    disp.ShowImage(image)


while True:
    log()
    gatherSolaxData()
    calculatePwmPercent()
    pi_pwm.ChangeDutyCycle(pwmcurrent)
    time.sleep(timetick)
