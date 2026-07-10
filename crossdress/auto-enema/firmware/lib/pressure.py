"""
lib/pressure.py — 压力传感器驱动
  气路: XGZP6847A (GPIO36 或 ADS1115 AIN0, 0~40kPa)
  水路: HX710B   (GPIO35/5, 数字, 0~11kPa)

用法:
  # ESP32 内置 ADC (旧接线)
  sensor = create_air_sensor()

  # 用 ADS1115 (气路)
  from lib.ads1115 import create_default
  ads = create_default()
  sensor = create_air_sensor(ads=ads)

  # 改水路量程 (28kPa)
  sensor = create_water_sensor(extra_pulses=2)
"""
from machine import ADC, Pin
import time

# ============================================================
# 气路 — XGZP6847A (模拟输出)
# 支持 ESP32 内置 ADC (GPIO36) 或 ADS1115 (AIN0)
# ============================================================
class AirSensor:
    """XGZP6847A 模拟气压传感器

    支持两种 ADC 后端:
      - ESP32 内置 ADC (默认, GPIO36)
      - ADS1115 外置 ADC (I2C, AIN0)
    """
    def __init__(self, ads1115=None, pin=36, v_zero=0.115, v_kpa=0.090,
                 adc_channel=0):
        """
        Args:
            ads1115:    ADS1115 实例 (None=使用 ESP32 内置 ADC)
            pin:        ESP32 ADC 引脚 (内置 ADC 时使用, 默认 GPIO36)
            v_zero:     0kPa 时的电压 (V)
            v_kpa:      每 kPa 的电压增量 (V/kPa)
            adc_channel: ADS1115 通道 (默认 AIN0)
        """
        self.ads = ads1115
        self._ch = adc_channel
        self.v_zero = v_zero
        self.v_kpa = v_kpa

        if ads1115 is None:
            # 使用 ESP32 内置 ADC
            self.adc = ADC(Pin(pin))
            self.adc.atten(ADC.ATTN_11DB)
            self.adc.width(ADC.WIDTH_12BIT)
        else:
            self.adc = None

    def read_voltage(self, samples=8):
        if self.ads:
            return self.ads.read_voltage_avg(self._ch, samples)
        else:
            total = 0
            for _ in range(samples):
                total += self.adc.read()
                time.sleep_ms(1)
            return total / samples / 4095 * 3.3

    def read_kpa(self, samples=8):
        v = self.read_voltage(samples)
        p = (v - self.v_zero) / self.v_kpa
        return max(0, p)

    def calibrate_zero(self, samples=15):
        print("气路归零中...")
        total = 0.0
        if self.ads:
            for _ in range(samples):
                total += self.ads.read_voltage(self._ch)
                time.sleep_ms(100)
            self.v_zero = total / samples
        else:
            for _ in range(samples):
                total += self.adc.read()
                time.sleep_ms(100)
            self.v_zero = total / samples / 4095 * 3.3
        print(f"气路零位: {self.v_zero:.3f}V")
        return self.v_zero

    def set_calibration(self, v_zero, v_kpa):
        self.v_zero = v_zero
        self.v_kpa = v_kpa


