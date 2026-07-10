import subprocess, sys, os

# Check if port is in use
os.system('netstat -ano | findstr :18792')

# Try to run server
try:
    p = subprocess.run([sys.executable, 'relay-minimal.py'], timeout=5, capture_output=True, text=True)
    print('STDOUT:', p.stdout)
    print('\n--- STDERR ---')
    print(p.stderr)
except subprocess.TimeoutExpired as e:
    print('Server started successfully (timeout as expected)')
    print('Output:', e.stdout[:500] if e.stdout else 'none')
    print('Error:', e.stderr[:500] if e.stderr else 'none')
except Exception as e:
    print('Error:', e)
