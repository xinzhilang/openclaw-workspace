# OpenClaw Browser Relay 插件配置指南

## 🚀 快速配置

您的插件需要以下配置信息才能连接到 OpenClaw 服务：

### 📋 配置信息

| 项目 | 值 |
|------|-----|
| **Relay 服务地址** | `ws://localhost:18792` |
| **Gateway 地址** | `ws://localhost:18789` |
| **Gateway Token** | `7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a` |
| **自动连接** | ✅ 启用 |
| **重试次数** | 3 次 |

---

## 🔧 手动配置步骤

### 步骤 1: 打开插件设置

1. 在 Chrome 浏览器中点击右上角的 **OpenClaw 图标** 🧩
2. 选择 **"选项"** 或 **"设置"**
3. 或者访问: `chrome://extensions` → 找到 OpenClaw 扩展 → 点击 **"详情"**

### 步骤 2: 填写连接信息

在配置页面中填写以下信息：

#### 🌐 Relay 设置

```
Relay Server URL: ws://localhost:18792
Gateway URL:      ws://localhost:18789
Gateway Token:    7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a
```

#### ⚙️ 高级选项

```
自动连接:          [✅] 启用
重试次数:          3
重试延迟:          1000ms
启用日志:          [ ] 禁用 (推荐)
```

### 步骤 3: 保存配置

点击 **"保存"** 或 **"应用"** 按钮

### 步骤 4: 验证连接

1. 插件图标应变为 **绿色** ✅
2. 鼠标悬停显示: **"已连接"**
3. 打开任意网页，右键菜单应出现 **"OpenClaw 操作"**

---

## 🔍 验证连接状态

### 方法 1: 检查图标颜色

- 🟢 **绿色**: 已连接 (正常)
- 🟡 **黄色**: 连接中
- 🔴 **红色**: 连接失败

### 方法 2: 查看状态信息

点击插件图标，应显示:
```
状态: 已连接
Relay: ws://localhost:18792 ✅
Gateway: ws://localhost:18789 ✅
```

### 方法 3: 命令行验证

```bash
# 检查 Relay 服务
python3 -c "import socket; s=socket.socket(); r=s.connect_ex(('127.0.0.1',18792)); print('Relay:', 'OK' if r==0 else 'FAIL'); s.close()"

# 检查 Gateway 服务
python3 -c "import socket; s=socket.socket(); r=s.connect_ex(('127.0.0.1',18789)); print('Gateway:', 'OK' if r==0 else 'FAIL'); s.close()"
```

**预期输出:**
```
Relay: OK
Gateway: OK
```

---

## 🛠️ 故障排除

### ❌ 问题: 插件显示"未连接"

**可能原因:**
1. Relay 服务未运行
2. 端口被占用
3. 防火墙阻止

**解决方案:**

```bash
# 1. 检查 Relay 服务状态
python3 -c "import socket; s=socket.socket(); print('Relay OK' if s.connect_ex(('127.0.0.1',18792))==0 else 'Relay Need Start'); s.close()"

# 2. 如果未运行，重新启动
python3 relay-daemon.py &

# 3. 检查端口
netstat -ano | findstr :18792
```

---

### ❌ 问题: 认证失败

**错误信息:** `Gateway token rejected`

**解决方案:**

```bash
# 检查 Token 是否正确
grep "token" ~/.openclaw/openclaw.json

# 如果需要，重新生成 Token
openclaw gateway stop
rm -rf ~/.openclaw/identity/ ~/.openclaw/devices/
openclaw gateway start

# 更新插件配置中的 Token
```

---

### ❌ 问题: 连接后断开

**可能原因:**
1. 网络不稳定
2. 服务崩溃
3. Token 过期

**解决方案:**

```bash
# 1. 检查服务状态
openclaw gateway status

# 2. 重启服务
openclaw gateway restart
python3 relay-daemon.py &

# 3. 重新连接插件
# 点击插件图标 → 断开 → 重新连接
```

---

## ✅ 配置完成检查清单

- [ ] Relay 服务在端口 18792 运行
- [ ] Gateway 服务在端口 18789 运行
- [ ] Chrome 插件已安装
- [ ] 插件配置正确:
  - [ ] Relay URL: `ws://localhost:18792`
  - [ ] Gateway URL: `ws://localhost:18789`
  - [ ] Gateway Token 正确
- [ ] 插件连接状态显示"已连接"
- [ ] 测试功能正常工作

---

## 🎯 使用示例

### 示例 1: 基础使用

```javascript
// 在 Chrome DevTools Console 中测试
fetch('http://localhost:18792/status')
  .then(r => r.json())
  .then(d => console.log('Relay Status:', d));
```

### 示例 2: 控制页面

```javascript
// 通过插件控制当前页面
// 1. 打开任意网页
// 2. 点击 OpenClaw 图标
// 3. 选择操作:
//    - 截取屏幕
//    - 查找元素
//    - 填写表单
```

### 示例 3: 与 agent-browser 配合

```bash
# 使用 agent-browser 控制
agent-browser --auto-connect get title

# 插件会自动同步状态
# 可以在页面中看到操作反馈
```

---

## 📄 配置文件

### JSON 配置格式

```json
{
  "relay": {
    "enabled": true,
    "relayServerUrl": "ws://localhost:18792",
    "gatewayUrl": "ws://localhost:18789",
    "gatewayToken": "7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a",
    "autoConnect": true,
    "reconnectAttempts": 3,
    "reconnectDelay": 1000
  },
  "features": {
    "highlightElements": true,
    "autoScreenshot": false
  }
}
```

---

## 🆘 获取帮助

### 官方文档
- 主文档: https://docs.openclaw.ai/
- 插件文档: https://docs.openclaw.ai/extensions/

### 常见问题
- FAQ: https://docs.openclaw.ai/faq/
- 故障排除: https://docs.openclaw.ai/troubleshooting/

### 社区支持
- Discord: https://discord.com/invite/clawd
- GitHub Issues: https://github.com/OpenClaw/issues

---

## ✨ 配置完成!

您的 OpenClaw Browser Relay 插件已配置完成！

**现在您可以:**
- ✅ 控制浏览器标签页
- ✅ 截取屏幕截图
- ✅ 填写表单
- ✅ 点击页面元素
- ✅ 执行自动化任务

**所有操作都通过浏览器插件完成！** 🎉
