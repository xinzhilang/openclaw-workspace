import subprocess, json, sys

tab = '5208A402254AADC04A9A9D45EA942C7F'

# Search for gangbang on scenes page
result = subprocess.run(['browser-relay', 'snapshot', '--tab', tab, '--max-length', '3000'],
                       capture_output=True, text=True, timeout=10)
text = result.stdout
if 'gangbang' in text.lower() or 'Gangbang' in text:
    print("Gangbang found in results!")
else:
    print("No gangbang in results")
    
# Show some scene titles
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'link' in line and ('gangbang' in line.lower() or 'Gangbang' in line.lower() or 'Orgy' in line or 'orgy' in line.lower() or 'DP' in line or 'double' in line.lower()):
        print(f"  {line.strip()}")
    if 'button' in line and ('gangbang' in line.lower() or 'Gangbang' in line):
        print(f"  {line.strip()}")
