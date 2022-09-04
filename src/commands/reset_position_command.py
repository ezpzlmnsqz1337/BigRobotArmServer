#!/usr/bin/env python3
from bitstring import BitStream
from commands.abstract_command import AbstractCommand

RESET_POSITION_COMMAND_ID = 3


class ResetPositionCommand(AbstractCommand):
  def __init__(self):
    super().__init__(RESET_POSITION_COMMAND_ID)

  def parse_serial_response(self, response: bytes):
    data = response.split(b'\r\n')
    stream = BitStream(data[1])
    b, s, e, wr, w, = self._parse_motor_values(stream)
    result = f"BigRobotArm::POSITION: B{b} S{s} E{e} WR{wr} W{w}\n"

    result += super().parse_serial_response(response)
    return result
