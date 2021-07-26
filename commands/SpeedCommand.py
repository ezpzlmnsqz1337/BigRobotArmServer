#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

SPEED_COMMAND_ID = 4


class SpeedCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(SPEED_COMMAND_ID)

  def parseCommandData(self, stream, command):
    self.parseJointData(stream, command)

  def parseResponse(self, response):
    return
