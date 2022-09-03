#!/usr/bin/env python3
from bitstring import BitStream
from .abstract_command import AbstractCommand

# robot arm command ids in accordance with BigRobotArmFirmware
GOTO_COMMAND_ID = 1


class PositionCommand(AbstractCommand):
  def __init__(self):
    super().__init__(GOTO_COMMAND_ID)

  def parse_serial_response(self, response: bytes):
    data = response.splitlines()
    stream = BitStream(data[1])
    b, s, e, wr, w, = self._parse_motor_values(stream)
    result = f"BigRobotArm::POSITION: B{b} S{s} E{e} WR{wr} W{w}\n"
    result += super().parse_serial_response(response)
    return result
