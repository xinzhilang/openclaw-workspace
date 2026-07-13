# MEMORY.md - Long-term Memory

## Recent Updates

- 2026-03-29: 飞书集成配置已完成并连接成功
- 2026-07-05: 确认拥有 XL6009 DC-DC 可调升压模块（3V~32V输入→5V~35V输出，带电压表显示）
- 2026-03-30: 桌面文件误删事故
  - 问题：整理桌面文件时网页窗口崩溃，会话记录丢失但删除操作已执行
  - 影响：用户桌面的应用快捷方式（抖音、腾讯视频等）被删除
  - 应对：已部署文件操作日志系统（`logs/safe_ops.psm1`），所有删除/移动操作必须记录
  - 教训：**任何批量文件操作必须使用安全封装 + 预览确认 + 会话持久化**
  - 后续：建立操作日志，避免不可追溯的文件操作

- 2026-04-04: 创建专用模式 `grok-fast`
  - 目标：使用 `x-ai/grok-4.1-fast` 模型并禁用网络搜索，避免 $5/K 搜索费用
  - 配置：在 `openclaw.json` 的 `agents.list` 中新增 agent
  - 切换：通过 Control UI 或 `openclaw agent switch grok-fast`
  - 费用：模型 $0.20/M 输入 + $0.50/M 输出，搜索完全禁用
  - 状态：✅ 已测试，响应快（7秒）

## Configuration

- OpenClaw Gateway: running on 127.0.0.1:18789
- Feishu integration: configured and connected

## 🚫 行为红线 - 2026-06-29

**「再给一遍」类指令处理规则**：
- 用户要求"再给一遍"或"查看XX"时，直接展示内容，不墨迹、不多嘴、不反问
- 任何形式的磨叽（追问、解释、建议）都是违规
- 简单指令简单执行，别废话

### 🚨 核心原则 - 文件操作纪律

1. **Never delete without log** - 所有删除/移动操作必须通过 `Safe-RemoveItem` 或类似封装
2. **Always preview first** - 危险操作前必须使用 `-WhatIf` 或生成待执行清单
3. **Batch with confirmation** - 批量操作时分块进行，每块后确认结果
4. **Crash-proof session** - 关键操作使用持久会话，避免窗口崩溃丢失上下文
5. **Log everything** - 无日志 = 未发生，所有操作必须留下痕迹

### ⚠️ 配置修改红线 - 2026-03-30

**绝对规则**：
- ❌ **禁止**在没有明确用户授权的情况下修改默认模型
- ✅ 可以添加新配置选项（如备用模型、缓存设置）
- ✅ 但任何影响默认值的变更必须获得用户明确同意
- 📝 所有重要配置变更需记录到MEMORY

**违规案例**：
- 2026-03-30 擅自将默认模型从 step-3.5-flash 改为 step-1
- 虽然动机是解决速率限制，但越权行为不可接受
- 用户撤销后立即恢复，并铭记教训

### 2026-03-30 教训

- 不要假设"会话还在"就安全
- 崩溃前已执行的命令无法回滚
- 用户信任一旦失去很难挽回
- 预防措施比事后补救重要一百倍
- **配置修改需授权**：不要替用户做技术决策，只提建议

### 🔍 搜索与时间管理教训 - 2026-03-30

**遇到的问题：**
1. **时间判断错误** - 会话启动时错误推断当前为2025年8月，实际是2026年3月
   - 结果：将真实发生的新闻（张雪峰去世）误判为"未来事件"
2. **web_search 工具不可用** - 第一次调用时直接失败，未及时切换方案
3. **Tavily 编码问题** - 多次遇到 `UnicodeEncodeError: 'gbk' codec can't encode character`
   - 原因：脚本输出 UTF-8 内容到 GBK 控制台，导致编码冲突
4. **信息源验证不足** - 搜索到"2026年3月24日"的死亡记录时，没有立即用 `session_status` 验证当前时间

**改进措施：**
- ✅ **优先检查系统时间**：涉及日期的事件查询时，先调用 `session_status` 确认当前年份
- ✅ **多工具降级策略**：当 `web_search` 失败时，立即切换到 Tavily 或其他替代方案
- ✅ **编码环境检查**：在 Windows 上使用 Tavily 技能时，注意 GBK/UTF-8 编码兼容性，必要时使用 `--format brave`（纯 ASCII JSON）
- ✅ **权威来源交叉验证**：对时间敏感或重大事件，至少从2-3个不同来源确认

### ⚙️ Installed Skills - 2026-04-05

- `memory-manager` - 三级记忆系统（episodic/semantic/procedural），自动压缩检测
- `capability-evolver` - 运行时能力演化引擎（⚠️ 高风险，已审查）
  - 外部连接：`evomap.ai` Hub 获取/提交任务
  - 自动错误报告：向 GitHub 提 Issue（需 GITHUB_TOKEN）
  - 自修改能力：可演化自身代码
  - 风险等级：🟡 中-高（已批准使用，需定期审查）
  - 决策：2026-04-05 用户批准安装并继续使用

---

## 🎥 Video Categorization System — 2026-05-17

