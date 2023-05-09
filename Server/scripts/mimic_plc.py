import asyncio


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", 9999
    )
    while True:
        data = await reader.read(100)
        print(f"Received: {data.decode()!r}")
        
        writer.write(b"pretend response from PLC: " + data + b"\n")
        await writer.drain()
        print(f"wrote data")


if __name__ == "__main__":
    asyncio.run(tcp_echo_client())
