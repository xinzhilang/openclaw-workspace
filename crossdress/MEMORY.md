# Long-Term Memory


## Promoted From Short-Term Memory (2026-06-24)

<!-- openclaw-memory-promotion:memory:memory/2026-06-20.md:10:13 -->
- LCD 显示画面设计: | 状态 | 第一行 | 第二行 | |:----:|--------|--------| | 空闲 | `A:12.3 W: 5.6` | `Ready 300ml` | | 充气 | `Inflate` | `24/25kPa` | [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-20.md:10-13]
<!-- openclaw-memory-promotion:memory:memory/2026-06-20.md:14:17 -->
- LCD 显示画面设计: | 注水 | `Fill 180/300` | `W:12kPa` | | 保持 | `Hold 25s` | `A:24 W:10` | | 定时注水 | `Timed Pump` | `30s remain` | | WiFi 连接后 | `IP:192.168.x.xx` | `Ready` | [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-20.md:14-17]
<!-- openclaw-memory-promotion:memory:memory/2026-06-20.md:31:32 -->
- 已清理: 删除所有 ` - 副本.py` 临时文件; LCD 显示独立为 `lib/display.py`，`webctrl.py` 通过 `import lib.display as disp` 调用 [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-20.md:31-32]
<!-- openclaw-memory-promotion:memory:memory/2026-06-20.md:19:21 -->
- LCD 显示画面设计: LCD 引脚：SDA→GPIO21, SCL→GPIO22, I2C 地址 0x27; `lcd_update()` 在 tick() / safe() / start_cycle() 中触发，各状态画面自动切换; 手动操作（充气/放气/开阀/零位标定）后也同步刷新 LCD [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-20.md:19-21]

## Promoted From Short-Term Memory (2026-06-26)

<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:19:22 -->
- 当前接线: | 用途 | 传感器 | ESP-32S 引脚 | |------|--------|-------------| | 气路 | XGZP6847A (GPIO36/SVP) | OUT→SVP(IO36) | | 水路 | HX710B (GPIO35/5) | OUT→IO35, SCK→IO5 | [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-22.md:19-22]
<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:23:25 -->
- 当前接线: | 流量计 | YF-S401 | IO34 (中断) | | 编码器 | 旋转编码器 | IO32, IO33 | | LCD | LCD1602 I2C | IO21(SDA), IO22(SCL) | [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-22.md:23-25]
<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:28:29 -->
- 待办: [ ] XGZP6847A 气路标定（用指针压力表）; [ ] 上线测试整机流程 [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-22.md:28-29]

## Promoted From Short-Term Memory (2026-06-27)

<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:15:16 -->
- 固件更新: `firmware/lib/pressure.py` → 重写：AirSensor(XGZP6847A) + WaterSensor(HX710B); `firmware/lib/core.py` → 无需改动 [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-22.md:15-16]
<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:4:7 -->
- 已到货 & 测试: **HX710B 压力传感器模块**（AD20-11F）; 数字接口（OUT=GPIO35, SCK=GPIO5）; Gain 128，量程 0~11 kPa（饱和点）; 水柱法标定: Offset=2863062, Scale=0.000001314, R²=0.9990 ✅ [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-22.md:4-7]
<!-- openclaw-memory-promotion:memory:memory/2026-06-22.md:9:12 -->
- 已到货 & 测试: **XGZP6847A 压力传感器绿板**; 模拟输出 on GPIO36/SVP; 量程 0~40 kPa（ESP32 ADC限制在~35kPa）; 临时系数: v_zero=0.115V, v_kpa=0.090 [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-22.md:9-12]

## Promoted From Short-Term Memory (2026-06-29)

