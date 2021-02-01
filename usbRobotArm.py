#!/usr/bin/env python3
import serial
import math
import time

USB_PORT = "/dev/ttyUSB1"
BAUD_RATE = 9600
usb = None

def connect():
   try:
      global usb
      usb = serial.Serial(USB_PORT, BAUD_RATE, timeout=2)
      print("USB: Connection successfull!")
      return True
   except:
      print("ERROR - Could not open USB serial port.  Please check your port name and permissions.")
      print("Exiting program.")
      return False

def disconnect():
   print("USB: Disconnection successfull!")
   global usb
   usb = usb.close()

def isConnected():
   return usb != None

def degToSteps(b,s,e,wr,w):
   # 90°                   1°
   # base 6500             72,22
   # shoulder 10000        111,11
   # elbow 20500           227,77
   # wrist rotate 800      8,88
   # wrist 3000            33,33

   base = math.ceil(b * 72.22)
   shoulder = math.ceil(s * 111.11)
   elbow = math.ceil(e * 227.77)
   wristRotate = math.ceil(wr * 8.88)
   wrist = math.ceil(w * 33.33)
   
   return f'X{base} Y{shoulder} Z{elbow} E{wristRotate} F{wrist}'.encode()

def sendCommand(command):   
   if command == "G28":
      usb.write(b'G28\r')
   elif command == "DEMO1":
      usb.write(b'G0 X500 Y2000 Z3000 E500 F1400\r')
   elif command == "DEMO2":
      usb.write(b'G0 X-700 Y2600 Z3200 E-500 F1400\r')
   elif command == "DEMO3":
      usb.write(b'G0 X-1500 Y0 Z15000 E0 F0\r')
   elif command == "DEMO4":
      usb.write(b'G0 X2000 Y2000 Z2000 E800 F2000\r')
   elif command == "DEMO5":
      usb.write(b'G0 X-2000 Y10000 Z-10250 E0 F2000\r')
   elif command == "P1":
      # pick up
      usb.write(b'G0 ' + degToSteps(0, 81.6, 91.3, 0, 82.7) + b'\r')
   elif command == "P2":
      # shoulder up
      usb.write(b'G0 ' + degToSteps(-35, 18.5, 92.6, -61.7, 25.7) + b'\r')
   elif command == "P3":
      # put down
      usb.write(b'G0 ' + degToSteps(-60, 75.6, 95, -180, -70.5) + b'\r') 
   else:
      print(b'' + command.encode() + b'\r')
      usb.write(b'' + command.encode() + b'\r')
      
   time.sleep(0.5)
   response = usb.readall().decode().strip()

   print(response)
   return response
