#!/usr/bin/env python3
import serial
import math
import time

USB_PORT = "/dev/ttyUSB0"
BAUD_RATE = 250000
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
  global usb
  usb = usb.close()


def is_connected():
  return usb != None


def deg_to_steps(b, s, e, wr, w):
  # 90°                   1°
  # base 6500             72,22
  # shoulder 10000        111,11
  # elbow 2600           28,88
  # wrist rotate 800      8,88
  # wrist 3000            33,33

  base = math.ceil(b * 72.22)
  shoulder = math.ceil(s * 111.11)
  elbow = math.ceil(e * 28.88)
  wrist_rotate = math.ceil(wr * 8.88)
  wrist = math.ceil(w * 33.33)

  return f'X{base} Y{shoulder} Z{elbow} E{wrist_rotate} F{wrist}'.encode()


def send_command(command):
  print(f'Sending: {command}\n')
  usb.write(command)
  usb.write(b'\r')

  response = ''
  line = ''
  while '200' not in line:
    time.sleep(0.1)
    line = usb.readline().decode().strip()
    if len(line) > 0:
      response += f'{line}\n'
    print(f'Line2: {line}')

  print(response)
  # usb.reset_input_buffer()
  return response
