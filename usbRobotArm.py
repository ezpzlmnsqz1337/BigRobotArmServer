#!/usr/bin/env python3
import serial
import math
import time

USB_PORT = "/dev/ttyUSB0"
BAUD_RATE = 250000
COMMAND_READY_TIMEOUT_SECONDS = 30
usb = None


class ConnectionLostError(RuntimeError):
   pass


def clearConnection():
   global usb
   if usb is not None:
      try:
         if usb.is_open:
            usb.close()
      except serial.SerialException:
         pass
   usb = None

def connect():
   try:
      global usb
      usb = serial.Serial(USB_PORT, BAUD_RATE, timeout=2)
      print("USB: Connection successfull!")
      usb.readline()
      return True
   except:
      try:
         usb = serial.Serial('/dev/ttyUSB1', BAUD_RATE, timeout=2)
         print("USB: Connection successfull!")
         usb.readline()
         return True
      except:
         print("ERROR - Could not open USB serial port.  Please check your port name and permissions.")
         return False

def disconnect():
   print("USB: Disconnection successfull!")
   clearConnection()

def isConnected():
   return usb is not None and usb.is_open

def degToSteps(b,s,e,wr,w):
   # 90°                   1°
   # base 6500             72,22
   # shoulder 10000        111,11
   # elbow 2600           28,88
   # wrist rotate 800      8,88
   # wrist 3000            33,33

   base = math.ceil(b * 72.22)
   shoulder = math.ceil(s * 111.11)
   elbow = math.ceil(e * 28.88)
   wristRotate = math.ceil(wr * 8.88)
   wrist = math.ceil(w * 33.33)
   
   return f'X{base} Y{shoulder} Z{elbow} E{wristRotate} F{wrist}'.encode()

def sendCommand(command):   
   try:
      if command == "G28":
         usb.write(b'G28\r')
      else:
         print(command.encode() + b'\r')
         usb.write(command.encode() + b'\r')
         
      response = ''
      line = ''
      deadline = time.monotonic() + COMMAND_READY_TIMEOUT_SECONDS
      while 'READY' not in line:
         if time.monotonic() >= deadline:
            response += 'ERROR: Timed out waiting for READY\n'
            break
         time.sleep(0.1)
         line = usb.readline().decode().strip()
         if len(line) > 0:
            response += f'{line}\n'
         # print(f'Line2: {line}')
   except (serial.SerialException, OSError, UnicodeDecodeError) as error:
      clearConnection()
      raise ConnectionLostError('Serial connection lost during command forwarding') from error

   print(response)
   # usb.reset_input_buffer()
   return response
