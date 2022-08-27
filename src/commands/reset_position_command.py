#!/usr/bin/env python3
from abstract_command import AbstractCommand
from bitstring import BitStream, pack

RESET_POSITION_COMMAND_ID = 3


class ResetPositionCommand(AbstractCommand):
  def __init__(self):
    super().__init__(RESET_POSITION_COMMAND_ID)
