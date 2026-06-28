#!/usr/bin/env python
"""
Enhanced i18n audit and patch generator.
- Scans all translatable strings from templates and Python files
- Reports on template completeness
- Generates patched django.po with placeholders for missing translations
"""
import os
import re
import csv
from collections import defaultdict

PO_PATH = os.path.join('locale', 'sw', 'LC_MESSAGES', 'django.po')
REPORT_CSV = os.path.join('reports', 'i18n_template_audit.csv')
REPORT_MD = os.path.join('reports', 'i18n_template_audit_details.md')
PATCHED_PO = os.path.join('locale', 'sw', 'LC_MESSAGES', 'django_patched.po')

if not os.path.exists(PO_PATH):
    print('PO file not found:', PO_PATH)
    raise SystemExit(1)

# Read the PO file
with open(PO_PATH, 'r', encoding='utf-8') as f:
    po_text = f.read()

# Parse PO entries
entries = re.split(r'\n\n(?=(?:#[:~,].*|msgid))', po_text)

po_data = {}  # {msgid: {msgstr, fuzzy, locations}}

for block in entries:
    if 'msgid' not in block:
        continue
    
    fuzzy = '#, fuzzy' in block
    m_msgid = re.search(r"msgid\s+((?:\".*?\"(?:\n|\s)?)*)", block, re.S)
    m_msgstr = re.search(r"msgstr\s+((?:\".*?\"(?:\n|\s)?)*)", block, re.S)
    
    if not m_msgid or not m_msgstr:
        continue
    
    def unquote(s):
        parts = re.findall(r'\"(.*?)\"', s, re.S)
        return ''.join(parts).strip()
    
    msgid = unquote(m_msgid.group(1))
    msgstr = unquote(m_msgstr.group(1))
    
    # Gather locations
    locations = []
    for line in block.splitlines():
        if line.startswith('#:'):
            locations.append(line[2:].strip())
    
    if msgid:  # Skip header
        po_data[msgid] = {
            'msgstr': msgstr,
            'fuzzy': fuzzy,
            'locations': locations,
            'block': block
        }

# Collect stats per template
template_stats = defaultdict(lambda: {'total': 0, 'translated': 0, 'fuzzy': 0, 'missing': 0, 'missing_list': []})

for msgid, data in po_data.items():
    if not msgid:  # Skip header
        continue
    
    for loc in data['locations']:
        # Extract template path
        if 'templates' in loc or '.py' in loc:
            # Normalize: remove line numbers
            loc_clean = re.sub(r':\d+', '', loc).strip()
            loc_clean = loc_clean.replace('\\', '/').lstrip('./')
            
            # Get template or file name
            if 'templates' in loc_clean:
                idx = loc_clean.find('templates')
                key = loc_clean[idx:]
            else:
                key = loc_clean
            
            s = template_stats[key]
            s['total'] += 1
            
            if data['fuzzy']:
                s['fuzzy'] += 1
            
            if data['msgstr'] == '':
                s['missing'] += 1
                s['missing_list'].append(msgid)
            else:
                s['translated'] += 1

# Add templates with zero entries
if os.path.exists('templates'):
    for root, dirs, files in os.walk('templates'):
        for fn in files:
            if fn.endswith('.html'):
                p = os.path.join(root, fn).replace('\\', '/')
                if p not in template_stats:
                    template_stats[p] = {'total': 0, 'translated': 0, 'fuzzy': 0, 'missing': 0, 'missing_list': []}

# Write CSV summary
os.makedirs('reports', exist_ok=True)
with open(REPORT_CSV, 'w', encoding='utf-8', newline='') as csvf:
    writer = csv.writer(csvf)
    writer.writerow(['template', 'total_entries', 'translated', 'fuzzy', 'missing', 'percent_translated'])
    for tpl, s in sorted(template_stats.items()):
        total = s['total']
        translated = s['translated']
        fuzzy = s['fuzzy']
        missing = s['missing']
        pct = (translated / total * 100) if total > 0 else (100 if translated > 0 else 0)
        writer.writerow([tpl, total, translated, fuzzy, missing, f"{pct:.1f}"])

# Write detailed markdown
with open(REPORT_MD, 'w', encoding='utf-8') as md:
    md.write('# i18n Template Audit (Swahili)\n\n')
    md.write(f'PO file: {PO_PATH}\n\n')
    md.write('## Summary\n\n')
    total_entries = sum(s['total'] for s in template_stats.values())
    total_translated = sum(s['translated'] for s in template_stats.values())
    total_fuzzy = sum(s['fuzzy'] for s in template_stats.values())
    total_missing = sum(s['missing'] for s in template_stats.values())
    overall_pct = (total_translated / total_entries * 100) if total_entries > 0 else 0
    
    md.write(f'- **Total entries**: {total_entries}\n')
    md.write(f'- **Translated**: {total_translated}\n')
    md.write(f'- **Fuzzy**: {total_fuzzy}\n')
    md.write(f'- **Missing**: {total_missing}\n')
    md.write(f'- **Overall completion**: {overall_pct:.1f}%\n\n')
    
    md.write('## By Template\n\n')
    md.write('| Template | Total | Translated | Fuzzy | Missing | % Translated |\n')
    md.write('|---|---:|---:|---:|---:|---:|\n')
    for tpl, s in sorted(template_stats.items()):
        total = s['total']
        translated = s['translated']
        fuzzy = s['fuzzy']
        missing = s['missing']
        pct = (translated / total * 100) if total > 0 else (100 if translated > 0 else 0)
        md.write(f'| {tpl} | {total} | {translated} | {fuzzy} | {missing} | {pct:.1f}% |\n')
    
    md.write('\n## Missing strings by template\n\n')
    for tpl, s in sorted(template_stats.items()):
        if s['missing'] > 0:
            md.write(f'### {tpl}\n\n')
            for msg in s['missing_list'][:50]:
                md.write(f'- {msg}\n')
            if len(s['missing_list']) > 50:
                md.write(f'- ...and {len(s["missing_list"]) - 50} more\n')
            md.write('\n')

print('Reports generated:')
print(f'  CSV: {REPORT_CSV}')
print(f'  Markdown: {REPORT_MD}')
print(f'  Total entries: {total_entries}')
print(f'  Translated: {total_translated} ({overall_pct:.1f}%)')
print(f'  Missing: {total_missing}')
print(f'  Fuzzy: {total_fuzzy}')

# Now generate patched PO with placeholders for missing entries
# Find all msgids that have empty msgstr and add placeholder translations

header_match = re.search(r'^(.*?)\n\nmsgid', po_text, re.DOTALL)
header = header_match.group(1) if header_match else ''

# Build patched PO
patched_lines = [header, '\n\n']

for msgid in sorted(po_data.keys()):
    data = po_data[msgid]
    
    if not msgid:  # Skip header entry
        continue
    
    block = data['block']
    msgstr = data['msgstr']
    
    # If msgstr is empty, add placeholder
    if msgstr == '':
        # Replace the empty msgstr with a placeholder (use original msgid in brackets)
        block = re.sub(
            r'msgstr\s+""\n',
            f'msgstr "[PENDING: {msgid[:50]}...]"\n',
            block
        )
    
    patched_lines.append(block)
    patched_lines.append('\n')

patched_po_content = ''.join(patched_lines)

os.makedirs(os.path.dirname(PATCHED_PO), exist_ok=True)
with open(PATCHED_PO, 'w', encoding='utf-8') as f:
    f.write(patched_po_content)

print(f'\nPatched PO generated: {PATCHED_PO}')
print(f'  (Empty msgstr entries marked with [PENDING: ...] placeholder)')
