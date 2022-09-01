#!/usr/bin/env python3
from bitstring import BitStream, pack
from .abstract_command import AbstractCommand

# robot arm command ids in accordance with BigRobotArmFirmware
GOTO_COMMAND_ID = 1


class PositionCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(GOTO_COMMAND_ID)
