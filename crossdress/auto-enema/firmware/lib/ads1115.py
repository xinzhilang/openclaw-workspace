"""
lib/ads1115.py — ADS1115 16-bit I2C ADC 驱动 (MicroPython)

接线:
  ADS1115 VDD → ESP32 3.3V (或 5V，取决于模块)
  ADS1115 GND → ESP32 GND
  ADS1115 SCL → ESP32 GPIO22 (与 LCD 共享 I2C 总线)
  ADS1115 SDA → ESP32 GPIO21 (与 LCD 共享 I2C 总线)
  ADS1115 ADDR → GND (默认 I2C 地址 0x48)

传感器输入 (XGZP6847A 模拟版):
  ADS1115 AIN0 ← XGZP6847A OUT
  (保留原有分压电路 — XGZP 输出 0.5-4.5V)

I2C 地址表:
  ADDR→GND:  0x48 (默认)
  ADDR→VDD:  0x49
  ADDR→SDA:  0x4A
  ADDR→SCL:  0x4B
"""
from machine import I2C, Pin
import time

_CFG_REG = 0x01
_CVT_REG = 0x00
_DFT_ADDR = 0x48

# ==================== PGA 配置 ====================
# ±FS 满量程电压 (V), ADS1115 寄存器 bits 11-9
_PGA_CFG = {
    6.144: 0x0000,   # ±6.144V
    4.096: 0x0200,   # ±4.096V
    2.048: 0x0400,   # ±2.048V
    1.024: 0x0600,   # ±1.024V
    0.512: 0x0800,   # ±0.512V
    0.256: 0x0A00,   # ±0.256V
}

# ==================== 数据速率 ====================
_DR_CFG = {
    8:    0x0000,
    16:   0x0020,
    32:   0x0040,
    64:   0x0060,
    128:  0x0080,
    250:  0x00A0,
    475:  0x00C0,
    860:  0x00E0,
}

_MUX_CFG = {
    0: 0x4000,    # AIN0 vs GND
    1: 0x5000,    # AIN1 vs GND
    2: 0x6000,    # AIN2 vs GND
    3: 0x7000,    # AIN3 vs GND
    # 差分模式 (如需):
    (0, 1): 0x0000,  # AIN0 - AIN1
    (0, 3): 0x1000,  # AIN0 - AIN3
    (1, 3): 0x2000,  # AIN1 - AIN3
    (2, 3): 0x3000,  # AIN2 - AIN3
}


