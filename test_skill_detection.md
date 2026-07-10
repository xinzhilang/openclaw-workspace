# Testing Automatic Skill Detection

When the user says: "请帮我搜索一下最新的AI模型信息"
(The request is about searching for AI model information)

The system should:
1. Detect keywords: "搜索" (search), "AI模型" (AI models)
2. Match to skills: `openclaw-tavily-search` (score: 10), `multi-search-engine-simple` (score: 5)
3. Recommend: "建议使用 openclaw-tavily-search 进行网络搜索"
4. Auto-invoke if accepted

Current installed skills in workspace/skills/:
- adaptive-reasoning
- agent-browser-clawdbot  
- capability-evolver
- claw-swarm
- find-skills-skill
- memory-manager
- multi-search-engine-simple
- openclaw-tavily-search ← Most relevant for search tasks
- pdf-smart-tool-cn
- proactive-agent-lite
- ralph-evolver
- shell
- skill-vetter
- summarize-pro
- word-docx
- xiucheng-self-improving-agent
