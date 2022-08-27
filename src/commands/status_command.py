#!/usr/bin/env python3
from abstract_command import AbstractCommand

STATUS_COMMAND_ID = 8


class StatusCommand(AbstractCommand):
  def __init__(self):
    super().__init__(STATUS_COMMAND_ID)
