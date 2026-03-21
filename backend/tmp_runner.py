from app.services.scanner_service import run_scan
sample = """
query = "SELECT * FROM users WHERE username = '" + user + "' AND password = '" + pwd + "'"
import os
os.system('rm ' + filename)
"""
res = run_scan('test.py', sample)
print('findings', len(res['vulnerabilities']))
for f in res['vulnerabilities']:
    print(f['name'], f['severity'], f['line_number'], f['code_snippet'])
print('summary', res['summary'])
