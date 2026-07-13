import os
key = os.environ.get("TAVILY_API_KEY")
print(f"TAVILY_API_KEY from env: {key}")
if not key:
    print("Key not found in environment")
else:
    print(f"Key length: {len(key)}")
    print(f"First 10 chars: {key[:10]}...")