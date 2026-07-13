# 灌肠控制器 v4 — 刷机指南

## 文件清单 (10 个文件, ~47KB)

```
/ (ESP32 根目录)
├── boot.py       (619B)  开机自检 + 蜂鸣器测试音
├── main.py       (123B)  入口 → 启动 webctrl
├── webctrl.py    (13KB)  Web 服务器 + 控制面板
└── lib/
    ├── ads1115.py      — ADS1115 16-bit ADC 驱动 (I2C)
    ├── calibration.py  — 标定参数持久化 (保存到 flash)
    ├── core.py         — 状态机 + 传感器 + LCD + 安全保护
    ├── display.py      — LCD1602 画面管理
    ├── flowmeter.py    — YF-S401 流量计驱动
    ├── lcd1602.py      — LCD1602 底层驱动
    └── pressure.py     — 气压/水压传感器驱动
```

## 刷机方式

### 方式 A: Thonny (推荐)

1. **连接 ESP32** → USB 线插入电脑，确认 COM3
2. **Thonny 设置** → 运行 → 选择解释器 → MicroPython (ESP32) → 端口 COM3
3. **上传文件** (逐个)：
   - 右键 `boot.py` → 上传到 /
   - 右键 `main.py` → 上传到 /
   - 右键 `webctrl.py` → 上传到 /
   - 右键 `lib/` 文件夹 → 上传到 /lib/ (或逐个上传 lib/ 下的文件)
4. **按 ESP32 复位键** → 会自动启动
5. **等 LCD 显示 IP** → 浏览器打开 http://192.168.x.xx

### 方式 B: esptool.py (批量)

```bash
# 确保已装 esptool
pip install esptool

# 上传单个文件
ampy --port COM3 put boot.py /boot.py
ampy --port COM3 put main.py /main.py
ampy --port COM3 put webctrl.py /webctrl.py

# lib/ 目录
ampy --port COM3 mkdir /lib
ampy --port COM3 put lib/ads1115.py /lib/ads1115.py
ampy --port COM3 put lib/calibration.py /lib/calibration.py
ampy --port COM3 put lib/core.py /lib/core.py
ampy --port COM3 put lib/display.py /lib/display.py
ampy --port COM3 put lib/flowmeter.py /lib/flowmeter.py
ampy --port COM3 put lib/lcd1602.py /lib/lcd1602.py
ampy --port COM3 put lib/pressure.py /lib/pressure.py

# 复位
ampy --port COM3 reset
```

## 刷机后验证

| 检查项 | 预期现象 |
|--------|----------|
| 开机蜂鸣 | "嘀"一声 ~60ms |
| LCD 亮起 | 显示 "Enema Ctrl" → IP + "Ready" |
| Web 界面 | 浏览器打开 IP 看到控制面板 |
| 传感器读数 | 通大气时气压 ~0kPa, 水路 ~0kPa |
| 标定持久化 | 点"标定"→ 重启 → 读数不变 (无需重标) |

## WiFi 连接

- SSID: `Xiaomi_6807`
- 密码: `guochunxi`
- 如需修改 → 编辑 `webctrl.py` 中 `w.connect(...)` 参数
