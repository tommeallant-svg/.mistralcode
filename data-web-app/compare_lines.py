#!/usr/bin/env python
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== Premières 10 lignes ===')
for i in range(10):
    print(f'{i+1:4d}: {lines[i][:100]}')

print('\n=== Lignes 1840-1849 ===')
for i in range(1839, 1849):
    print(f'{i+1:4d}: {lines[i][:100]}')

print('\n=== Lignes 1850-1859 ===')
for i in range(1849, min(1859, len(lines))):
    print(f'{i+1:4d}: {lines[i][:100]}')
