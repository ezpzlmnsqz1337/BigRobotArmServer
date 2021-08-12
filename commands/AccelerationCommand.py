#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

ACCEL_COMMAND_ID = 5


class AccelerationCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(ACCEL_COMMAND_ID)
