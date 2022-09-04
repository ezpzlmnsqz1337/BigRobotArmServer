#!/usr/bin/env python3
from bitstring import BitStream
from commands.abstract_command import AbstractCommand

GRIPPER_COMMAND_ID = 6


class GripperCommand(AbstractCommand):
  def __init__(self):
    super().__init__(GRIPPER_COMMAND_ID, ["uint:8", "uint:8"])

  def parse_serial_response(self, response: bytes):
    data = response.split(b'\r\n')
    stream = BitStream(data[1])
    e = stream.read("uint:8")
    p = stream.read("uint:8")
    result = f"BigRobotArm::GRIPPER: E{e} P{p}\n"

    result += super().parse_serial_response(response)
    return result
