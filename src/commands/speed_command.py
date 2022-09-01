#!/usr/bin/env python3
from .abstract_command import AbstractCommand

SPEED_COMMAND_ID = 4


class SpeedCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(SPEED_COMMAND_ID)
