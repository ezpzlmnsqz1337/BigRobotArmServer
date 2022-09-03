#!/usr/bin/env python3

from typing import List
from bitstring import BitStream, pack
import string


class AbstractCommand:
  def __init__(self, command_id: int, param_types: List[str] = None):
    self.command_id = command_id
    self.param_types = param_types if param_types != None else []

  def parse_web_message(self, command: str):
    stream = BitStream()
    stream.append(pack("uint:8", self.command_id))
    self.parse_web_message_params(stream, command)
    return stream.tobytes()

  def parse_web_message_params(self, stream: BitStream, command: str):
    params = command.split()
    # first part of command parameters (positions, speeds, accels) is command type (eg: G0, G1, M250, G28)
    params.pop(0)
    # add command parameters
    for i, p in enumerate(params):
      value = int(p.strip(string.ascii_letters))
      valueType = self.param_types[i] if len(
          self.param_types) > i else 'intle:32'
      stream.append(pack(valueType, value))

  def _parse_motor_values(self, stream: BitStream):
    p_base: int = stream.read("intle:32")
    p_shoulder: int = stream.read("intle:32")
    p_elbow: int = stream.read("intle:32")
    p_wrist_rotate: int = stream.read("intle:32")
    p_wrist: int = stream.read("intle:32")
    return p_base, p_shoulder, p_elbow, p_wrist_rotate, p_wrist

  def parse_serial_response(self, response: bytes):
    return 'BigRobotArm::READY'
