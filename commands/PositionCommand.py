#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand
from bitstring import BitStream, pack

# robot arm command ids in accordance with BigRobotArmFirmware
GOTO_COMMAND_ID = 1


class PositionCommand(AbstractCommand):
  def __init__(self):
    super().__init__(GOTO_COMMAND_ID)
