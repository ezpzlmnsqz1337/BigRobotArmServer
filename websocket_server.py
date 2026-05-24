from simple_websocket_server import WebSocketServer, WebSocket
import usb_robot_arm

class SimpleEcho(WebSocket):
    def handle(self):
        message = self.data.rstrip('\r').rstrip('\n')
        print(message)

        try:
            if usb_robot_arm.isConnected():
                if message == 'disconnect':
                    usb_robot_arm.disconnect()
                    self.send_message(getConnectionStatus())
                else:
                    response = usb_robot_arm.sendCommand(message)
                    self.send_message(response)
            else:
                if message == 'connect':
                    usb_robot_arm.connect()
                    self.send_message(getConnectionStatus())
        except usb_robot_arm.ConnectionLostError as error:
            self.send_message(f'{getConnectionStatus()}\nERROR: {error}')

    def connected(self):
        print(self.address, 'connected')
        self.send_message(getConnectionStatus())

    def handle_close(self):
        print(self.address, 'closed')

def getConnectionStatus():
    status = 1 if usb_robot_arm.isConnected() else 0
    return f'connectionStatus:{status}'

server = WebSocketServer('', 1337, SimpleEcho)
server.serve_forever()