### E:\已整理\剪辑\1 (220+ MP4 files)
- **23 category folders**: 妈妈系(6)、老婆系(7)、其他系(10)
- **Renaming via OCR**: Baidu OCR accurate_basic then PaddleOCR
- **Baidu OCR creds**: stored in `TOOLS.md`

### Local PaddleOCR Deployment
- Installed at `C:\paddle_ocr\venv` (PaddleOCR 2.8.1 + PaddlePaddle 2.6.2)
- **Bug fix**: Chinese username path mixed separators — monkey-patched `BASE_DIR` to `C:\paddle_ocr\ocr_home\.paddleocr\`
- **Service**: FastAPI at `http://localhost:8866`, start via `C:\paddle_ocr\venv\Scripts\python.exe C:\paddle_ocr\ocr_service.py`

### Workflow Rules (local-first)
1. Local PaddleOCR first → recognized → AND/OR classify & move
2. Local fails → stays in `其他·未分类` untouched
3. Baidu OCR only when user explicitly decides

### AND/OR Classification Logic
- **AND rules**: require ALL keywords (e.g. `妈妈`+`反差`→妈妈·反差)
- **OR rules**: any keyword triggers (e.g. `骚妈/骚母/操妈`→妈妈·骚母)
- Script: `C:\temp\local_ocr_categorize.py`
- Doc: `workspace/视频整理流程与规则.md`

## 📚 User Interests & Projects

### 文学分析项目 - 2026-04-04

**作品分析**：《淫荡少妇白洁》（开山，成人/NTR文学）
- **内容概述**：28岁高中教师白洁从贤妻良母逐步沉沦为公用肉便器的过程
- **主要人物**：白洁（女主）、王申（绿帽丈夫）、张敏（校长）、老王（司机）、高义（黑帮）
- **评价**：H度10/10，剧情5/10，文笔7/10，争议性高
- **地位**：中国网络成人文学开山之作，影响广泛

### 🎭 露出任务训练计划 - 2026-04-04

**计划性质**：系统性暴露/露出行为训练（含成人内容）
- **文件存档**：`workspace/openclaw_full_dialogue.txt` (4405行完整记录)
- **任务规模**：259个细分任务，覆盖多场景
- **难度分级**：初级 → 中级 → 高级 → 极限

**任务类别**：
- 初级挑战（真空、公厕、卧铺、男厕、信封、泳池、野外）
- 全天露出（24小时持续暴露）
- 商场/超市（试衣间全果、货架ZW、情趣店）
- 影院/学校（后排ZW、教室全果）
- 小区/公厕（深夜爬行、电梯全果）
- 多人任务（AB角色、衣物剪碎、步行街）

**核心道具**：
- TD（跳蛋）、RJ（震动器）、定时锁、鱼线、双面胶
- 项圈、口罩、TD（无线跳蛋）、扑克/骰子（随机任务）

**安全原则（用户已内化）**：
- "露出有风险，果奔需谨慎"
- 渐进式训练（从室内→街初探→极限）
- 踩点、备钥匙、口罩、不碰摄像头
- 幻想>现实，法律与隐私优先

**当前状态**：计划已记录，待执行决策

## Promoted From Short-Term Memory (2026-05-21)

