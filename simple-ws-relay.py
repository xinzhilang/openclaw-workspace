#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('Relay')

RELAY_PORT = 18792
GATEWAY_URL = 'ws://127.0.0.1:18789'

async def handler(websocket, path):
    addr = websocket.remote_address
    logger.info(f'[CONNECT] Client: {addr[0]}:{addr[1]}')
    
    # Send welcome
    await websocket.send(json.dumps({
        'type': 'welcome',
        'message': 'OpenClaw Relay Service Running'
    }))
    logger.info('[READY] WebSocket connection established')
    
    try:
        async for message in websocket:
            logger.info(f'[RECV] {message[:50]}')
            
            # Forward to gateway
            try:
                async with websockets.connect(GATEWAY_URL) as gw:
                    await gw.send(message)
                    response = await gw.recv()
                    await websocket.send(response)
                    logger.info(f'[SENT] Response forwarded')
            except Exception as e:
                logger.error(f'[ERROR] Gateway: {e}')
                await websocket.send(json.dumps({'error': str(e)}))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info('[DISCONNECT] Client closed connection')
    except Exception as e:
        logger.error(f'[ERROR] {e}')
    finally:
        logger.info(f'[CLOSED] Connection ended')

async def main():
    logger.info(f'Starting OpenClaw Relay on port {RELAY_PORT}')
    logger.info(f'Gateway: {GATEWAY_URL}')
    
    async with websockets.serve(handler, '0.0.0.0', RELAY_PORT):
        logger.info(f'✅ Relay ready: ws://localhost:{RELAY_PORT}')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
