
import os, json

skills_dir = 'C:/Users/ϲ/.openclaw/workspace/skills'

for skill_name in os.listdir(skills_dir):
    skill_path = os.path.join(skills_dir, skill_name)
    if os.path.isdir(skill_path):
        print(skill_name + ':')
        files = os.listdir(skill_path)
        for f in files:
            print('  - ' + f)
        print()
