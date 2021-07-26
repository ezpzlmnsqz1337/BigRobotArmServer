#!/usr/bin/env python3
from bitstring import BitStream, pack
import string


class AbstractCommand:
  def __init__(self, commandId) -> None:
    self.commandId = commandId

  def parseCommand(self, command):
    stream = BitStream()
    stream.append(pack('uint:8', self.commandId))
    self.parseCommandData(stream, command)
    return stream

  def parseCommandData(self, stream, command):
    return

  def parseResponse(self, response):
    return

  def parseJointData(self, stream, message):
    jointsData = message.split()
    # first part of joint data (positions, speeds, accels) is command type (eg: G0, G1, M250, G28)
    jointsData.pop(0)
    # add joint positions without the letters
    for j in jointsData:
      steps = int(j.strip(string.ascii_letters))
      stream.append(pack('int:32', steps))
      print(stream)
