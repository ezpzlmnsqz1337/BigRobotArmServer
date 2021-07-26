#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

GRIPPER_COMMAND_ID = 6


class GripperCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(GRIPPER_COMMAND_ID)

  def parseResponse(self, response):
    return
