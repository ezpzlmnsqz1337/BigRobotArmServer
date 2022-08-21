#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand
from bitstring import pack

GRIPPER_COMMAND_ID = 6


class GripperCommand(AbstractCommand):
  def __init__(self):
    super().__init__(GRIPPER_COMMAND_ID, ['uint:8', 'uint:8'])
