"""
buzzer_diag.py — 蜂鸣器终极诊断
复制整个文件到 Thonny，点击运行
它会告诉你：
  ① 模块是 HIGH触发 还是 LOW触发
  ② 哪个 GPIO 能用
  ③ 最终结论

接线要求：
  蜂鸣器 VCC → 面包板 5V 轨 (重要：不要接3.3V)
  蜂鸣器 GND → 面包板 GND
  蜂鸣器 SIG → 先悬空，脚本会逐个 GPIO 测试
"""
from machine import Pin
import time

print("=" * 50)
print("  蜂鸣器终极诊断 v1.0")
print("=" * 50)

# ===== 第一步：裸测触发极性 =====
print("\n【第一步】裸测触发极性")
print("请把蜂鸣器 SIG 线从所有 GPIO 上拔掉，保持悬空")
input("  准备好后按 Enter > ")

print("  ⏳ 悬空测试（3秒）—— 应静音...")
time.sleep(3)

print("  🔌 把 SIG 线插到面包板 GND（蓝色轨），等3秒")
input("    插好后按 Enter > ")
time.sleep(3)
print("  → 悬空不响、接GND响 = LOW触发")
print("  → 悬空不响、接GND也不响 = ??（可能是 HIGH触发 或模块坏了）")

print("\n  🔌 把 SIG 线插到面包板 3.3V 轨，等3秒")
input("    插好后按 Enter > ")
time.sleep(3)
print("  → 接3.3V响 = HIGH触发 ✓")
print("  → 接3.3V不响 = ?? 可能是模块坏了")

# ===== 第二步：多引脚测试 =====
print("\n\n【第二步】扫描多个 GPIO")
print("确保蜂鸣器 SIG 已经回到 GPIO 上，脚本会逐个测试")

# 候选 GPIO：排除正在使用的
# 已用: 19(pump), 21/22(I2C), 26/27(relay),
#       34(flow), 35/5(HX710B), 36(air),
#       32/33(encoder)
# 空闲可测: 2, 4, 12, 13, 14, 15, 16, 17, 18, 23, 25
candidates = [18, 17, 16, 4, 25, 23, 14, 12, 13, 15, 2]

for pin in candidates:
    print(f"\n── GPIO{pin} ──")
    
    # 测试 HIGH 触发
    p = Pin(pin, Pin.OUT)
    
    p.value(1)  # HIGH
    print(f"  GPIO{pin}=HIGH ...", end=" ")
    time.sleep(0.8)
    
    p.value(0)  # LOW
    print(f"LOW", end=" ")
    time.sleep(0.5)
    
    # 测试 PWM (低频，绕过晶体管问题)
    from machine import PWM
    pp = PWM(Pin(pin, Pin.OUT), freq=2000, duty=512)
    print(f"| PWM 2kHz", end=" ")
    time.sleep(0.5)
    pp.deinit()
    
    print("✓")

print("\n\n⭐ 诊断结论：")
print("  第一步的结果决定触发极性")
print("  第二步看哪个 GPIO 能驱动")
print("  把能响的 GPIO+极性告诉我")
