#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand
from bitstring import BitStream, pack

# robot arm command ids in accordance with BigRobotArmFirmware
GOTO_COMMAND_ID = 1


class PositionCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(GOTO_COMMAND_ID)

  def parseCommand(self, command):
    """
    Parses command from website in string format to byte data.
    >>> example: parseGoToCommand('G0 B2000 S2500 E3000 WR3500 W4000')
        result (in hex): 0x000007d0000009c400000bb800000dac00000fa0
    """

    stream = BitStream()
    stream.append(pack('uint:8', GOTO_COMMAND_ID))
    return stream

  def parseCommandData(self, stream, command):
    self.parseJointData(stream, command)

  def parseResponse(self, response):
    return
