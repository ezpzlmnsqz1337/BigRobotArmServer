from simple_websocket_server import WebSocketServer, WebSocket
import usbRobotArm
import commandBuilder

class SimpleEcho(WebSocket):
    def handle(self):
        message = self.data.rstrip('\r').rstrip('\n')
        print(message)

        if usbRobotArm.isConnected():
            if message == 'disconnect':
                usbRobotArm.disconnect()
                self.send_message(getConnectionStatus())
            else:
                response = usbRobotArm.sendCommand(commandBuilder.getCommand(message))
                self.send_message(commandBuilder.parseResponse(response))
        else:
            if message == 'connect':
                usbRobotArm.connect()
                self.send_message(getConnectionStatus())

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