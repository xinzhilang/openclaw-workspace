# Automatic Skill Detection & Routing

## Overview

The assistant now automatically detects when a task would benefit from an installed OpenClaw skill and recommends its use with proper invocation patterns.

## How It Works

### 1. Skill Discovery

On startup, the assistant scans `workspace/skills/` for installed skills:

```bash
workspace/skills/
├── adaptive-reasoning/
├── agent-browser-clawdbot/
├── capability-evolver/
├── claw-swarm/
├── find-skills-skill/
├── memory-manager/
├── multi-search-engine-simple/
├── openclaw-tavily-search/
├── pdf-smart-tool-cn/
├── proactive-agent-lite/
├── ralph-evolver/
├── shell/
├── skill-vetter/
├── summarize-pro/
├── word-docx/
└── xiucheng-self-improving-agent/
```

### 2. Task Matching

When you describe a task, the system matches keywords to installed skills:

| Task Keywords | Matched Skill | Match Score |
|---------------|---------------|-------------|
| "search web", "find info" | `openclaw-tavily-search`, `multi-search-engine-simple` | 5-10 |
| "summarize", "summary" | `summarize-pro` | 10 |
| "PDF", "convert PDF" | `pdf-smart-tool-cn` | 10 |
| "Word", "docx", "edit document" | `word-docx` | 10 |
| "browser", "automate browser" | `agent-browser-clawdbot` | 10 |
| "memory", "remember" | `memory-manager` | 10 |
| "skill", "find skills" | `find-skills-skill`, `skill-vetter` | 5-10 |
| "swarm", "multi-agent" | `claw-swarm` | 10 |
| "adapt", "reasoning level" | `adaptive-reasoning` | 5 |
| "shell", "run command", "terminal" | `shell` | 10 |
| "evolve", "self-improve" | `capability-evolver`, `ralph-evolver` | 5 |
| "proactive" | `proactive-agent-lite` | 5 |

### 3. Recommendation Output

When a match is found, the assistant provides:

```
🤖 **技能自动推荐**
任务: "搜索最新的AI技术新闻"

推荐使用的技能:
1. **openclaw-tavily-search** (匹配度: 10/10)
   Web搜索工具
   可用工具: SKILL:openclaw-tavily-search

2. **multi-search-engine-simple** (匹配度: 5/10)
   多种搜索引擎
   可用工具: SKILL:multi-search-engine-simple

💡 提示: 使用 `sessions_spawn` + `runtime="acp"` 调用这些技能
   或直接使用对应的工具调用指令
```

## Usage Patterns

### Pattern 1: Accept Recommendation (Implicit)

Simply state your task naturally:

**You**: "请帮我搜索一下OpenRouter上有哪些免费的模型"

**Assistant**: Uses `openclaw-tavily-search` automatically to fulfill the request

### Pattern 2: Explicit Skill Invocation

**You**: "请用tavily搜索来查找..."

The assistant will:
1. Detect the explicit skill request
2. Use `sessions_spawn` with `runtime="acp"` 
3. Route to the `openclaw-tavily-search` skill
4. Return results

### Pattern 3: Direct Tool Call

If you want to use a specific tool from a skill:

**You**: "用pdf-smart-tool-cn转换这个PDF"

The assistant will invoke the PDF tool directly.

### Pattern 4: Swarm/Group Tasks

**You**: "帮我用claw-swarm分析一下这个复杂问题"

The assistant will:
1. Spawn a `claw-swarm` session
2. Distribute work across multiple agents
3. Aggregate results

## Available Skills & Their Purposes

### Information Retrieval
- **openclaw-tavily-search** - Web search with content extraction
- **multi-search-engine-simple** - Multiple Chinese search engines
- **agent-browser-clawdbot** - Headless browser automation

### Document Processing
- **pdf-smart-tool-cn** - PDF conversion, OCR, merge, split, watermark
- **word-docx** - Word document creation and editing with styles

### Knowledge Management
- **memory-manager** - Local memory with compression detection
- **summarize-pro** - 20-format summarizer (TL;DR, ELI5, bullet points)

### Code & Automation
- **shell** - Shell scripting and command execution
- **claw-swarm** - Multi-agent collaboration
- **find-skills-skill** - Discover available skills

### AI Enhancement
- **adaptive-reasoning** - Auto-assess task complexity
- **proactive-agent-lite** - Proactive assistance with memory
- **capability-evolver** - Self-improvement engine
- **ralph-evolver** - Recursive self-improvement

### Quality & Security
- **skill-vetter** - Security-first skill vetting
- **xiucheng-self-improving-agent** - Response quality optimization

## ACP Harness Integration

Skills are invoked via the ACP (Agent Communication Protocol) harness:

```json
{
  "runtime": "acp",
  "agentId": "openclaw-tavily-search",
  "task": "搜索OpenRouter免费模型",
  "context": "从之前的对话中提取需求"
}
```

For thread-bound persistent sessions:
```json
{
  "thread": true,
  "mode": "session"
}
```

## Best Practices

1. **Natural Language First**: Describe what you want to achieve, not how
2. **Explicit When Important**: If a specific tool is critical, mention it
3. **Let the System Choose**: The router considers context, tools available, and task complexity
4. **Review Recommendations**: You can always ask "为什么推荐这个技能？" to understand the reasoning

## Configuration

The auto-detection runs automatically. To customize:

- **Disable**: Set `"autoSkillDetection": false` in user preferences
- **Adjust Thresholds**: Modify match score thresholds in `auto_skill_router.py`
- **Add Custom Skills**: Place in `workspace/skills/` with proper `SKILL.md`

## Troubleshooting

**Skill not detected?**
- Ensure it's in `workspace/skills/`
- Check for `SKILL.md` file
- Verify it's properly installed

**Wrong skill chosen?**
- Be more explicit in your request
- Mention the specific skill name
- Provide more context

**Performance concerns?**
- Skill discovery only runs once per session
- Matching uses simple keyword scoring (fast)
- No external API calls for routing
