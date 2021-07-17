def parseCommand(command):
  if 'BEGIN I' in command:
    return parseBeginCommand(command)
  return parseEndCommand(command)

def parseBeginCommand(command):
  return

def parseEndCommand(command):
  return

def parseResponse(response):
  return