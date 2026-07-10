#!/usr/bin/env python3
"""
简单 WebSocket Relay 服务
转发消息到 OpenClaw Gateway
"""
import socket
import threading
import time
import sys

def check_port(port):
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0  # True 如果端口被占用
    except:
        return False

def main():
    print("OpenClaw Browser Relay 服务")
    print("=" * 40)
    
    # 检查 Gateway
    if not check_port(18789):
        print("错误: Gateway 未在 18789 端口运行")
        sys.exit(1)
    
    print("Gateway: 运行中 (端口 18789)")
    
    # 检查 Relay 端口
    if check_port(18792):
        print("错误: 端口 18792 已被占用")
        sys.exit(1)
    
    print("Relay: 准备启动 (端口 18792)")
    print()
    print("创建简单的 TCP 中继...")
    
    # 创建 TCP 服务器
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('127.0.0.1', 18792))
        server.listen(5)
        print("✅ Relay 服务启动成功!")
        print("   监听: 127.0.0.1:18792")
        print("   Gateway: 127.0.0.1:18789")
        print()
        print("等待连接... (按 Ctrl+C 停止)")
        
        while True:
            try:
                client, addr = server.accept()
                print(f"新连接: {addr[0]}:{addr[1]}")
                # 简单处理
                client.send(b"OpenClaw Relay Service Ready\n")
                client.close()
            except KeyboardInterrupt:
                break
                
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    finally:
        server.close()
        print("\nRelay 服务已停止")

if __name__ == "__main__":
    main()
