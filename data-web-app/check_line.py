with open('static/js/events.js', 'r') as f:
    lines = f.readlines()
    for i in range(152, 158):
        print(f'{i+1}: {lines[i][:100]}')