class ADS1115:
    """ADS1115 16-bit I2C ADC"""

    def __init__(self, i2c, addr=_DFT_ADDR, gain=4.096, sps=860):
        """
        Args:
            i2c:  machine.I2C 实例（已初始化）
            addr: I2C 地址 (默认 0x48)
            gain: PGA 满量程 (V), 可选 6.144/4.096/2.048/1.024/0.512/0.256
            sps:  采样率, 可选 8/16/32/64/128/250/475/860
        """
        self.i2c = i2c
        self.addr = addr

        # 选最接近的 PGA
        gain_opts = sorted(_PGA_CFG.keys())
        self._pga = min(gain_opts, key=lambda x: abs(x - gain))
        self._pga_code = _PGA_CFG[self._pga]

        # 选最接近的 SPS
        sps_opts = sorted(_DR_CFG.keys())
        self._sps = min(sps_opts, key=lambda x: abs(x - sps))
        self._dr_code = _DR_CFG[self._sps]

        self.lsb = self._pga / 32768.0  # 每 LSB 对应电压 (V)

    # ---- 底层寄存器读写 ----

    def _rd16(self, reg):
        data = bytearray(2)
        self.i2c.readfrom_mem_into(self.addr, reg, data)
        return (data[0] << 8) | data[1]

    def _wr16(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg,
                             bytes([(val >> 8) & 0xFF, val & 0xFF]))

    # ---- 单次/连续读取 ----

    def _build_config(self, mux, pga_code, cont, alert_rdy=False):
        mode = 0x0000 if cont else 0x0100
        comp_que = 0x0000 if alert_rdy else 0x0003  # 00=RDY, 11=关闭
        return 0x8000 | mux | pga_code | mode | self._dr_code | comp_que

    def _do_read(self, mux, gain, cont):
        pga_code = self._pga_code
        if gain is not None:
            opts = sorted(_PGA_CFG.keys())
            pga_code = _PGA_CFG[min(opts, key=lambda x: abs(x - gain))]
        config = self._build_config(mux, pga_code, cont)
        self._wr16(_CFG_REG, config)
        if not cont:
            time.sleep_ms(max(1, 1000 // self._sps + 1))
        raw = self._rd16(_CVT_REG)
        if raw >= 0x8000:
            raw -= 0x10000
        return raw

    def read_raw(self, channel=0, gain=None, cont=False):
        """
        单端读取 (AINx vs GND)
        channel: 0~3, 返回 int (-32768~32767)
        """
        mux = _MUX_CFG.get(channel, 0x4000)
        return self._do_read(mux, gain, cont)

    def read_raw_diff(self, ch_p, ch_n, gain=None, cont=False):
        """
        差分读取 (ch_p - ch_n)
        可用差分对:
          (0,1): AIN0 - AIN1   (0x0000)
          (0,3): AIN0 - AIN3   (0x1000)
          (1,3): AIN1 - AIN3   (0x2000)
          (2,3): AIN2 - AIN3   (0x3000)
        """
        pair = (ch_p, ch_n)
        mux = _MUX_CFG.get(pair)
        if mux is None:
            raise ValueError(f"不支持的差分对: {pair}")
        return self._do_read(mux, gain, cont)

    def read_voltage(self, channel=0, gain=None):
        """单端电压 (V)"""
        lsb = self._lsb_for(gain)
        return self.read_raw(channel, gain) * lsb

    def _lsb_for(self, gain):
        """返回指定 gain 对应的 LSB, None=用实例默认"""
        if gain is None:
            return self.lsb
        return gain / 32768.0

    def read_voltage_avg(self, channel=0, samples=8, gain=None):
        """单端多次采样平均 (V)"""
        lsb = self._lsb_for(gain)
        total = 0
        for _ in range(samples):
            total += self.read_raw(channel, gain)
        return (total / samples) * lsb

    def read_diff_voltage(self, ch_p, ch_n, gain=None, samples=1):
        """差分电压 (V), 多次采样取平均"""
        lsb = self._lsb_for(gain)
        if samples <= 1:
            return self.read_raw_diff(ch_p, ch_n, gain) * lsb
        total = 0
        for _ in range(samples):
            total += self.read_raw_diff(ch_p, ch_n, gain)
        return (total / samples) * lsb

    def set_continuous(self, channel=0, gain=None):
        """切到单端连续转换模式"""
        mux = _MUX_CFG.get(channel, 0x4000)
        pga_code = self._pga_code
        if gain is not None:
            opts = sorted(_PGA_CFG.keys())
            pga_code = _PGA_CFG[min(opts, key=lambda x: abs(x - gain))]
        config = 0x8000 | mux | pga_code | 0x0000 | self._dr_code
        self._wr16(_CFG_REG, config)
        time.sleep_ms(2)

    def read_latest(self):
        """连续模式下读最新值"""
        raw = self._rd16(_CVT_REG)
        if raw >= 0x8000:
            raw -= 0x10000
        return raw


# ==================== 快捷检测 / 工厂 ====================

def scan_device(i2c=None, addr=_DFT_ADDR):
    """扫描 I2C 总线，检测 ADS1115。自动尝试 0x48-0x4B。返回 True/False"""
    if i2c is None:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
    devs = i2c.scan()
    # 先试指定地址
    if addr in devs:
        print(f"✅ ADS1115 已检测到 (0x{addr:02X})")
        return True
    # 没找到，试试其他可能的地址
    alt_addrs = [a for a in [0x48, 0x49, 0x4A, 0x4B] if a != addr]
    for a in alt_addrs:
        if a in devs:
            print(f"✅ ADS1115 已检测到 (0x{a:02X}, 非默认地址)")
            # 更新模块默认地址
            global _DFT_ADDR
            _DFT_ADDR = a
            return True
    print(f"⚠ ADS1115 未检测到 (已尝试 0x48-0x4B)")
    print(f"  I2C 设备: {[hex(d) for d in devs]}")
    if not devs:
        print("  ⚡ 总线无设备！检查 I2C 接线 (SDA=21, SCL=22)")
    return False


def create_default(i2c=None):
    """快速创建 ADS1115 实例，自动检测 I2C 总线
    默认 PGA=±6.144V (兼容所有传感器量程)
    """
    if i2c is None:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
    if not scan_device(i2c):
        return None
    return ADS1115(i2c, addr=_DFT_ADDR, gain=6.144, sps=860)
