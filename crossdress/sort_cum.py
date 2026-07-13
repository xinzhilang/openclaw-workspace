import subprocess, json, re, os

# First fetch data from Stash API
query = {
    "query": """query FindScenes($filter: FindFilterType!, $scene_filter: SceneFilterType!) {
        findScenes(filter: $filter, scene_filter: $scene_filter) {
            count
            scenes {
                id
                title
                details
                date
            }
        }
    }""",
    "variables": {
        "filter": {"per_page": 200, "sort": "date", "direction": "DESC"},
        "scene_filter": {"tags": {"value": ["2287", "2286", "2285"], "modifier": "INCLUDES", "depth": 0}}
    }
}

query_file = os.path.join(os.environ['TEMP'], 'sgql.json')
with open(query_file, 'w', encoding='utf-8') as f:
    json.dump(query, f)

result = subprocess.run(
    ['curl.exe', '-s', '-X', 'POST', 'http://localhost:9999/graphql',
     '-H', 'Content-Type: application/json',
     '-d', f'@{query_file}'],
    capture_output=True
)
stdout = result.stdout.decode('utf-8', errors='replace')

data = json.loads(stdout)
scenes = data['data']['findScenes']['scenes']

# Extract numbers from titles
def extract_loads(title):
    patterns = [
        r'swallows?\s+(\d+)\s+(?:big|huge|mouthful|cum)',
        r'(\d+)\s+(?:big|huge|mouthful)\s+loads?',
        r'(\d+)\s+cum\s+loads?',
    ]
    for p in patterns:
        m = re.search(p, title, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None

entries = []
for s in scenes:
    n = extract_loads(s['title'])
    if n and n > 0:
        entries.append((n, s['id'], s['title'][:80], s['date']))

entries.sort(key=lambda x: -x[0])

print(f"\n{'='*100}")
print(f"  吞精数量排行榜 (共 {len(entries)} 部)")
print(f"{'='*100}")
print(f"{'#':>3}  {'数量':>5}  {'日期':<12}  {'标题'}")
print(f"{'-'*3}  {'-'*5}  {'-'*12}  {'-'*70}")
for i, (n, sid, title, date) in enumerate(entries, 1):
    print(f"{i:>3}  {n:>5}  {date:<12}  {title}")
print(f"{'='*100}")

# Also print the top links
print(f"\n🎬 直接打开链接播放：")
for i, (n, sid, title, date) in enumerate(entries[:10], 1):
    print(f"  #{i} ({n}发): http://localhost:9999/scenes/{sid}")
