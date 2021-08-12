#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand
from bitstring import BitStream, pack

RESET_POSITION_COMMAND_ID = 3


class ResetPositionCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(RESET_POSITION_COMMAND_ID)
