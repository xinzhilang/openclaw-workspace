"""最简蜂鸣器测试"""
from machine import Pin
import time

p = Pin(18, Pin.OUT, value=0)  # 拉低 = 停
print("GPIO18 = LOW（应停止）")
time.sleep(3)

print("GPIO18 = HIGH（应响起）")
p.value(1)
time.sleep(2)

print("GPIO18 = LOW（应停止）")
p.value(0)
time.sleep(3)

print("测试完毕")
