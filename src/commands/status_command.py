#!/usr/bin/env python3
from bitstring import BitStream
from .abstract_command import AbstractCommand

STATUS_COMMAND_ID = 8


class StatusCommand(AbstractCommand):
  def __init__(self):
    super().__init__(STATUS_COMMAND_ID)

  def parse_response(self, response: bytes):
    data = response.splitlines()
    stream = BitStream(data[1])

    p_base = stream.read("intle:32")
    p_shoulder = stream.read("intle:32")
    p_elbow = stream.read("intle:32")
    p_wrist_rotate = stream.read("intle:32")
    p_wrist = stream.read("intle:32")
    result = f"BigRobotArm::POSITION: B{p_base} S{p_shoulder} E{p_elbow} WR{p_wrist_rotate} W{p_wrist}\n"

    a_base = stream.read("intle:32")
    a_shoulder = stream.read("intle:32")
    a_elbow = stream.read("intle:32")
    a_wrist_rotate = stream.read("intle:32")
    a_wrist = stream.read("intle:32")
    result += f"BigRobotArm::ACCELERATION: B{a_base} S{a_shoulder} E{a_elbow} WR{a_wrist_rotate} W{a_wrist}\n"

    s_base = stream.read("intle:32")
    s_shoulder = stream.read("intle:32")
    s_elbow = stream.read("intle:32")
    s_wrist_rotate = stream.read("intle:32")
    s_wrist = stream.read("intle:32")
    result += f"BigRobotArm::SPEED: B{s_base} S{s_shoulder} E{s_elbow} WR{s_wrist_rotate} W{s_wrist}\n"

    g_enabled = stream.read("uint:8")
    g_position = stream.read("uint:8")
    sync_enabled = stream.read("uint:8")

    result += f"BigRobotArm::GRIPPER: E{g_enabled} P{g_position}\n"
    result += f"BigRobotArm::SYNC-MOTORS: {sync_enabled}\n"

    result += super().parse_response(response)
    return result
