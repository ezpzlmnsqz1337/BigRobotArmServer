#!/usr/bin/env python3
from commands.abstract_command import AbstractCommand
from bitstring import BitStream

HOME_COMMAND_ID = 2


class HomeCommand(AbstractCommand):
  def __init__(self):
    super().__init__(HOME_COMMAND_ID)

  def parse_serial_response(self, response: bytes):
    data = response.split(b'\r\n')
    stream = BitStream(data[1])
    b, s, e, wr, w, = self._parse_motor_values(stream)
    result = f"BigRobotArm::POSITION: B{b} S{s} E{e} WR{wr} W{w}\n"

    result += super().parse_serial_response(response)
    return result
