"""
test_buzzer.py — 蜂鸣器独立测试
上传到 ESP32 运行，测试各引脚和触发极性
"""
from machine import Pin
import time

def test_pin(pin_num, active_low=True):
    """测试单个引脚"""
    label = "LOW=响" if active_low else "HIGH=响"
    on = 0 if active_low else 1
    off = 1 if active_low else 0

    print(f"\n═ 测试 GPIO{pin_num} ({label}) ═")
    p = Pin(pin_num, Pin.OUT, value=off)

    for i in range(3):
        p.value(on)
        time.sleep_ms(300)
        p.value(off)
        time.sleep_ms(200)
        print(f"  第{i+1}声 → ", end="")
    print("完毕")


print("=" * 40)
print("  蜂鸣器测试 — 听哪声响")
print("=" * 40)
print()
print("先试 GPIO18（低电平触发, 3声各300ms）")
test_pin(18, active_low=True)

print()
print("再试 GPIO18（高电平触发, 3声各300ms）")
test_pin(18, active_low=False)

print()
print("如果以上都不响, 试试其他引脚:")
for pin in [12, 13, 14, 15, 16, 17, 4, 5]:
    print(f"  GPIO{pin} (LOW触发, 2声)")
    test_pin(pin, active_low=True)
    time.sleep_ms(500)

print()
print("=" * 40)
print("  测试完成！")
print("  哪次响了就记住引脚号和触发极性")
print("=" * 40)
