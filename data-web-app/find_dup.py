#!/usr/bin/env python
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver toutes les lignes qui commencent par '/* ===='
occurrences = []
for i, line in enumerate(lines):
    if line.strip().startswith('/* ==='):
        occurrences.append(i)

print(f'Occurrences de "/* ===" trouvées aux lignes: {occurrences}')

if len(occurrences) > 1:
    print(f'\nDuplication détectée !')
    print(f'Première occurrence: ligne {occurrences[0] + 1}')
    print(f'Deuxième occurrence: ligne {occurrences[1] + 1}')
    print(f'\nContenu à la ligne {occurrences[1] + 1}: {repr(lines[occurrences[1]][:80])}')
