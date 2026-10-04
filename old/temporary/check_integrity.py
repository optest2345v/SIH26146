import re
import os

with open('src/dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all onclick handlers
onclicks = re.findall(r'onclick=[\'"]([^\'"]+)[\'"]', content)
print(f"Total onclick handlers in HTML: {len(onclicks)}")

# Find all function definitions in script
funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', content))
funcs.update(re.findall(r'async\s+function\s+([a-zA-Z0-9_]+)\s*\(', content))
print(f"Defined functions in script: {len(funcs)}")

# Check which called functions might be missing
called_funcs = set()
for oc in onclicks:
    # may have multiple statements separated by semicolon
    statements = oc.split(';')
    for stmt in statements:
        m = re.search(r'([a-zA-Z0-9_]+)\s*\(', stmt.strip())
        if m:
            called_funcs.add(m.group(1))

builtin_or_dom = {'alert', 'print', 'close', 'focus', 'click'}
missing = [cf for cf in called_funcs if cf not in funcs and cf not in builtin_or_dom]
print("Missing onclick functions:", missing)

# Check API endpoints called in index.html vs endpoints defined in server.py
fe_fetch_endpoints = set(re.findall(r'fetch\([`\'"]([^`\'"?]+)', content))
print(f"\nFrontend fetch endpoints found: {len(fe_fetch_endpoints)}")
for ep in sorted(fe_fetch_endpoints):
    print("  FE:", ep)

with open('src/api/server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

be_endpoints = set(re.findall(r'@app\.(?:get|post|put|delete)\([\'"]([^\'"]+)', server_code))
print(f"\nBackend defined endpoints found: {len(be_endpoints)}")
for ep in sorted(be_endpoints):
    print("  BE:", ep)
