#!/usr/bin/env python3
"""Script to restore the clean CSS from the broken file."""

# Read the broken CSS file
with open('static/css/style.css.broken', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the clean CSS (after the conflict markers)
# The clean CSS starts with the header comment
start_marker = "/* ============================================\n   Road - Travel Management Application"
start_index = content.find(start_marker)

if start_index == -1:
    # Try alternative search
    start_marker = "Road - Travel Management Application"
    start_index = content.find(start_marker)
    if start_index == -1:
        print("Could not find start marker!")
        exit(1)
    # Go back to the beginning of the line (look for the comment start)
    prev_newline = content.rfind('\n', 0, start_index)
    if prev_newline != -1 and prev_newline > 0:
        start_index = prev_newline + 1
    else:
        start_index = 0

clean_css = content[start_index:]

# Also check if there's duplicate content at the end
# The clean CSS should end with the button user-select none
end_marker = "button {\n    user-select: none;\n}"
end_index = clean_css.rfind(end_marker)
if end_index != -1:
    # Add a bit more to be safe
    end_index += len(end_marker)
    clean_css = clean_css[:end_index]

# Write the clean CSS to style.css
with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(clean_css)

print(f"CSS file restored! Wrote {len(clean_css)} bytes to style.css")
