#!/usr/bin/env python

import asyncio
import websockets
import json

async def producer():
    await asyncio.sleep(0.1)
    return input(">>> ")


async def producer_handler(websocket):
    while True:
        message = await producer()

        with open("s.json", "r") as f:
            message = f.read()

        await websocket.send(message)


async def handler(websocket):
    await asyncio.gather(
        producer_handler(websocket),
    )


async def hi():
    uri = "ws://localhost:8080/sock"
    async with websockets.connect(uri) as websocket:
        try:
            await handler(websocket)
        except KeyboardInterrupt:
            print("Closing...")


if __name__ == "__main__":
    asyncio.run(hi())
