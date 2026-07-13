#!/usr/bin/env python3
"""
OpenClaw Browser Relay - WebSocket 服务
支持 WebSocket 协议，用于浏览器扩展连接
"""
import asyncio
import websockets
import logging
import json

# 配置
RELAY_PORT = 18792
GATEWAY_URL = "ws://127.0.0.1:18789"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OpenClaw-Relay')

# 连接的客户端
clients = set()

async def gateway_relay(websocket, path):
    """处理来自 Chrome 扩展的连接"""
    # 注册客户端
    clients.add(websocket)
    client_addr = websocket.remote_address
    logger.info(f'客户端连接: {client_addr}')
    
    try:
        # 发送欢迎消息
        welcome = {
            'type': 'welcome',
            'message': 'OpenClaw Relay Service',
            'version': '1.0.0',
            'gateway': GATEWAY_URL
        }
        await websocket.send(json.dumps(welcome))
        
        # 保持连接，转发消息
        async for message in websocket:
            logger.info(f'收到消息: {message[:50]}...')
            
            try:
                # 转发到 Gateway
                async with websockets.connect(GATEWAY_URL) as gateway_ws:
                    await gateway_ws.send(message)
                    response = await gateway_ws.recv()
                    await websocket.send(response)
            except Exception as e:
                logger.error(f'Gateway 错误: {e}')
                error_msg = json.dumps({'type': 'error', 'message': str(e)})
                await websocket.send(error_msg)
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f'客户端断开: {client_addr}')
    except Exception as e:
        logger.error(f'连接错误: {e}')
    finally:
        clients.discard(websocket)

async def main():
    logger.info(f'启动 OpenClaw Relay 服务 (端口 {RELAY_PORT})')
    logger.info(f'Gateway 地址: {GATEWAY_URL}')
    
    # 启动 WebSocket 服务器
    async with websockets.serve(gateway_relay, '0.0.0.0', RELAY_PORT):
        logger.info(f'Relay 服务已启动!')
        logger.info(f'WebSocket: ws://localhost:{RELAY_PORT}')
        logger.info('等待连接...')
        await asyncio.Future()  # 永久运行

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('服务已停止')
    except Exception as e:
        logger.error(f'启动失败: {e}')
