import socket
import sys

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0  # 返回 True 如果端口被占用
    except:
        return False

print("OpenClaw Browser Relay 状态检查")
print("=" * 40)

# 检查 Gateway
if check_port(18789):
    print("[OK] Gateway 端口 18789 正在运行")
else:
    print("[FAIL] Gateway 端口 18789 未运行")

# 检查 Relay
if check_port(18792):
    print("[OK] Relay 端口 18792 正在监听")
else:
    print("[FAIL] Relay 端口 18792 未监听")
    print("\n注意: Relay 服务需要手动启动")
    print("使用 'agent-browser stream' 或独立 Relay 服务")

# 检查 CDP
if check_port(9222):
    print("[OK] CDP 端口 9222 正在监听")
else:
    print("[WARN] CDP 端口 9222 未监听")

print("\n配置端口:")
print("  Gateway: 18789")
print("  Relay: 18792")
print("  CDP: 9222")