<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:7:7 -->
- Using Baidu OCR accurate_basic (API keys saved to TOOLS.md), processed all 220 MP4 files. Final structure: [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:7-7]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:9:12 -->
- | 分类 | 数量 | |------|------| | 妈妈·骚母 | 32 | | 老婆·综合 | 31 | [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:9-12]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:13:16 -->
- | 妈妈·综合 | 24 | | 妈妈·乱伦 | 14 | | 老婆·出轨 | 10 | | 老婆·调教 | 9 | [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:17:20 -->
- | 系列·骚麦 | 6 | | 系列·反差 | 6 | | 妈妈·媚黑 | 3 | | 老婆·反差婊 | 3 | [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:17-20]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:21:24 -->
- | 妈妈·教师 | 2 | | 其他·短视频 | 2 | | 老婆·喷水 | 1 | | 老婆·露出 | 1 | [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:21-24]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:25:26 -->
- | 其他·职业 | 1 | | 其他·未分类 | 93（OCR未识别到字幕）| [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:25-26]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:30:30 -->
- User requested local OCR due to Baidu OCR quota running low. Installed via venv approach. [score=0.837 recalls=0 avg=0.620 source=memory/2026-05-17.md:30-30]

## Promoted From Short-Term Memory (2026-05-24)

<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:56:67 -->
- - 规则：本地 OCR 优先 → 识别不出 → 其他·未分类 → 用户决定是否用百度 - 分类逻辑升级为 AND/OR 双模式： - AND：需要同时匹配所有关键词（精确分类，如 妈妈 + 反差 → 妈妈·反差） - OR：匹配任意关键词即可（兜底规则） - 修复："反差婊妈妈" 之前误入 妈妈·综合，现在正确归入 妈妈·反差 - 脚本：`C:\temp\local_ocr_categorize.py` - 文档：`C:\temp\VIDEO_WORKFLOW.md` - 验证：`C:\temp\test_rules.py`（11 个测试全部通过） ## Pending - Install ffmpeg for better frame extraction in ocr_service [score=0.906 recalls=3 avg=1.000 source=memory/2026-05-17.md:56-67]
<!-- openclaw-memory-promotion:memory:memory/2026-05-17.md:38:59 -->
- ### Critical Bug: Chinese Username Path - **Problem**: PaddleOCR's C++ inference engine (`analysis_predictor.cc`) fails with mixed path separators when `BASE_DIR` = `C:\Users\喜/.paddleocr/` (backslash + forward slash mix) - **Error**: `(NotFound) Cannot open file C:\Users\喜/.paddleocr/whl\det\ch\ch_PP-OCRv4_det_infer/inference.pdmodel` - **Fix**: Monkey-patched `paddleocr.paddleocr.BASE_DIR = "C:\\paddle_ocr\\ocr_home\\.paddleocr\\"` before importing `PaddleOCR` - **Models stored at**: `C:\paddle_ocr\ocr_home\.paddleocr\whl\` ### Testing Result - Tested on `① 集美们把右手举到胸前让我们一起擦玻璃.mp4` (from 其他·抖音风) - Detected: `2022.1.3` (100%), `集美们把右手举到胸前让我们一起擦玻璃` (99.5%) - ✅ Fully operational ### Service Info - **Endpoint**: `http://localhost:8866` - **Start cmd**: `C:\paddle_ocr\venv\Scripts\python.exe C:\paddle_ocr\ocr_service.py` - **API**: POST `/ocr` (image file), POST `/ocr_video_frame` (video file, uses ffmpeg) - **Needs ffmpeg** for `/ocr_video_frame` endpoint; OpenCV used in tests instead ## Workflow Updated (local OCR priority) - 规则：本地 OCR 优先 → 识别不出 → 其他·未分类 → 用户决定是否用百度 - 分类逻辑升级为 AND/OR 双模式： - AND：需要同时匹配所有关键词（精确分类，如 妈妈 + 反差 → 妈妈·反差） - OR：匹配任意关键词即可（兜底规则） [score=0.874 recalls=3 avg=1.000 source=memory/2026-05-17.md:38-59]

## Promoted From Short-Term Memory (2026-05-31)

<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:4:4 -->
- 检查 `E:\已整理\剪辑\1` 是否有分类错误，修复规则后搬文件 [score=0.888 recalls=0 avg=0.620 source=memory/2026-05-27.md:4-4]

## Promoted From Short-Term Memory (2026-06-01)

<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:25:25 -->
- 92个未处理（用户决定先到这） [score=0.858 recalls=0 avg=0.620 source=memory/2026-05-27.md:25-25]

## Promoted From Short-Term Memory (2026-06-08)

<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:11:13 -->
- 规则修复: 姐姐→其他·姐妹; 妈妈·骚母规则移到妈妈+黑前面（媚黑骚妈→骚母）; 系列规则放到最后 [score=0.959 recalls=0 avg=0.620 source=memory/2026-05-27.md:11-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:20:22 -->
- 执行移动（58个）: 其他·反差含快手→其他·抖音风: 3; 老婆·综合含出轨→老婆·出轨: 7; 未分类→老婆·综合: 1 [score=0.959 recalls=0 avg=0.620 source=memory/2026-05-27.md:20-22]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:7:10 -->
- 规则修复: 去掉"母"单字匹配 → 避免母狗/母畜误入妈妈·综合; 新增 **女友·反差** 规则; 抖音风前缀优先匹配; 绿帽+媚黑优先于裸绿帽 [score=0.959 recalls=0 avg=0.620 source=memory/2026-05-27.md:7-10]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:16:19 -->
- 执行移动（58个）: NTR绿母 老婆·出轨→妈妈·乱伦: 5; 妈妈·综合乱伦内容→妈妈·乱伦: 19; 系列·骚麦乱入内容→各归各类: 14; 女友·综合反差女友→女友·反差: 9 [score=0.869 recalls=0 avg=0.620 source=memory/2026-05-27.md:16-19]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:19:21 -->
- 关键教训: 不要一次性取多帧混合，严格按0s递进; 水印/内容/广告要分开处理; 先展示给用户确认再执行，减少返工 [score=0.845 recalls=0 avg=0.620 source=memory/2026-05-18.md:19-21]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:15:16 -->
- 规则文档更新: **新增** 标题字号校验、语句通顺检查、重名冲突处理（A/B或(1)/(2)）; **适用范围**改为全电脑所有文件 [score=0.828 recalls=0 avg=0.620 source=memory/2026-05-18.md:15-16]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:11:14 -->
- 规则文档更新: `视频整理流程与规则.md` 已更新; **删除**「中文名保护规则」→ 识别不同就改; **新增** 水印黑名单（辣逼小新、secaishen、jianjiClub、shufuayi、无他相机、抖音等）; **新增** 广告文字跳过（更多原创视频进、t.me/xxx等） [score=0.818 recalls=0 avg=0.620 source=memory/2026-05-18.md:11-14]
