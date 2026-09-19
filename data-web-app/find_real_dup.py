#!/usr/bin/env python
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Le début du fichier
start_marker = '/* ============================================\n   Road - Travel Management Application\n   Station F Vibe Design\n   ============================================ */'

# Trouver toutes les occurrences
first = content.find(start_marker)
second = content.find(start_marker, first + 1)

if second > 0:
    print(f'Duplication détectée !')
    print(f'Première occurrence: position {first}')
    print(f'Deuxième occurrence: position {second}')
    print(f'Taille avant duplication: {second} octets')
    
    # Extraire la partie avant la duplication
    clean_content = content[:second]
    print(f'\nTaille du contenu propre: {len(clean_content)} octets')
else:
    print('Pas de duplication détectée')
