from simple_websocket_server import WebSocketServer, WebSocket
import usb_robot_arm
from command_builder import CommandBuilder


class SimpleEcho(WebSocket):
  def handle(self):
    cb = CommandBuilder()
    message = self.data.rstrip('\r').rstrip('\n')
    print(message)

    if usb_robot_arm.is_connected():
      if message == 'disconnect':
        usb_robot_arm.disconnect()
        self.send_message(getConnectionStatus())
      else:
        response = usb_robot_arm.send_command(cb.parse_command(message))
        self.send_message(cb.parse_response(response))
    else:
      if message == 'connect':
        usb_robot_arm.connect()
        self.send_message(getConnectionStatus())

  def connected(self):
    print(self.address, 'connected')
    self.send_message(getConnectionStatus())

  def handle_close(self):
    print(self.address, 'closed')


def getConnectionStatus():
  status = 1 if usb_robot_arm.is_connected() else 0
  return f'connectionStatus:{status}'


server = WebSocketServer('', 1337, SimpleEcho)
server.serve_forever()
