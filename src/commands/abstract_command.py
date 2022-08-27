#!/usr/bin/env python3
from bitstring import BitStream, pack
import string


class AbstractCommand:
  def __init__(self, command_id, param_types):
    self.command_id = command_id
    self.param_types = param_types if param_types != None else []

  def parse_command(self, command):
    stream = BitStream()
    stream.append(pack('uint:8', self.command_id))
    self.parse_commandParams(stream, command)
    print(stream)
    return stream.tobytes()

  def parse_commandParams(self, stream, command):
    params = command.split()
    # first part of command parameters (positions, speeds, accels) is command type (eg: G0, G1, M250, G28)
    params.pop(0)
    # add command parameters
    for i, p in enumerate(params):
      value = int(p.strip(string.ascii_letters))
      valueType = self.param_types[i] if len(
          self.param_types) > i else 'int:32'
      stream.append(pack(valueType, value))

  def parse_response(self, response):
    return 'BigRobotArm::READY'
