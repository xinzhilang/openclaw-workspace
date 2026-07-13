"""
boot.py — ESP32 全自动灌肠控制器
启动初始化：引脚安全状态 + 内存释放
"""
from machine import Pin
import time, gc

Pin(19, Pin.OUT, value=0)        # 蠕动泵
Pin(27, Pin.OUT, value=0)        # 充气泵继电器
Pin(26, Pin.OUT, value=0)        # 电磁阀
time.sleep_ms(20)

# 蜂鸣器：上电不做任何设置（保持默认高阻态=静音）
# core.py 中用 IN/OUT 切换控制

# 关闭 WiFi/BT 省内存（main.py 按需开启）
import esp
esp.osdebug(None)
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

# 蜂鸣器开机自检（IN/OUT 切换方案）
time.sleep_ms(150)
from machine import Pin as _P
for _ in range(2):
    _P(18, _P.OUT, value=0)  # OUT+LOW = 响
    time.sleep_ms(200)
    _P(18, _P.IN)            # 高阻 = 静音
    time.sleep_ms(100)

gc.collect()
print("✅ boot.py — 进入 main.py")