<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:13:16 -->
- 原始电桥传感器接入 (17:38): 嘻嘻还有一只未标定气压传感器，6 脚电桥输出; VO+(Pin4) / VO-(Pin1), VS+(Pin5)/VS-(Pin2), NC(Pin3), Pin6 悬空; 桥阻 5kΩ, FS 输出 35-110mV, 量程可选 10~700kPa; ADS1115 差分读取（AIN1-AIN3），PGA ±0.256V [score=0.888 recalls=0 avg=0.620 source=memory/2026-06-24.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:17:20 -->
- 原始电桥传感器接入 (17:38): 新增 `BridgeSensor` 类 (`pressure.py`)，差分 AIN1-AIN3，±0.256V; 验证接线：VO+ (Pin4)→AIN1, VO- (Pin6)→AIN3, VS+/VS- 正常; 通大气零位 ~-77mV，手捏变化 ~5-7mV ✅ 传感器工作正常; 标定完成: XGZP 对标, R²=0.997 ✅ [score=0.888 recalls=0 avg=0.620 source=memory/2026-06-24.md:17-20]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:22:23 -->
- 原始电桥传感器接入 (17:38): 传感器差分范围 ~-3700 ~ +2000 mV (0~65 kPa); core.py 已切换: 有 ADS1115 则水路走 BridgeSensor(AIN1-AIN3) [score=0.888 recalls=0 avg=0.620 source=memory/2026-06-24.md:22-23]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:21:21 -->
- 原始电桥传感器接入 (17:38): mv_zero=-3744, mv_kpa=86, PGA=±6.144V [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-24.md:21-21]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:25:27 -->
- 原始电桥传感器接入 (17:38): ADS1115 全通道:; AIN0: XGZP6847A 气路 (单端); AIN1-AIN3: 新桥式传感器 水路 (差分) → 替换 HX710B [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-24.md:25-27]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:4:7 -->
- ADS1115 模块到货 (17:22): 嘻嘻的 ADS1115 模块到货了; 写了全套支持代码：; `lib/ads1115.py` — ADS1115 16-bit I2C ADC 驱动（单次/连续模式，可配PGA/SPS）; `lib/pressure.py` — AirSensor 升级，同时支持 ESP32 内置 ADC 和 ADS1115 [score=0.849 recalls=0 avg=0.620 source=memory/2026-06-24.md:4-7]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:8:10 -->
- ADS1115 模块到货 (17:22): `lib/core.py` — 启动时自动检测 ADS1115，有就用、没有回退; `hardware/test_ads1115.py` — 到货验证测试（I2C扫描 + 电压读取 + AIN0实时监控）; `hardware/calibrate_ads1115_xgzp.py` — 接 XGZP6847A 后的重新标定脚本 [score=0.849 recalls=0 avg=0.620 source=memory/2026-06-24.md:8-10]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:24:24 -->
- 原始电桥传感器接入 (17:38): 无 ADS1115 则回退 HX710B [score=0.836 recalls=0 avg=0.620 source=memory/2026-06-24.md:24-24]

## Promoted From Short-Term Memory (2026-06-30)

<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:12:14 -->
- 标定持久化: 新建 `lib/calibration.py` — 标定参数存到 ESP32 flash; `core.py` 开机自动加载 `/calib.json`，点"标定"自动保存; 自动适配 BridgeSensor 和 HX710B [score=0.816 recalls=0 avg=0.620 source=memory/2026-06-26.md:12-14]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:22:23 -->
- 泵速控制: `_set_pump()` 函数，按 Web UI 设的百分比调速; 之前全部硬编码 `duty(1000)` [score=0.816 recalls=0 avg=0.620 source=memory/2026-06-26.md:22-23]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:6:9 -->
- 蜂鸣器: 查明是有源蜂鸣器，**高电平触发**（不是低电平）; 当前测试：一上电就响（硬件问题，需要外置下拉电阻）; 代码中 `buz()` 已全部调整为 `value(1)=响, value(0)=停`; 开机自检：boot.py 两声 + core.py 三声（`beep_startup` 在 WiFi 连上后调用） [score=0.816 recalls=0 avg=0.620 source=memory/2026-06-26.md:6-9]

## Promoted From Short-Term Memory (2026-07-01)

<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:17:19 -->
- I2C 共享: `core.py` 创建共享 `_i2c`，ADS1115 和 LCD 共用; I2C 频率从 400kHz 降到 100kHz（面包板更稳定）; ADS1115 扫描自动试 0x48-0x4B 四个地址 [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:17-19]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:26:29 -->
- Web UI 大升级: 曲线图：Canvas 原生，120 点 ≈ 60s 历史; 阈值虚线：气压/水压目标值显示; 快捷预设：快速/轻柔/深度 + 自定义保存; 运行计时：`fmtTime()` 显示 MM:SS [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:26-29]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:30:31 -->
- Web UI 大升级: 急停闪烁：运行时停止按钮变红 + 脉冲动画; 传感器状态：ADC 模式 + 水路类型 [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:30-31]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:34:37 -->
- 双模式切换（网页端选择）: 灌肠模式（默认）↔ 炮机模式; 页面顶部切换链接触发 `switch_mode()`; 炮机模式接管 GPIO19（电机 PWM），启动 GPIO32/33（限位开关）; 灌肠模式释放 GPIO19 重新初始化为泵 PWM [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:34-37]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:40:43 -->
- 炮机控制器 (`lib/fucker.py`): 6 种运行模式：恒定/正弦波/随机/脉冲/渐加速/波浪; 速度滑条 0-100%，实时调速; 定时器 0-120 分钟; 限位保护（GPIO32/33 触发即停） [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:40-43]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:44:44 -->
- 炮机控制器 (`lib/fucker.py`): 软启动/软停止（200ms 渐变） [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:44-44]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:47:50 -->
- 节目模式（第 7 模式）: 多段自动切换：每段定义 `{mode, speed, duration}`; 浏览器内编辑 JSON，点"应用"生效; 点"示例"一键加载 5 段方案; 自动推进：一段结束 → 下一段 → 全部播完自动停止 [score=0.856 recalls=0 avg=0.620 source=memory/2026-06-26.md:47-50]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:21:24 -->
- ✅ 参数面板重排: 水量: ±50/±100, 默认 500ml; 泵速: ±10, 默认 60%; 保持: ±10/±30, 默认 60s; 气压/水压: ±1/±5, 默认 25kPa [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-27.md:21-24]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:25:25 -->
- ✅ 参数面板重排: 标签对齐，flex 布局干净 [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-27.md:25-25]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:4:7 -->
- ✅ 蜂鸣器问题解决: **根因**: 5V 有源蜂鸣器模块 CMOS 阈值 ~3.5V，ESP32 GPIO 最高 3.3V 关不掉; **方案**: 改用 IN/OUT 切换控制（OUT+LOW=响 → IN高阻=静音）; 改 `core.py`: `buz()` 重写; 改 `boot.py`: 去掉 GPIO18 初始化，自检也用 IN/OUT 切换 [score=0.844 recalls=0 avg=0.620 source=memory/2026-06-27.md:4-7]

## Promoted From Short-Term Memory (2026-07-02)

<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:11:12 -->
- ✅ 网页系统信息: 新增 `/api/sys` 接口（mem_free/used, cpu_freq, flash_size, uptime）; enema.html + fucker.html 底部显示 `🧠 xx/xxKB ⚡ xxMHz 💾 xxMB ⏱ xxhxxm` [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-27.md:11-12]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:15:18 -->
- ✅ 性能优化: JS 轮询间隔 1500ms → 400ms; tick() 刷新间隔 100ms → 50ms; GC 策略：每次请求都跑 → 每 10 次才跑; Socket 超时 50ms → 10ms [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-27.md:15-18]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:8:8 -->
- ✅ 蜂鸣器问题解决: `boot.py` 旧代码把 GPIO18 设 OUT+LOW 保持 → 上电一直响，改完正常 [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-27.md:8-8]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:51:52 -->
- 节目模式（第 7 模式）: 面板显示当前段序号/名称/剩余时间; **Bug 修复**：`_prog_mode`/`_prog_speed` 内部变量，不覆盖 `self.mode` [score=0.862 recalls=0 avg=0.620 source=memory/2026-06-26.md:51-52]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:55:56 -->
- ADS1115 识别修复: 用户反馈 ADS1115 未检测到 → 确认 I2C 地址问题; 自动扫描 0x48-0x4B，不管 ADDR 脚怎么接都能认 [score=0.862 recalls=0 avg=0.620 source=memory/2026-06-26.md:55-56]
