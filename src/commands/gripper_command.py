#!/usr/bin/env python3
from bitstring import pack
from .abstract_command import AbstractCommand

GRIPPER_COMMAND_ID = 6


class GripperCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(
        GRIPPER_COMMAND_ID, ['uint:8', 'uint:8'])
