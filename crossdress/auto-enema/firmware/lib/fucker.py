"""
lib/fucker.py — 炮机控制器
  与灌肠器共用 IRF520 模块 (GPIO19)，物理切换端子
  限位开关: GPIO32/33 (INPUT_PULLUP)
"""
import math, time
from machine import Pin, PWM

# ═══════════════ 默认引脚 ═══════════════
PIN_MOTOR_DEF = 19       # 与灌肠器蠕动泵共用 IRF520
PIN_LIMIT_A = 32         # 前限位
PIN_LIMIT_B = 33         # 后限位
MOTOR_FREQ = 1000        # 与水泵频率一致，不需改
MAX_DUTY = 1023

MODE_LIST = ['恒定', '正弦波', '随机', '脉冲', '渐加速', '波浪', '节目']


class Fucker:
    """炮机控制器"""

    def __init__(self):
        self.pwm = None
        self.pin_a = Pin(PIN_LIMIT_A, Pin.IN, Pin.PULL_UP)
        self.pin_b = Pin(PIN_LIMIT_B, Pin.IN, Pin.PULL_UP)
        self._reset_state()

    def _reset_state(self):
        self.running = False
        self.speed = 60
        self.mode = 0
        self.time_limit = 0
        self.stages = []
        self._stage_idx = 0
        self._stage_elapsed = 0
        self._duty = 0
        self._t0 = 0
        self._mode_t = 0
        self._pulse_t = 0
        self._elapsed = 0
        self._limit_hit = False
        self._rand_t = 0
        self._rand_v = 0
        self._rand_next = 3

    def set_program(self, stages):
        self.stages = stages
        print(f'📋 节目单已设置: {len(stages)} 段')

    def get_program_status(self):
        if not self.stages:
            return {'total': 0, 'current': 0, 'name': '', 'stage_remain': 0, 'stage_speed': 0, 'total_dur': 0, 'note': ''}
        st = self.stages[self._stage_idx] if self._stage_idx < len(self.stages) else None
        total_dur = sum(s['duration'] for s in self.stages)
        return {
            'total': len(self.stages),
            'current': self._stage_idx + 1,
            'name': MODE_LIST[st['mode']] if st else '',
            'stage_speed': st['speed'] if st else 0,
            'stage_remain': max(0, st['duration'] - self._stage_elapsed) if st else 0,
            'total_dur': total_dur,
            'note': st.get('note', '') if st else '',
        }

    def load_session_90min(self):
        """加载 90 分钟终极榨精节目"""
        self.stages = [
            {'mode':0, 'speed':20, 'duration':480, 'note':'❄️ 2.5cm冰棒 戴乳夹+震动蛋低档 先测肛温'},
            {'mode':3, 'speed':35, 'duration':360, 'note':'🔴 换019粉振动 震动全开 ➔ ②结束前塞🟢薄荷胶囊'},
            {'mode':1, 'speed':45, 'duration':420, 'note':'❄️ 换3.0cm冰棒 薄荷+冰双重清凉 测肛温'},
            {'mode':2, 'speed':55, 'duration':420, 'note':'🌈 换彩虹中号 戴眼罩+塞肛珠 不用看节奏'},
            {'mode':4, 'speed':65, 'duration':480, 'note':'🐚 换014粉龟甲 渐加速越操越快 口塞戴上'},
            {'mode':0, 'speed':70, 'duration':420, 'note':'❄️ 换3.5cm冰棒 已经很大了 ➔ ⑥结束前塞🔴辣椒胶囊'},
            {'mode':5, 'speed':75, 'duration':420, 'note':'⚫ 换006黑巨根 辣椒开始在肠子里燃烧🔥'},
            {'mode':2, 'speed':80, 'duration':360, 'note':'❄️ 换4.0cm冰棒 辣到受不了插冰棒进来❄️🔥'},
            {'mode':0, 'speed':85, 'duration':360, 'note':'🌈 换彩虹大号 让肠道缓一缓 测肛温'},
            {'mode':3, 'speed':88, 'duration':300, 'note':'❄️ 换4.5cm冰棒 最粗的 ➔ ⑩结束前塞⚪白胶囊'},
            {'mode':4, 'speed':92, 'duration':420, 'note':'🎯 葫芦造型 三种感觉同时在屁眼里炸裂!!'},
            {'mode':5, 'speed':95, 'duration':420, 'note':'💦 半融4.5cm冰沙 冰碴混着辣椒水咕叽响'},
            {'mode':0, 'speed':100, 'duration':300, 'note':'🚨 全新冰冻4.5cm 满速冲刺! 全部交出来!!!'},
        ]
        print(f'📋 90分钟终极节目已加载 ({len(self.stages)}段)')
        return self.stages

    def init(self):
        """初始化（切到炮机模式时调用）"""
        self.pwm = PWM(Pin(PIN_MOTOR_DEF), freq=MOTOR_FREQ, duty=0)
        print("✅ 炮机模式已加载 (GPIO19=电机, 32/33=限位)")

    def deinit(self):
        """释放（切回灌肠模式时调用）"""
        self.stop()
        if self.pwm:
            self.pwm.deinit()
            self.pwm = None
        self._reset_state()
        print("ℹ️ 炮机模式已卸载")

    def start(self):
        if self.running:
            return
        self.running = True
        self._duty = 0
        self._t0 = time.time()
        self._mode_t = 0
        self._pulse_t = 0
        self._elapsed = 0
        self._limit_hit = False
        self._rand_t = 0
        self._rand_v = self.speed / 100.0
        self._rand_next = 3
        self._stage_idx = 0
        self._stage_elapsed = 0
        # 节目模式：加载第一段到内部变量，mode 保持 6 不变
        if self.mode == 6 and self.stages:
            self._prog_mode = self.stages[0]['mode']
            self._prog_speed = self.stages[0]['speed']
        sp = self._prog_speed if self.mode == 6 else self.speed
        md = self._prog_mode if self.mode == 6 else self.mode
        print(f"🔥 炮机启动  速度={sp}%  模式={MODE_LIST[md]}")

    def stop(self):
        self.running = False
        if self.pwm:
            for i in range(10):
                d = int(self.pwm.duty() * (1 - i / 10))
                self.pwm.duty(d)
                time.sleep_ms(15)
            self.pwm.duty(0)

    def tick(self):
        """每 ~100ms 调用"""
        if not self.running or not self.pwm:
            return

        t = time.time()
        self._elapsed = t - self._t0

        # 限位检查
        if self.pin_a.value() == 0 or self.pin_b.value() == 0:
            self._limit_hit = True
            self.pwm.duty(0)
            return
        self._limit_hit = False

        # 定时检查
        if self.time_limit > 0 and self._elapsed >= self.time_limit:
            self.stop()
            return

        dt = 0.1
        target = self._calc_target(dt)

        diff = target - self._duty
        if abs(diff) > 2:
            self._duty += diff * 0.08
        else:
            self._duty = target
        self._duty = max(0, min(MAX_DUTY, self._duty))
        self.pwm.duty(int(self._duty))

        # 节目模式：检查是否进入下一段
        if self.mode == 6 and self.stages and self._stage_idx < len(self.stages):
            self._stage_elapsed += dt
            if self._stage_elapsed >= self.stages[self._stage_idx]['duration']:
                self._stage_idx += 1
                self._stage_elapsed = 0
                if self._stage_idx >= len(self.stages):
                    self.stop()
                    print('✅ 节目播放完毕')
                else:
                    ns = self.stages[self._stage_idx]
                    self._prog_mode = ns['mode']
                    self._prog_speed = ns['speed']
                    # 重置模式计时器
                    self._mode_t = 0
                    self._pulse_t = 0
                    self._rand_t = 0
                    n = ns.get('note', '')
                    print(f'📋 第{self._stage_idx+1}段: {MODE_LIST[self._prog_mode]} @{self._prog_speed}% {n}')

    def _calc_target(self, dt):
        # 节目模式下使用内部子模式/速度
        if self.mode == 6:
            md = self._prog_mode
            spd = self._prog_speed
        else:
            md = self.mode
            spd = self.speed
        s = spd / 100.0 * MAX_DUTY
        self._mode_t += dt

        if md == 0:           # 恒定
            return s
        elif md == 1:         # 正弦波 10s
            phase = (math.sin(self._mode_t * 2 * math.pi / 10) + 1) / 2
            return s * (0.3 + 0.7 * phase)
        elif md == 2:         # 随机
            self._rand_t += dt
            if self._rand_t >= self._rand_next:
                import random
                self._rand_v = s * (0.2 + 0.8 * (random.getrandbits(8) / 255))
                self._rand_next = 3 + (random.getrandbits(8) / 255) * 5
                self._rand_t = 0
            return self._rand_v
        elif md == 3:         # 脉冲 2s冲 1.5s停
            self._pulse_t += dt
            return s if (self._pulse_t % 3.5) < 2.0 else 0
        elif md == 4:         # 渐加速 60s
            prog = min(self._elapsed / 60.0, 1.0)
            return s * (0.3 + 0.7 * prog)
        elif md == 5:         # 波浪 30s
            phase = (math.sin(self._mode_t * 2 * math.pi / 30) + 1) / 2
            return s * (0.2 + 0.8 * phase)
        return s

    def get_status(self):
        # 节目模式下显示当前子模式
        show_mode = self._prog_mode if self.mode == 6 else self.mode
        show_speed = self._prog_speed if self.mode == 6 else self.speed
        s = {
            'running': self.running,
            'speed': show_speed,
            'mode': self.mode,
            'mode_name': MODE_LIST[show_mode],
            'elapsed': self._elapsed,
            'time_limit': self.time_limit,
            'remaining': max(0, self.time_limit - self._elapsed) if self.time_limit > 0 else 0,
            'limit_hit': self._limit_hit,
            'duty_pct': round(self._duty / MAX_DUTY * 100, 1),
        }
        if self.mode == 6:
            s['program'] = self.get_program_status()
        return s
