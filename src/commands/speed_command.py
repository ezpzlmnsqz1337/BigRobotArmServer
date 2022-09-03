#!/usr/bin/env python3
from .abstract_command import AbstractCommand
from bitstring import BitStream

SPEED_COMMAND_ID = 4


class SpeedCommand(AbstractCommand):
  def __init__(self):
    super().__init__(SPEED_COMMAND_ID)

  def parse_serial_response(self, response: bytes):
    data = response.splitlines()
    stream = BitStream(data[1])
    b, s, e, wr, w, = self._parse_motor_values(stream)
    result = f"BigRobotArm::SPEED: B{b} S{s} E{e} WR{wr} W{w}\n"
    result += super().parse_serial_response(response)
    return result
