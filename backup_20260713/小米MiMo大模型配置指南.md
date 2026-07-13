# 小米 MiMo 大模型配置指南

> 适用于 OpenClaw 接入小米 MiMo-V2.5 系列模型

---

## 前置条件

- 已安装 OpenClaw（`npm install -g openclaw`）
- 已完成 OpenClaw 初始配置（`openclaw configure`）
- 小米 MiMo API Key（从 https://mimo.mi.com 获取）

---

## 第一步：获取 API Key

1. 访问 https://mimo.mi.com
2. 注册/登录账号
3. 进入控制台，创建 API Key
4. 保存好 Key，后面要用

---

## 第二步：配置 OpenClaw 接入小米模型

编辑 OpenClaw 配置文件：

```
C:\Users\<你的用户名>\.openclaw\openclaw.json
```

### 2.1 添加认证配置

在 `auth.profiles` 中添加小米的认证：

```json
"auth": {
  "profiles": {
    "xiaomi:default": {
      "provider": "xiaomi",
      "mode": "api_key"
    }
  }
}
```

### 2.2 添加模型提供商配置

在 `models.providers` 中添加小米：

```json
"models": {
  "mode": "replace",
  "providers": {
    "xiaomi": {
      "baseUrl": "https://api.xiaomimimo.com/v1",
      "api": "openai-completions",
      "models": [
        {
          "id": "mimo-v2.5-pro",
          "name": "Xiaomi MiMo V2.5 Pro",
          "reasoning": true,
          "input": ["text"],
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          },
          "contextWindow": 262144,
          "maxTokens": 32000,
          "api": "openai-completions"
        },
        {
          "id": "mimo-v2.5",
          "name": "Xiaomi MiMo V2.5",
          "reasoning": true,
          "input": ["text"],
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          },
          "contextWindow": 262144,
          "maxTokens": 32000,
          "api": "openai-completions"
        }
      ],
      "apiKey": "sk-cqsiw6ewknz2a5egrg7wn5a5dnkhrmlutitnofkr3x9kwjrp"
    }
  }
}
```

> ⚠️ **关键**：两个模型的 `reasoning` 都要设为 `true`，否则无法使用推理/思考功能。

### 2.3 添加到可用模型列表

在 `agents.defaults.models` 中注册：

```json
"agents": {
  "defaults": {
    "models": {
      "xiaomi/mimo-v2.5-pro": {},
      "xiaomi/mimo-v2.5": {}
    }
  }
}
```

### 2.4 启用小米插件

在 `plugins.entries` 中确保：

```json
"plugins": {
  "entries": {
    "xiaomi": {
      "enabled": true
    }
  }
}
```

---

## 第三步：重启 Gateway

配置修改后必须重启 Gateway 才能生效：

```powershell
openclaw gateway restart
```

---

## 第四步：验证配置

```powershell
openclaw gateway status
```

确认 `xiaomi` 插件状态为 OK。

---

## 第五步：切换模型

在 OpenClaw 中切换到小米模型：

```
/model xiaomi/mimo-v2.5
```

或使用别名（如果配置了的话）：

```
/model MiMo
```

---

## ⚠️ 常见问题

### Q1: 设置推理等级时报错 `thinkingLevel "high" is not supported`

**原因**：`mimo-v2.5` 的 `reasoning` 被设为 `false`。

**解决**：在配置文件中将对应模型的 `reasoning` 改为 `true`，然后重启 Gateway。

### Q2: MiMo 的 thinking 参数和 OpenAI 标准不一样

MiMo 使用自己的参数体系：

| 参数 | 值 |
|------|-----|
| MiMo 原生 | `thinking.type`: `enabled` / `disabled` |
| OpenAI 标准 | `reasoning_effort`: off / low / medium / high |

OpenClaw 内部会做映射，通常 `reasoning: true` + `thinkingLevel` 即可正常工作。

### Q3: 配置文件在哪

Windows 路径：
```
C:\Users\<用户名>\.openclaw\openclaw.json
```

macOS/Linux 路径：
```
~/.openclaw/openclaw.json
```

---

## 模型价格参考（2026年7月）

| 模型 | 输入（缓存命中） | 输入（缓存未命中） | 输出 |
|------|------------------|-------------------|------|
| MiMo-V2.5 | ¥0.02/M tokens | ¥1/M tokens | ¥2/M tokens |
| MiMo-V2.5-Pro | ¥0.025/M tokens | ¥3/M tokens | ¥6/M tokens |

---

*最后更新：2026-07-01*
