"""
buzzer_fix.py — 蜂鸣器诊断 + 一次性修复

怎么用：
1. 确保蜂鸣器 VCC→5V, GND→GND, SIG→GPIO18（当前接线）
2. 把这个文件传到 ESP32 上运行
3. 根据输出告诉我结果
"""
from machine import Pin, PWM
import time

# ========== 第1步：硬件自检 ==========
print("=" * 50)
print("  蜂鸣器诊断 v1.0")
print("  当前接线: SIG → GPIO18")
print("=" * 50)

print("\n▶ 第1关：GPIO18 直接测试")

# 先确保引脚是干净的
_p = Pin(18, Pin.OUT)

for label, val in [("LOW (0V)   ", 0), ("HIGH (3.3V)", 1)]:
    _p.value(val)
    print(f"  GPIO18={label} → ", end="")
    time.sleep(1.5)
    print()
_p.value(0)

print("  (响了就告诉我哪次响)")

# ========== 第2步：PWM 测试（绕过晶体管驱动问题）==========
print("\n▶ 第2关：GPIO18 PWM 频率扫描")
for freq in [500, 1000, 2000, 3000, 5000]:
    pp = PWM(Pin(18, Pin.OUT), freq=freq, duty=512)
    print(f"  {freq}Hz 50% → ", end="")
    time.sleep(0.8)
    print()
    pp.deinit()
Pin(18, Pin.OUT).value(0)

# ========== 第3步：换引脚试 ==========
print("\n▶ 第3关：换引脚测试（HIGH触发）")
other_pins = [17, 16, 4, 25]

for pn in other_pins:
    pp = Pin(pn, Pin.OUT)
    pp.value(1)  # HIGH
    print(f"  GPIO{pn}=HIGH → ", end="")
    time.sleep(1)
    print()
    pp.value(0)
    time.sleep(0.3)

# ========== 第4步：反极性测试 ==========
print("\n▶ 第4关：GPIO18 LOW触发测试（反极性）")
for label, val in [("LOW (0V)   ", 0), ("HIGH (3.3V)", 1)]:
    for _ in range(3):
        Pin(18, Pin.OUT).value(1 - val)  # 静音
        time.sleep_ms(50)
        Pin(18, Pin.OUT).value(val)      # 发声
        time.sleep_ms(200)
    print(f"  GPIO18={label} ×3 → 响了吗？")

Pin(18, Pin.OUT).value(1)  # 确保关闭（假设HIGH触发时关）
time.sleep(1)
Pin(18, Pin.OUT).value(0)

print("\n" + "=" * 50)
print("  测试完毕！告诉我：")
print("  ① 第1关哪次响了？")
print("  ② 第2关PWM哪次有声音？")
print("  ③ 第3关哪个引脚响了？")
print("  ④ 第4关反极性测试响了吗？")
print("=" * 50)

# ========== 第5步：如果有回应说某个引脚+极性对了，自动修复 ==========
# 等用户反馈后再决定怎么修 core.py
