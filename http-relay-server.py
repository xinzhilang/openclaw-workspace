#!/usr/bin/env python3
"""
OpenClaw Browser Relay - HTTP 长轮询中继服务
替代 WebSocket，使用纯 HTTP 协议
支持 Chrome 插件连接和令牌验证
"""
import http.server
import socketserver
import json
import threading
import time
import urllib.parse
from datetime import datetime

# 配置
RELAY_PORT = 18792
VALID_TOKEN = "7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a"

# 消息队列（内存存储）
message_queues = {}
queue_lock = threading.Lock()

class RelayHandler(http.server.BaseHTTPRequestHandler):
    """处理所有 HTTP 请求"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == "/" or path == "/index.html":
            self.serve_homepage()
        elif path == "/status":
            self.serve_status()
        elif path == "/health":
            self.serve_health()
        elif path == "/ws":
            # WebSocket 握手模拟 - 返回升级信息
            self.serve_ws_info()
        elif path == "/poll":
            # 长轮询端点
            token = query.get('token', [''])[0]
            client_id = query.get('client_id', ['default'])[0]
            timeout = int(query.get('timeout', ['30'])[0])
            self.serve_poll(token, client_id, timeout)
        elif path == "/config":
            self.serve_config()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        token = query.get('token', [''])[0]
        if not token:
            try:
                data = json.loads(body) if body else {}
                token = data.get('token', '')
            except:
                pass
        
        if path == "/send":
            client_id = query.get('client_id', ['default'])[0]
            self.handle_send(token, client_id, body)
        elif path == "/register":
            self.handle_register(token, body)
        else:
            self.send_error(404, "Not Found")
    
    def serve_homepage(self):
        """服务主页"""
        html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Browser Relay</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .status {
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .status.online {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .status.offline {
            background: #ffebee;
            color: #c62828;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .endpoint {
            background: #fafafa;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #4CAF50;
        }
        .timestamp {
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenClaw Browser Relay</h1>
        
        <div class="status online">
            <strong>✅ 服务状态: 在线</strong>
        </div>
        
        <p>OpenClaw 浏览器中继服务正在运行，提供 HTTP 长轮询中继功能。</p>
        
        <div class="info">
            <h3>📋 配置信息</h3>
            <ul>
                <li><strong>中继端口:</strong> <code>18792</code></li>
                <li><strong>验证令牌:</strong> <code>7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a</code></li>
                <li><strong>服务地址:</strong> <code>http://127.0.0.1:18792/</code></li>
                <li><strong>WebSocket 兼容端点:</strong> <code>ws://127.0.0.1:18792/ws</code> (HTTP模拟)</li>
            </ul>
        </div>
        
        <h3>🔌 API 端点</h3>
        
        <div class="endpoint">
            <strong>GET /</strong> - 服务主页
        </div>
        
        <div class="endpoint">
            <strong>GET /status</strong> - 服务状态
        </div>
        
        <div class="endpoint">
            <strong>GET /health</strong> - 健康检查
        </div>
        
        <div class="endpoint">
            <strong>GET /config</strong> - 获取配置
            <br><small>返回中继配置信息</small>
        </div>
        
        <div class="endpoint">
            <strong>GET /poll?token=TOKEN&client_id=ID&timeout=30</strong> - 长轮询
            <br><small>等待新消息，最长等待 timeout 秒</small>
        </div>
        
        <div class="endpoint">
            <strong>POST /send?token=TOKEN&client_id=ID</strong> - 发送消息
            <br><small>Body: JSON 消息内容</small>
        </div>
        
        <div class="endpoint">
            <strong>POST /register?token=TOKEN</strong> - 注册客户端
            <br><small>Body: JSON {"client_id": "..."}</small>
        </div>
        
        <div class="timestamp">
            启动时间: <span id="uptime">--</span>
        </div>
    </div>
    
    <script>
        // 自动轮询状态
        function updateUptime() {
            document.getElementById('uptime').textContent = new Date().toLocaleString();
        }
        setInterval(updateUptime, 1000);
        updateUptime();
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_status(self):
        """服务状态"""
        status = {
            'status': 'online',
            'service': 'OpenClaw Browser Relay',
            'version': '1.0',
            'port': RELAY_PORT,
            'protocol': 'HTTP Long Polling',
            'clients': len(message_queues),
            'timestamp': datetime.now().isoformat()
        }
        self.send_json(status)
    
    def serve_health(self):
        """健康检查"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def serve_ws_info(self):
        """WebSocket 信息端点"""
        info = {
            'type': 'relay_info',
            'relay': 'OpenClaw Browser Relay',
            'supports_websocket': False,
            'protocol': 'HTTP Long Polling',
            'description': 'This relay uses HTTP long polling instead of WebSocket',
            'endpoints': {
                'poll': '/poll',
                'send': '/send',
                'register': '/register'
            }
        }
        self.send_json(info)
    
    def serve_config(self):
        """获取配置"""
        config = {
            'relay_port': RELAY_PORT,
            'token_required': True,
            'protocol': 'HTTP',
            'supports_cors': True,
            'endpoints': {
                'poll': '/poll',
                'send': '/send',
                'health': '/health',
                'status': '/status'
            }
        }
        self.send_json(config)
    
    def serve_poll(self, token, client_id, timeout):
        """长轮询端点"""
        # 验证令牌
        if not self.validate_token(token):
            self.send_error_json(401, 'Invalid token')
            return
        
        # 检查超时
        try:
            timeout = min(int(timeout), 60)  # 最大60秒
        except:
            timeout = 30
        
        # 等待消息
        start_time = time.time()
        while time.time() - start_time < timeout:
            with queue_lock:
                if client_id in message_queues and message_queues[client_id]:
                    message = message_queues[client_id].pop(0)
                    self.send_json({
                        'type': 'message',
                        'data': message,
                        'timestamp': datetime.now().isoformat()
                    })
                    return
            time.sleep(0.5)  # 短暂等待
        
        # 超时 - 返回空消息
        self.send_json({
            'type': 'timeout',
            'message': 'No messages available',
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_send(self, token, client_id, body):
        """处理发送消息"""
        if not self.validate_token(token):
            self.send_error_json(401, 'Invalid token')
            return
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {'raw': body}
        
        # 添加到目标客户端队列
        target_client = data.get('target', client_id)
        with queue_lock:
            if target_client not in message_queues:
                message_queues[target_client] = []
            message_queues[target_client].append(data)
        
        self.send_json({
            'status': 'sent',
            'target': target_client,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_register(self, token, body):
        """处理客户端注册"""
        if not self.validate_token(token):
            self.send_error_json(401, 'Invalid token')
            return
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        client_id = data.get('client_id', 'unknown')
        
        with queue_lock:
            if client_id not in message_queues:
                message_queues[client_id] = []
        
        # 添加欢迎消息
        welcome_msg = {
            'type': 'welcome',
            'message': 'Connected to OpenClaw Browser Relay',
            'client_id': client_id,
            'protocol': 'HTTP Long Polling',
            'timestamp': datetime.now().isoformat()
        }
        message_queues[client_id].append(welcome_msg)
        
        self.send_json({
            'status': 'registered',
            'client_id': client_id,
            'poll_endpoint': f'/poll?token={token}&client_id={client_id}',
            'timestamp': datetime.now().isoformat()
        })
    
    def validate_token(self, token):
        """验证令牌"""
        return token == VALID_TOKEN
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def send_error_json(self, code, message):
        """发送错误 JSON 响应"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{timestamp}] {format % args}')

def main():
    PORT = RELAY_PORT
    
    # 设置服务器
    handler = RelayHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f'{"=" * 60}')
        print(f'  OpenClaw Browser Relay - HTTP 长轮询服务')
        print(f'{"=" * 60}')
        print(f'  端口: {PORT}')
        print(f'  协议: HTTP (长轮询)')
        print(f'  令牌: {VALID_TOKEN[:16]}...')
        print(f'  URL: http://127.0.0.1:{PORT}/')
        print(f'{"=" * 60}')
        print(f'  服务已启动! 按 Ctrl+C 停止')
        print(f'{"=" * 60}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f'\n服务已停止')

if __name__ == '__main__':
    main()
