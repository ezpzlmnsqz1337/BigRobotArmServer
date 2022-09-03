#!/usr/bin/env python3
from .abstract_command import AbstractCommand

BEGIN_COMMAND_ID = 9


class BeginCommand(AbstractCommand):
  def __init__(self):
    super().__init__(BEGIN_COMMAND_ID)
