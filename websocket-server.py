from simple_websocket_server import WebSocketServer, WebSocket
import usbRobotArm

class SimpleEcho(WebSocket):
    def handle(self):
        message = self.data.rstrip('\r').rstrip('\n')
        print(message)

        try:
            if usbRobotArm.isConnected():
                if message == 'disconnect':
                    usbRobotArm.disconnect()
                    self.send_message(getConnectionStatus())
                else:
                    response = usbRobotArm.sendCommand(message)
                    self.send_message(response)
            else:
                if message == 'connect':
                    usbRobotArm.connect()
                    self.send_message(getConnectionStatus())
        except usbRobotArm.ConnectionLostError as error:
            self.send_message(f'{getConnectionStatus()}\nERROR: {error}')

    def connected(self):
        print(self.address, 'connected')
        self.send_message(getConnectionStatus())

    def handle_close(self):
        print(self.address, 'closed')

def getConnectionStatus():
     status = 1 if usbRobotArm.isConnected() else 0
     return f'connectionStatus:{status}'

server = WebSocketServer('', 1337, SimpleEcho)
server.serve_forever()