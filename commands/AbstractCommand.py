#!/usr/bin/env python3
from bitstring import BitStream, pack
import string


class AbstractCommand:
  def __init__(self, commandId, paramTypes=[]) -> None:
    self.commandId = commandId
    self.paramTypes = paramTypes

  def parseCommand(self, command):
    stream = BitStream()
    stream.append(pack('uint:8', self.commandId))
    self.parseCommandParams(stream, command)
    print(stream)
    return stream.tobytes()

  def parseCommandParams(self, stream, command):
    params = command.split()
    # first part of command parameters (positions, speeds, accels) is command type (eg: G0, G1, M250, G28)
    params.pop(0)
    # add command parameters
    for i, p in enumerate(params):
      value = int(p.strip(string.ascii_letters))
      valueType = self.paramTypes[i] if len(self.paramTypes) > i else 'int:32'
      stream.append(pack(valueType, value))

  def parseResponse(self, response):
    return 'BigRobotArm::READY'
