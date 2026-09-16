#!/usr/bin/env python
# Script to fix the duplicated CSS file

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the duplication starts
# The file should start with "/* ============================================"
start_marker = '/* ============================================'
first = content.find(start_marker)
second = content.find(start_marker, first + 1)

if second > 0:
    print(f'Duplication detected at position {second}')
    # Keep only the first part
    clean_content = content[:second]
    
    # Write back
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print(f'Fixed! File reduced from {len(content)} to {len(clean_content)} bytes')
else:
    print('No duplication found')
