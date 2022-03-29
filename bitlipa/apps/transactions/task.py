import asyncio

loop = asyncio.get_event_loop()

def callback():
    print("code here")
    loop.call_later(1, callback)

loop.call_later(1, callback)

async def main():
    while True:
        await asyncio.sleep(1)

loop.run_until_complete(main())