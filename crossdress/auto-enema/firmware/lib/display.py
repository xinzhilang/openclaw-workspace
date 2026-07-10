"""
lib/display.py — LCD1602 显示封装
  依赖: lib/lcd1602.py
  提供各状态画面函数，webctrl.py 直接调用
"""
from machine import Pin, I2C
from lib.lcd1602 import LCD1602
import time

# ==================== 全局 LCD 实例 ====================
_Z = None  # LCD1602 instance, lazy init
_I2C_EXT = None  # 外部共享 I2C 总线

def set_i2c(i2c):
    """使用 core.py 创建的共享 I2C 总线，避免重复初始化"""
    global _I2C_EXT
    _I2C_EXT = i2c

def _get():
    global _Z
    if _Z is None:
        if _I2C_EXT:
            i2c = _I2C_EXT
        else:
            i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        _Z = LCD1602(i2c, 0x27)
    return _Z


# ==================== 初始化画面 ====================
def splash():
    """开机欢迎画面"""
    l = _get()
    l.print("  Enema Ctrl")
    l.set_cursor(0, 1)
    l.print("  Init...  ")
    time.sleep(1)
    l.clear()


def show_ip(ip):
    """WiFi 连接后显示 IP 地址"""
    l = _get()
    # IP 最长 15 字符，LCD 每行 16
    s = ip if len(ip) <= 15 else ip[:15]
    l.print_at(0, 0, s + " " * (15 - len(s)))
    l.print_at(0, 1, "Ready       ")


# ==================== 状态画面 ====================
def idle(air_kpa, water_kpa, vol_ml):
    """空闲状态显示传感器读数"""
    l = _get()
    l.print_at(0, 0, f"A:{air_kpa:4.1f} W:{water_kpa:4.1f}")
    l.print_at(0, 1, f"Ready {vol_ml:4.0f}ml   ")


def inflating(p_kpa, target_kpa):
    """充气中"""
    l = _get()
    l.print_at(0, 0, "Inflate")
    l.print_at(0, 1, f"{p_kpa:.0f}/{target_kpa}kPa")


def filling(vol_now, vol_target, water_kpa):
    """注水中"""
    l = _get()
    l.print_at(0, 0, f"Fill {vol_now:.0f}/{vol_target}")
    l.print_at(0, 1, f"W:{water_kpa:.0f}kPa")


def holding(remain_s, air_kpa, water_kpa):
    """保持阶段"""
    l = _get()
    l.print_at(0, 0, f"Hold {remain_s:3d}s")
    l.print_at(0, 1, f"A:{air_kpa:.0f} W:{water_kpa:.0f}")


def timed_pump(remain_s):
    """定时注水"""
    l = _get()
    l.print_at(0, 0, "Timed Pump")
    l.print_at(0, 1, f"{remain_s:3d}s remain")


def message(msg):
    """通用消息显示，超出 16 字滚到第二行"""
    l = _get()
    l.print_at(0, 0, f"{msg[:16]:<16}")
    l.print_at(0, 1, f"{msg[16:32]:<16}")
