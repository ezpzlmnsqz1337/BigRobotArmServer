#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

BEGIN_COMMAND_ID = 9


class BeginCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(BEGIN_COMMAND_ID)
