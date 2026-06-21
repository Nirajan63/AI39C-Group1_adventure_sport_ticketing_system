import re

content = open('app/static/js/dashboard_Admin.js', encoding='utf-8').read()
for line in content.splitlines():
    if 'fetch(' in line or 'url:' in line:
        print(line.strip())
