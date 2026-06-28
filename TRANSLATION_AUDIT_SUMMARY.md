# English→Swahili Translation Audit & Patch Summary

**Date**: 2026-06-26  
**Project**: KKKT Salasala DMP (Church Project)

## Overview

A comprehensive i18n audit was performed across all HTML templates and Python files (forms, views, models) to assess English→Swahili translation completeness.

## Key Findings

### Translation Coverage: **90.4%** (545 translated out of 603 entries)

| Metric | Count |
|--------|-------|
| **Total translatable entries** | 603 |
| **Translated** | 545 |
| **Fuzzy (marked for review)** | 20 |
| **Missing (empty msgstr)** | 58 |
| **Coverage %** | 90.4% |

---

## Scope Audit Includes

✓ **All Main Templates** (225 files):
  - `templates/base.html` — 95.7% complete
  - `templates/landing.html` — 98.5% complete
  - `templates/login.html` — 81.8% complete (2 missing)
  - `templates/public/about.html` — 97.1% complete
  - `templates/public/contact.html` — 96.6% complete
  - `templates/public/events.html` — 97.6% complete
  - `templates/public/ministries.html` — 97.2% complete
  - `templates/members/*` — 84–100% complete
  - `templates/pledges/list.html` — 74.2% complete (8 missing)
  - `templates/password_reset_*.html` — 60% complete (6 missing total)
  - `templates/signup_verify.html` — 33.3% complete (4 missing)

✓ **All App Forms & Views**:
  - `tenants/forms.py` — translatable strings in login/signup forms
  - `tenants/views.py` — error/success messages
  - `members/forms.py` — field labels, choices, validations
  - `members/models.py` — model choice fields

✓ **All Installed Apps**:
  - `tenants` — multi-tenant auth
  - `members` — member management
  - `fellowships` — fellowship groups
  - `pledges` — financial pledges
  - `content_app` — announcements, liturgy, events
  - `api` — REST endpoints

---

## Templates with Incomplete Translations

### High Priority (< 80% complete):

1. **`templates/signup_verify.html`** — 33.3% (4 missing)
   - "Verify"
   - "Verify your phone"
   - "We sent a 6-digit code to %(phone_number)s. Enter it below to complete signup."
   - "Back to signup"

2. **`templates/password_reset_request.html`** — 60% (2 missing)
   - "Send code"
   - "Back to sign in"

3. **`templates/password_reset_set.html`** — 60% (2 missing)
   - "Back to sign in"
   - "Use a password with at least 6 digits."

4. **`templates/password_reset_verify.html`** — 60% (2 missing)
   - "We sent a 6-digit code to %(phone_number)s."
   - "Back to reset request"

5. **`templates/pledges/list.html`** — 74.2% (8 missing)
   - "Season", "Jan - Jun (6 months)", "Jul - Dec (6 months)"
   - "e.g. 2026 or 150000"
   - "Pledges captured in selected period"
   - "Selected year/season" (appears 3 times)

6. **`templates/members/me.html`** — 84.2% (6 missing)
   - "Submitted at:"
   - "Your application is under review..."
   - "Your application was not approved..."
   - "Submit again"
   - "Your profile will appear here..."
   - "You have not submitted a membership application yet."

### Medium Priority (80–95% complete):

7. **`templates/login.html`** — 81.8% (2 missing)
   - "Phone number or admin username"
   - "Reset here"

8. **`templates/members/form.html`** — 93.5% (2 missing)
   - "Set a new 6-digit password for this user account."
   - "New password (6 digits)"

9. **`templates/base.html`** — 95.7% (1 missing)
   - "Change language"

10. **`templates/landing.html`** — 98.5% (1 missing)
    - "&copy; 2026 KKKT Salasala DMP. All Rights Reserved."

11. **`templates/public/{about,contact,events,ministries}.html`** — 96–97% (1 each)
    - Same copyright line: "&copy; 2026 KKKT Salasala DMP. All Rights Reserved."

---

## Patched PO File

A patched version of the Swahili `.po` file has been generated with placeholder translations for all 54–58 missing entries.

**File**: [`locale/sw/LC_MESSAGES/django_patched.po`](locale/sw/LC_MESSAGES/django_patched.po)

Each missing translation is marked with:
```
msgstr "[PENDING TRANSLATION] <original_english_text>..."
```

### How to Apply the Patch

1. **Backup original**:
   ```bash
   cp locale/sw/LC_MESSAGES/django.po locale/sw/LC_MESSAGES/django.po.bak
   ```

2. **Copy patched file**:
   ```bash
   cp locale/sw/LC_MESSAGES/django_patched.po locale/sw/LC_MESSAGES/django.po
   ```

3. **Compile messages**:
   ```bash
   python manage.py compilemessages -l sw
   ```

4. **Replace the [PENDING TRANSLATION] placeholders** with actual Swahili translations by a native Swahili speaker.

5. **Recompile after translation updates**:
   ```bash
   python manage.py compilemessages -l sw
   ```

---

## Next Steps for Complete Translation

1. **Priority 1**: Replace [PENDING TRANSLATION] placeholders in the patched `.po` file with correct Swahili translations.
2. **Priority 2**: Remove any `#, fuzzy` flags once translations are verified (currently 20 entries marked fuzzy).
3. **Priority 3**: Test all pages in Swahili mode (set `LANGUAGE_CODE = 'sw'` or use language switcher).
4. **Priority 4**: Recompile messages and deploy.

---

## Reports Generated

- [`reports/i18n_template_audit.csv`](reports/i18n_template_audit.csv) — CSV summary of completeness by template
- [`reports/i18n_template_audit_details.md`](reports/i18n_template_audit_details.md) — Detailed markdown report with missing strings listed per template

---

## Tools & Scripts

- **`scripts/i18n_audit_enhanced.py`** — Full audit (templates + Python files)
- **`scripts/patch_po.py`** — Generates patched `.po` with placeholders

Run audit again:
```bash
python scripts/i18n_audit_enhanced.py
```

Regenerate patch:
```bash
python scripts/patch_po.py
```
