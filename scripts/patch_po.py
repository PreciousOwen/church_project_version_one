#!/usr/bin/env python
"""
Proper PO patcher that handles multi-line msgstr entries.
"""
import os
import re

PO_PATH = os.path.join('locale', 'sw', 'LC_MESSAGES', 'django.po')
PATCHED_PO = os.path.join('locale', 'sw', 'LC_MESSAGES', 'django_patched.po')

if not os.path.exists(PO_PATH):
    print(f'PO file not found: {PO_PATH}')
    raise SystemExit(1)

with open(PO_PATH, 'r', encoding='utf-8') as f:
    po_text = f.read()

# Read PO and find all entries
lines = po_text.split('\n')
patched_lines = []
i = 0
pending_count = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is the start of a msgstr
    if line.startswith('msgstr '):
        # Collect the full msgstr (handle multi-line strings)
        msgstr_full = [line]
        j = i + 1
        while j < len(lines) and lines[j].startswith('"'):
            msgstr_full.append(lines[j])
            j += 1
        
        # Check if msgstr is empty
        msgstr_text = ' '.join(msgstr_full)
        if re.search(r'msgstr\s+(?:""(?:\s*""\s*)*)\s*$', msgstr_text.replace('\n', ' ')):
            # This is an empty msgstr - find the corresponding msgid
            # Look backwards for msgid
            msgid = "[PENDING]"
            for k in range(i - 1, max(0, i - 10), -1):
                if lines[k].startswith('msgid '):
                    msgid_match = re.search(r'msgid\s+"([^"]*)"', lines[k])
                    if msgid_match:
                        msgid = msgid_match.group(1)[:50]
                    break
            
            # Replace with placeholder
            patched_lines.append(f'msgstr "[PENDING TRANSLATION] {msgid}..."')
            pending_count += 1
            i = j
        else:
            # msgstr is not empty, keep as is
            patched_lines.extend(msgstr_full)
            i = j
    else:
        patched_lines.append(line)
        i += 1

# Write patched file
os.makedirs(os.path.dirname(PATCHED_PO), exist_ok=True)
patched_content = '\n'.join(patched_lines)
with open(PATCHED_PO, 'w', encoding='utf-8') as f:
    f.write(patched_content)

print(f'✓ Patched PO file: {PATCHED_PO}')
print(f'  - Entries with pending placeholders: {pending_count}')
print(f'\nTo use the patched file:')
print(f'  1. Backup original: cp locale\\sw\\LC_MESSAGES\\django.po locale\\sw\\LC_MESSAGES\\django.po.bak')
print(f'  2. Copy patched: cp locale\\sw\\LC_MESSAGES\\django_patched.po locale\\sw\\LC_MESSAGES\\django.po')
print(f'  3. Compile: python manage.py compilemessages -l sw')
