import re
import subprocess

html = open('d:/sadhana UNI/Documents/GitHub/Focus_Fighter/templates/index.html', encoding='utf-8').read()
matches = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)

for i, js in enumerate(matches):
    with open(f'test_{i}.js', 'w', encoding='utf-8') as f:
        f.write(js)
    
    print(f"--- Testing Script {i} ---")
    proc = subprocess.run(['node', '-c', f'test_{i}.js'], capture_output=True, text=True, shell=True)
    print("STDOUT:", proc.stdout)
    print("STDERR:", proc.stderr)
