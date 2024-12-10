import asyncio
import websockets
import json

async def process_geometry(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print("Received data:", data)

        # Process the incoming data here (e.g., send to Houdini)

        # Respond back to the client
        response = {"status": "success", "message": "Data received and processed"}
        await websocket.send(json.dumps(response))

async def main():
    # Create the WebSocket server
    async with websockets.serve(process_geometry, "localhost", 8765):
        print("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())  # Explicitly start the asyncio event loop
