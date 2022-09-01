#!/usr/bin/env python3
from .abstract_command import AbstractCommand

ACCEL_COMMAND_ID = 5


class AccelerationCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(ACCEL_COMMAND_ID)
