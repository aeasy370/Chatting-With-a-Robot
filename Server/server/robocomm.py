import logging
import asyncio


log = logging.getLogger("server.robocomm")


async def handle_plc_connection(inqueue, outqueue, reader, writer):
    peername = writer.get_extra_info("peername")
    log.debug(f"received conection from {peername}")
    
    while True:
        try:
            to_send = await inqueue.get()
            log.debug("got diagnostic, sending to PLC...")
            
            writer.write(to_send)
            await writer.drain()
            
            recvd = await reader.readline()
            log.debug(f"got PLC response: {recvd}")
            if recvd == b"":
                raise ConnectionError
            await outqueue.put(recvd)
        except ConnectionError:
            log.debug(f"connection from {peername} closed")
            await outqueue.put("PLC connection closed, please retry")
            break
