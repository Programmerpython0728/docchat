"""WebSocket test client"""
import asyncio
import json
import sys

import websockets


async def test(token: str, port: int = 8005):
    uri = f"ws://localhost:{port}/api/v1/chat/ws?token={token}"
    print(f"Connecting to {uri[:60]}...")

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "message", "content": "Salom DocChat"}))
        print("\n--- LLM stream ---")
        async for message in ws:
            data = json.loads(message)
            if data["type"] == "token":
                print(data["content"], end="", flush=True)
            elif data["type"] == "done":
                print("\n[TUGADI]")
                break


if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else "INVALID"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8005
    asyncio.run(test(token, port))
