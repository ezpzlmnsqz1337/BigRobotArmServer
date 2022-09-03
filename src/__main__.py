from simple_websocket_server import WebSocketServer, WebSocket
import usb_robot_arm
from command_builder import CommandBuilder


class SimpleEcho(WebSocket):
  def handle(self):
    cb = CommandBuilder()
    message = self.data.rstrip("\r").rstrip("\n")
    print(message)

    if message == "connect" and not usb_robot_arm.is_connected():
      usb_robot_arm.connect()
      self.send_message(getConnectionStatus())
    elif message == "connect" and usb_robot_arm.is_connected():
      self.send_message(getConnectionStatus())
    elif usb_robot_arm.is_connected():
      if message == "disconnect":
        usb_robot_arm.disconnect()
        self.send_message(getConnectionStatus())
      else:
        serial_command = cb.parse_web_message(message)
        serial_response = usb_robot_arm.send_serial_command(serial_command)
        self.send_message(cb.parse_serial_response(serial_response))

  def connected(self):
    print(self.address, "connected")
    self.send_message(getConnectionStatus())

  def handle_close(self):
    print(self.address, "closed")


def getConnectionStatus():
  status = 1 if usb_robot_arm.is_connected() else 0
  return f"connectionStatus:{status}"


server = WebSocketServer("", 1337, SimpleEcho)
server.serve_forever()
