#testing client for run_time.py
import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8765"
    
    try:
        print("Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            print(" Connected! Waiting for messages...")
            print("Make some gestures in front of your camera!\n")
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "gesture":
                        print(f"🎭 GESTURE: {data['name']} (confidence: {data['conf']:.2f})")
                    
                    elif data.get("type") == "action":
                        print(f"🎵 ACTION: {data['name']}")
                        if 'value' in data:
                            print(f"   Value: {data['value']}")
                    
                    elif data.get("type") == "state":
                        print(f" STATE: xfader={data['xfader']:.1f}, reverb={data['reverb']}, lowpass={data['lowpass']}")
                    
                    else:
                        print(f" MESSAGE: {data}")
                    
                    print()  # Empty line for readability
                    
                except websockets.exceptions.ConnectionClosed:
                    print(" Connection closed by server")
                    break
                except Exception as e:
                    print(f" Error: {e}")
                    break
                    
    except ConnectionRefused:
        print(" Could not connect to WebSocket server")
        print("Make sure run_time.py is running first!")
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    print(" AirDJ Test Client")
    print("===================")
    asyncio.run(test_client())
