import os
import re
import csv

PO_PATH = os.path.join('locale','sw','LC_MESSAGES','django.po')
REPORT_CSV = os.path.join('reports','i18n_template_audit.csv')
REPORT_MD = os.path.join('reports','i18n_template_audit_details.md')

if not os.path.exists(PO_PATH):
    print('PO file not found:', PO_PATH)
    raise SystemExit(1)

with open(PO_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Split into entries by two newlines followed by a msgid or by EOF
entries = re.split(r'\n\n(?=(?:#[:~,].*|msgid))', text)

template_stats = {}  # {template: {'total':int,'translated':int,'fuzzy':int,'missing':int,'missing_list':[]}}

for block in entries:
    if 'msgid' not in block:
        continue
    # detect fuzzy
    fuzzy = '#, fuzzy' in block
    # find msgid
    m_msgid = re.search(r"msgid\s+((?:\".*?\"(?:\n|\s)?)*)", block, re.S)
    m_msgstr = re.search(r"msgstr\s+((?:\".*?\"(?:\n|\s)?)*)", block, re.S)
    if not m_msgid or not m_msgstr:
        continue
    def unquote(s):
        parts = re.findall(r'\"(.*?)\"', s, re.S)
        return ''.join(parts).strip()
    msgid = unquote(m_msgid.group(1))
    msgstr = unquote(m_msgstr.group(1))

    # gather referenced files
    refs = []
    for line in block.splitlines():
        if line.startswith('#:'):
            parts = line[2:].strip().split()
            for p in parts:
                # Normalize path separators and remove leading .\ or ./
                p_norm = p.replace('\\','/').lstrip('./\\')
                # Remove trailing :lineno
                p_norm = re.sub(r':\d+$','',p_norm)
                refs.append(p_norm)
    # For each ref that is a template under templates/, update stats
    for r in refs:
        if '/templates/' in r or r.startswith('templates/'):
            # find the substring starting at templates/
            idx = r.find('templates/')
            tpl = r[idx:]
            # normalize
            tpl = tpl.replace('\\','/').lstrip('./')
            s = template_stats.setdefault(tpl, {'total':0,'translated':0,'fuzzy':0,'missing':0,'missing_list':[]})
            s['total'] += 1
            if fuzzy:
                s['fuzzy'] += 1
            if msgstr == '':
                s['missing'] += 1
                s['missing_list'].append(msgid)
            else:
                s['translated'] += 1

# Also include templates that may have zero entries by scanning templates directory
all_templates = []
if os.path.exists('templates'):
    for root, dirs, files in os.walk('templates'):
        for fn in files:
            if fn.endswith('.html'):
                p = os.path.join(root, fn).replace('\\','/')
                all_templates.append(p)
                rel = p
                if rel not in template_stats:
                    template_stats[rel] = {'total':0,'translated':0,'fuzzy':0,'missing':0,'missing_list':[]}

# Write CSV summary
os.makedirs('reports', exist_ok=True)
with open(REPORT_CSV, 'w', encoding='utf-8', newline='') as csvf:
    writer = csv.writer(csvf)
    writer.writerow(['template','total_entries','translated','fuzzy','missing','percent_translated'])
    for tpl, s in sorted(template_stats.items()):
        total = s['total']
        translated = s['translated']
        fuzzy = s['fuzzy']
        missing = s['missing']
        pct = (translated / total * 100) if total>0 else (100 if translated>0 else 0)
        writer.writerow([tpl, total, translated, fuzzy, missing, f"{pct:.1f}"])

# Write detailed markdown
with open(REPORT_MD, 'w', encoding='utf-8') as md:
    md.write('# i18n Template Audit (Swahili)\n\n')
    md.write(f'PO file: {PO_PATH}\n\n')
    md.write('| Template | Total | Translated | Fuzzy | Missing | % Translated |\n')
    md.write('|---|---:|---:|---:|---:|---:|\n')
    for tpl, s in sorted(template_stats.items()):
        total = s['total']
        translated = s['translated']
        fuzzy = s['fuzzy']
        missing = s['missing']
        pct = (translated / total * 100) if total>0 else (100 if translated>0 else 0)
        md.write(f'| {tpl} | {total} | {translated} | {fuzzy} | {missing} | {pct:.1f}% |\n')
    md.write('\n## Missing strings by template\n\n')
    for tpl, s in sorted(template_stats.items()):
        if s['missing']>0:
            md.write(f'### {tpl}\n\n')
            for msg in s['missing_list'][:50]:
                md.write(f'- {msg}\n')
            if len(s['missing_list'])>50:
                md.write(f'- ...and {len(s["missing_list"]) - 50} more\n')
            md.write('\n')

print('Report generated:', REPORT_CSV, REPORT_MD)
