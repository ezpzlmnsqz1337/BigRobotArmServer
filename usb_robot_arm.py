#!/usr/bin/env python3
from __future__ import annotations

import math
import time
from typing import Any

import serial

USB_PORT = "/dev/ttyUSB0"
USB_FALLBACK_PORT = "/dev/ttyUSB1"
BAUD_RATE = 250000
COMMAND_READY_TIMEOUT_SECONDS = 30
usb: Any | None = None


class ConnectionLostError(RuntimeError):
   pass


def clearConnection() -> None:
   global usb
   if usb is not None:
      try:
         if usb.is_open:
            usb.close()
      except serial.SerialException:
         pass
   usb = None


def _open_serial(port: str) -> Any:
   return serial.Serial(port, BAUD_RATE, timeout=2)


def connect() -> bool:
    global usb

    for port in (USB_PORT, USB_FALLBACK_PORT):
        try:
            usb = _open_serial(port)
            print("USB: Connection successfull!")
            usb.readline()
            return True
        except (serial.SerialException, OSError):
            clearConnection()

    print(
        "ERROR - Could not open USB serial port. "
        "Please check your port name and permissions."
    )
    return False

def disconnect() -> None:
    print("USB: Disconnection successfull!")
    clearConnection()

def isConnected() -> bool:
    return usb is not None and usb.is_open

def degToSteps(b: float, s: float, e: float, wr: float, w: float) -> bytes:
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


def sendCommand(command: str) -> str:
    if usb is None or not usb.is_open:
        raise ConnectionLostError('Serial connection is not open')

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
            if line:
                response += f'{line}\n'
    except (serial.SerialException, OSError, UnicodeDecodeError) as error:
        clearConnection()
        raise ConnectionLostError(
            'Serial connection lost during command forwarding'
        ) from error

    print(response)
    return response
