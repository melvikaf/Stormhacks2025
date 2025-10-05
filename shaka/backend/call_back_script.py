#used for connecting web sockets call backs in the touch designer app
def onConnect(websocketDAT, connection):
    debug(' Connected to Python backend')
    return

def onReceiveText(websocketDAT, connection, data):
    import json
    try:
        msg = json.loads(data)
    except Exception as e:
        debug(" JSON decode error:", e)
        return

    msg_type = msg.get("type")

    if msg_type == "gesture":
        op('text1').text = f"Gesture: {msg['name']} ({msg['conf']:.2f})"
    elif msg_type == "action":
        op('text1').text = f"Action: {msg['name']}"
    elif msg_type == "state":
        op('text1').text = f"State: {msg}"
    return

def onDisconnect(websocketDAT, connection):
    debug('Disconnected from backend')
    return
