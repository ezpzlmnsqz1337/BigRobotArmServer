#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

END_COMMAND_ID = 10


class EndCommand(AbstractCommand):
  def __init__(self):
    super().__init__(END_COMMAND_ID)
