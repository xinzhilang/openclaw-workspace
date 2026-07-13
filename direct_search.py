import os
import sys

# Add the scripts directory to path so we can import the tavily search module
scripts_path = r"C:\Users\喜\.openclaw\workspace\skills\openclaw-tavily-search\scripts"
sys.path.insert(0, scripts_path)

# Set the API key
os.environ["TAVILY_API_KEY"] = "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"

# Import and run the search
from tavily_search import tavily_search, to_markdown
import argparse

# Create a mock args object
class Args:
    def __init__(self):
        self.query = "free translation model openrouter"
        self.max_results = 10
        self.include_answer = False
        self.search_depth = "basic"
        self.format = "md"

args = Args()

# Perform the search
res = tavily_search(
    query=args.query,
    max_results=max(1, min(args.max_results, 10)),
    include_answer=args.include_answer,
    search_depth=args.search_depth,
)

# Convert to markdown and write to file to avoid encoding issues
if args.format == "md":
    result_text = to_markdown(res)
    with open("C:\\Users\\喜\\.openclaw\\workspace\\search_results.md", "w", encoding="utf-8") as f:
        f.write(result_text)
    print("Search results written to search_results.md")
else:
    # For other formats, just print JSON (should be ASCII safe)
    import json
    if args.format == "brave":
        # Convert to brave format
        results = []
        for r in res.get("results", []) or []:
            results.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "snippet": r.get("content"),
            })
        out = {"query": res.get("query"), "results": results}
        if "answer" in res:
            out["answer"] = res.get("answer")
        res = out
    
    print(json.dumps(res, ensure_ascii=False, indent=2))