#!/usr/bin/env python
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Total lines:', len(lines))
print('First line:', repr(lines[0][:80]))
print('Line 1850:', repr(lines[1849][:80]))
