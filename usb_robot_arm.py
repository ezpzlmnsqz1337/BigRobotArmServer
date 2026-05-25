#!/usr/bin/env python3
from __future__ import annotations

import math
import time
from typing import Any, Callable

import serial

from job_manager import JobCancelledError

USB_PORT = "/dev/ttyUSB0"
USB_FALLBACK_PORT = "/dev/ttyUSB1"
BAUD_RATE = 250000
COMMAND_READY_TIMEOUT_SECONDS = 30
QUEUE_RETRY_DELAY_SECONDS = 0.05
BUFFERED_POSITION_COMMAND = 'Q0'
QUEUE_FLUSH_COMMAND = 'QFLUSH'
QUEUE_CLEAR_COMMAND = 'QCLEAR'
QUEUE_FULL_RESPONSE = 'BigRobotArm::QUEUE-FULL'
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


def _read_response_until_ready() -> str:
    serial_port = usb
    if serial_port is None:
        raise ConnectionLostError('Serial connection is not open')

    response = ''
    line = ''
    deadline = time.monotonic() + COMMAND_READY_TIMEOUT_SECONDS
    while 'READY' not in line:
        if time.monotonic() >= deadline:
            response += 'ERROR: Timed out waiting for READY\n'
            break
        time.sleep(0.1)
        line = serial_port.readline().decode().strip()
        if line:
            response += f'{line}\n'

    return response


def _send_serial_command(command: str) -> str:
    if usb is None or not usb.is_open:
        raise ConnectionLostError('Serial connection is not open')

    try:
        if command == 'G28':
            usb.write(b'G28\r')
        else:
            print(command.encode() + b'\r')
            usb.write(command.encode() + b'\r')

        response = _read_response_until_ready()
    except (serial.SerialException, OSError, UnicodeDecodeError) as error:
        clearConnection()
        raise ConnectionLostError(
            'Serial connection lost during command forwarding'
        ) from error

    print(response)
    return response


def _is_position_command(command: str) -> bool:
    return command.split(' ', 1)[0] == 'G0'


def _to_buffered_position_command(command: str) -> str:
    return BUFFERED_POSITION_COMMAND + command[2:]


def _cancel_buffered_motion() -> None:
    _send_serial_command(QUEUE_CLEAR_COMMAND)
    _send_serial_command(QUEUE_FLUSH_COMMAND)
    raise JobCancelledError('Job cancelled')


def _enqueue_buffered_position(
    command: str, is_cancel_requested: Callable[[], bool]
) -> str:
    while True:
        if is_cancel_requested():
            _cancel_buffered_motion()

        response = _send_serial_command(_to_buffered_position_command(command))
        if QUEUE_FULL_RESPONSE not in response:
            return response

        time.sleep(QUEUE_RETRY_DELAY_SECONDS)


def _flush_buffered_motion(is_cancel_requested: Callable[[], bool]) -> None:
    if is_cancel_requested():
        _cancel_buffered_motion()

    _send_serial_command(QUEUE_FLUSH_COMMAND)


def sendCommand(command: str) -> str:
    return _send_serial_command(command)


def sendBufferedJob(
    commands: list[str],
    on_progress: Callable[[str], None],
    is_cancel_requested: Callable[[], bool],
) -> None:
    has_buffered_motion = False

    for command in commands:
        normalized = command.strip()
        if not normalized:
            continue

        if _is_position_command(normalized):
            response = _enqueue_buffered_position(normalized, is_cancel_requested)
            has_buffered_motion = True
        else:
            if has_buffered_motion:
                _flush_buffered_motion(is_cancel_requested)
                has_buffered_motion = False
            response = _send_serial_command(normalized)

        on_progress(response)

    if has_buffered_motion:
        _flush_buffered_motion(is_cancel_requested)