# ============================================================
# 水路 — HX710B (数字串行 on GPIO35/5)
#   可通过 extra_pulses 切换增益/量程
# ============================================================
class WaterSensor:
    """HX710B 数字压力传感器 (GPIO35=OUT, GPIO5=SCK)

    增益选择 (extra_pulses):
      1 → Gain 128  (最灵敏, 量程 ~7.5 kPa)
      3 → Gain 64   (量程 ~15 kPa)
      2 → Gain 32   (量程 ~28 kPa)  ← 推荐
      4 → 最低增益   (量程 ~56 kPa)
    """
    def __init__(self, dout_pin=35, sck_pin=5, scale=0.000001314,
                 extra_pulses=1):
        """
        extra_pulses: HX710B 增益选择脉冲数 (1/2/3/4)
        scale: ADC counts → kPa 转换系数 (换增益后需重标)
        """
        self.dout = Pin(dout_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT)
        self.sck.value(0)
        self._offset = 2863062   # 通大气零位 (Gain 128 旧值, 换了需重标)
        self._scale = scale
        self._extra = extra_pulses

    def _wait_ready(self, timeout_ms=1000):
        start = time.ticks_ms()
        while self.dout.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise TimeoutError("HX710B not ready")
            time.sleep_ms(1)

    def read_raw(self, timeout_ms=1000):
        self._wait_ready(timeout_ms)
        raw = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            raw = (raw << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(1)
        for _ in range(self._extra):
            self.sck.value(1)
            time.sleep_us(1)
            self.sck.value(0)
            time.sleep_us(1)
        if raw & 0x800000:
            raw -= 0x1000000
        return raw

    def read_raw_avg(self, samples=5):
        vals = [self.read_raw() for _ in range(samples)]
        if samples >= 3:
            vals.sort()
            vals = vals[1:-1]
        return sum(vals) // len(vals)

    def read_kpa(self, samples=5):
        tared = self.read_raw_avg(samples) - self._offset
        p = tared * self._scale
        return max(0, p)

    def calibrate_zero(self, samples=15):
        print("水路归零中...")
        vals = [self.read_raw_avg() for _ in range(samples)]
        self._offset = sum(vals) // len(vals)
        print(f"水路零位 Offset: {self._offset}")
        return float(self._offset)

    def set_calibration(self, offset, scale):
        self._offset = offset
        self._scale = scale


# ============================================================
# 原始电桥传感器 (通过 ADS1115 差分读取)
#   适用于 VO+/VO- 差分输出型压力传感器
#   替代 HX710B 作为水路传感器
# ============================================================
class BridgeSensor:
    """差分桥式压力传感器 (ADS1115 差分 AIN1-AIN3)

    已验证真实接线:
      VO+ (Pin4) → AIN1
      VO- (Pin6) → AIN3  (⚠ 不是 Pin1!)
      VS+ (Pin5) → 5V
      VS- (Pin2) → GND

    传感器自然差分偏压 ~-1.3V, 需用 ±4.096V PGA 避饱和。
    """
    def __init__(self, ads1115, ch_p=1, ch_n=3,
                 mv_zero=7, mv_kpa=1.8, gain=0.256):
        """
        Args:
            ads1115:  ADS1115 实例
            ch_p/ch_n: 差分通道 (默认 AIN1-AIN3)
            mv_zero:   0kPa 时的差分电压 (mV), 实测 ~-1290mV
            mv_kpa:    每 kPa 的电压增量 (mV/kPa), 需标定
            gain:      PGA 满量程, 差分用 ±4.096V
        """
        self.ads = ads1115
        self._ch_p = ch_p
        self._ch_n = ch_n
        self._gain = gain
        self.mv_zero = mv_zero
        self.mv_kpa = mv_kpa

    def read_diff_mv(self, samples=4):
        """读取差分电压 (mV), samples 少用避免时序问题"""
        return self.ads.read_diff_voltage(
            self._ch_p, self._ch_n,
            gain=self._gain, samples=samples) * 1000

    def read_kpa(self, samples=4):
        mv = self.read_diff_mv(samples)
        p = (mv - self.mv_zero) / self.mv_kpa
        return max(0, p)

    def calibrate_zero(self, samples=10):
        print("传感器归零中... (通大气)")
        vals = []
        for _ in range(samples):
            vals.append(self.ads.read_diff_voltage(
                self._ch_p, self._ch_n, gain=self._gain))
            time.sleep_ms(100)
        self.mv_zero = sum(vals) / len(vals) * 1000
        print(f"零位: {self.mv_zero:.2f} mV")
        return self.mv_zero

    def set_calibration(self, mv_zero, mv_kpa):
        self.mv_zero = mv_zero
        self.mv_kpa = mv_kpa


# ===== 工厂函数 =====
def create_air_sensor(ads1115=None, v_zero=0.030):
    """气路: XGZP6847A on GPIO36 或 ADS1115 AIN0
    v_zero: 当前通大气 AIN0 电压 (V), 实测 0.030V
    """
    if ads1115:
        return AirSensor(ads1115=ads1115, v_zero=v_zero, v_kpa=0.090)
    return AirSensor(pin=36, v_zero=0.115, v_kpa=0.090)


# 各 extra_pulses 对应的理论 scale 估算值 (基于 Gain 128 标定值推算)
_EST_SCALE = {1: 0.000001314, 3: 0.000000657, 2: 0.000000328, 4: 0.000000164}

def create_water_sensor(extra_pulses=2):
    """水路: HX710B on GPIO35/5

    Args:
        extra_pulses: 1=Gain128(~7.5kPa), 2=Gain32(~28kPa, 默认),
                      3=Gain64(~15kPa), 4=最低增益(~56kPa)

    换增益后务必重新跑水柱法标定!
    """
    scale = _EST_SCALE.get(extra_pulses, 0.000000328)
    return WaterSensor(dout_pin=35, sck_pin=5, scale=scale,
                       extra_pulses=extra_pulses)
