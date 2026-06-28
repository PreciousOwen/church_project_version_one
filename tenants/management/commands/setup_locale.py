"""
Management command: python manage.py setup_locale

Creates the locale directory structure, writes English and Swahili .po
translation files, then compiles them to .mo binary files.

Run once after setup:
    python manage.py setup_locale
    
If compilemessages fails (gettext not installed), compile manually:
    pip install polib
    python manage.py setup_locale   # will use polib fallback
"""

from __future__ import annotations

import os
from pathlib import Path

from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parents[4]

# ─────────────────────────────────────────────────────────────────────────────
# Translation catalogue
# Each entry: (msgid, swahili_msgstr)
# ─────────────────────────────────────────────────────────────────────────────
TRANSLATIONS: list[tuple[str, str]] = [
    # ── landing.html ──────────────────────────────────────────────────────────
    (
        "Digital Msharika — A Church for Every Season",
        "Digital Msharika — Kanisa kwa Kila Wakati",
    ),
    ("About", "Kuhusu"),
    ("Ministries", "Huduma"),
    ("Portal", "Lango"),
    ("Go to Dashboard", "Nenda Dashibodini"),
    ("Welcome", "Karibu"),
    ("Member Login", "Ingia kama Mwanachama"),
    ("Welcome to Digital Msharika", "Karibu Digital Msharika"),
    (
        "We are a vibrant, multi-generational parish committed to worship, fellowship, "
        "and the transformation of lives. Join thousands of members growing together in Christ.",
        "Sisi ni parokia yenye nguvu na vizazi vingi, iliyojitolea kwa ibada, ushirika, "
        "na mabadiliko ya maisha. Jiunge na maelfu ya wanachama wanaokua pamoja katika Kristo.",
    ),
    ("Discover our church", "Gundua kanisa letu"),
    ("Open Dashboard", "Fungua Dashibodi"),
    ("Member Portal", "Lango la Wanachama"),
    ("Our Parish at a Glance", "Parokia Yetu kwa Muhtasari"),
    ("Registered Members", "Wanachama Waliojisajili"),
    ("Fellowship Groups", "Vikundi vya Ushirika"),
    ("Sunday Services", "Ibada za Jumapili"),
    ("Years of Ministry", "Miaka ya Huduma"),
    (
        "For where two or three gather in my name, there am I with them.",
        "Kwa maana po pote wawili au watatu walipokusanyika kwa jina langu, nipo hapo katikati yao.",
    ),
    ("Who We Are", "Sisi Ni Nani"),
    ("A Church Built on the Word of God", "Kanisa Lililojengwa juu ya Neno la Mungu"),
    (
        "Digital Msharika is the digital home of a real, worshipping community where every person matters.",
        "Digital Msharika ni nyumba ya kidijitali ya jumuiya halisi ya waabudu ambayo kila mtu ana thamani.",
    ),
    (
        "Founded on the belief that the church is the body of Christ, we exist to glorify God "
        "through authentic worship, intentional discipleship, and compassionate service to our "
        "neighbourhood and the world.",
        "Imejengwa juu ya imani kwamba kanisa ni mwili wa Kristo, tunakuwepo kumtukuza Mungu "
        "kupitia ibada ya kweli, ufuasi wa makusudi, na huduma ya huruma kwa jirani zetu na ulimwengu.",
    ),
    (
        "Our congregation spans all generations — from children in Sunday school to seniors in "
        "prayer groups — united by a common faith and a shared mission to love God and love people.",
        "Mkutano wetu unajumuisha vizazi vyote — kuanzia watoto wa shule ya Jumapili hadi wazee "
        "katika vikundi vya sala — wamounganishwa na imani moja na ujumbe wa pamoja wa kupenda Mungu na watu.",
    ),
    (
        "Love the Lord your God with all your heart, soul, and mind — and love your neighbour as yourself.",
        "Mpende Bwana Mungu wako kwa moyo wako wote, na roho yako yote, na akili yako yote — "
        "na umpende jirani yako kama nafsi yako.",
    ),
    (
        "Through our fellowship groups, outreach programmes, and pastoral care teams, "
        "no member walks their journey alone.",
        "Kupitia vikundi vyetu vya ushirika, mipango ya ufikiano, na timu za huduma ya kichungaji, "
        "hakuna mwanachama anayetembea safari yake peke yake.",
    ),
    ("Worship", "Ibada"),
    (
        "Spirit-filled Sunday services and midweek prayer meetings that draw us into God's presence.",
        "Ibada za Jumapili zilizojaa Roho na mikutano ya sala ya katikati ya wiki inayotuvuta mbele za Mungu.",
    ),
    ("The Word", "Neno"),
    (
        "Expository preaching and Bible study that grounds us in Scripture and shapes our lives.",
        "Mahubiri ya ufafanuzi na masomo ya Biblia yanayotutia mizizi katika Maandiko na kuumba maisha yetu.",
    ),
    ("Fellowship", "Ushirika"),
    (
        "Vibrant small groups where relationships are forged and spiritual gifts are discovered.",
        "Vikundi vidogo vyenye nguvu ambapo mahusiano yanajengwa na vipawa vya kiroho vinagunduliwa.",
    ),
    ("Service", "Huduma"),
    (
        "Outreach, social justice, and community care that puts our faith into action beyond these walls.",
        "Ufikiano, haki za kijamii, na utunzaji wa jamii unaoweka imani yetu katika vitendo nje ya kuta hizi.",
    ),
    ("What We Offer", "Tunachotoa"),
    ("Church Life & Ministries", "Maisha ya Kanisa & Huduma"),
    (
        "Whether you are a lifelong member or visiting for the first time, there is a place for you here.",
        "Iwe wewe ni mwanachama wa maisha yote au unatembelea kwa mara ya kwanza, kuna nafasi yako hapa.",
    ),
    ("Sunday Worship", "Ibada ya Jumapili"),
    (
        "Three services every Sunday — early morning, mid-morning, and an evening family service.",
        "Ibada tatu kila Jumapili — asubuhi mapema, katikati ya asubuhi, na ibada ya familia jioni.",
    ),
    ("Bible Study", "Masomo ya Biblia"),
    (
        "Weekly in-depth study of Scripture in cell groups across the parish.",
        "Masomo ya kina ya kila wiki ya Maandiko katika vikundi vidogo kote parokiani.",
    ),
    ("Children & Youth", "Watoto & Vijana"),
    (
        "Dedicated programmes that nurture the next generation in faith and character.",
        "Programu maalum zinazolisha kizazi kijacho katika imani na tabia.",
    ),
    ("Choir & Worship", "Kwaya & Ibada"),
    (
        "Join a music team passionate about leading the congregation into authentic worship.",
        "Jiunge na timu ya muziki yenye shauku ya kuongoza mkutano katika ibada ya kweli.",
    ),
    ("Outreach", "Ufikiano"),
    (
        "Community feeding, hospital visits, and mission trips that serve the least and the lost.",
        "Kulisha jamii, kutembelea hospitali, na safari za umishonari zinazohudumia maskini na waliopotea.",
    ),
    ("Pastoral Care", "Huduma ya Kichungaji"),
    (
        "Counselling, home visits, and prayer support for members in every season of life.",
        "Ushauri, ziara za nyumbani, na msaada wa sala kwa wanachama katika kila wakati wa maisha.",
    ),
    ("Everything Your Parish Needs, Digitised", "Kila Kitu Kinachohitajika na Parokia Yako, Kimedigitishwa"),
    (
        "Our secure member portal gives church leaders and administrators a powerful toolkit to "
        "shepherd the congregation with clarity and care.",
        "Lango letu salama la wanachama linawapa viongozi wa kanisa na wasimamizi kifaa chenye nguvu "
        "cha kuchunga mkutano kwa uwazi na utunzaji.",
    ),
    ("Member Records", "Rekodi za Wanachama"),
    (
        "Complete profiles for every parishioner — contact details, family info, and giving history, all in one place.",
        "Wasifu kamili kwa kila mwanachama wa parokia — maelezo ya mawasiliano, taarifa za familia, "
        "na historia ya michango, yote mahali pamoja.",
    ),
    (
        "Create and manage small groups, ministry teams, and prayer circles with attendance tracking.",
        "Unda na simamia vikundi vidogo, timu za huduma, na mzunguko wa sala ukifuatilia mahudhurio.",
    ),
    ("Pledge & Giving", "Ahadi & Michango"),
    (
        "Track financial commitments and monitor fulfilment against targets — no spreadsheets required.",
        "Fuatilia ahadi za kifedha na angalia utimilifu dhidi ya malengo — hakuna lahajedwali zinazohitajika.",
    ),
    ("Announcements", "Matangazo"),
    (
        "Publish categorised notices, event updates, and urgent communications instantly.",
        "Chapisha matangazo yaliyopangwa, masasisho ya matukio, na mawasiliano ya dharura mara moja.",
    ),
    ("Daily Liturgy", "Liturujia ya Kila Siku"),
    (
        "Share Scripture readings, devotionals, and liturgical content to nourish members daily.",
        "Shiriki masomo ya Maandiko, ibada za kibinafsi, na maudhui ya liturujia ili kulisha wanachama kila siku.",
    ),
    ("Secure & Private", "Salama & ya Siri"),
    (
        "Role-based access and multi-tenant isolation mean each church's data is completely protected.",
        "Ufikiaji unaotegemea jukumu na kutengwa kwa wapangaji wengi kunamaanisha data ya kila kanisa inalindwa kabisa.",
    ),
    ("Ready to Access the Member Portal?", "Uko Tayari Kufikia Lango la Wanachama?"),
    (
        "Sign in with your credentials to manage members, fellowships, pledges, and more.",
        "Ingia kwa nambari zako za uthibitisho ili kusimamia wanachama, ushirika, ahadi, na zaidi.",
    ),
    ("Sign in to Portal", "Ingia Langoni"),
    (
        "A living community rooted in faith, love, and service. "
        "Bringing the church into the digital age without losing the human heart.",
        "Jumuiya hai iliyojengwa katika imani, upendo, na huduma. "
        "Kuleta kanisa katika enzi ya kidijitali bila kupoteza moyo wa kibinadamu.",
    ),
    ("Quick Links", "Viungo vya Haraka"),
    ("About Us", "Kuhusu Sisi"),
    ("Ministries & Services", "Huduma & Miradi"),
    ("Sign In", "Ingia"),
    ("Service Times", "Nyakati za Ibada"),
    ("Sunday Early Service — 7:00 AM", "Ibada ya Jumapili ya Mapema — Saa 1 Asubuhi"),
    ("Sunday Main Service — 9:30 AM", "Ibada Kuu ya Jumapili — Saa 3:30 Asubuhi"),
    ("Sunday Evening — 5:00 PM", "Ibada ya Jumapili Jioni — Saa 11 Jioni"),
    ("Wednesday Prayer — 6:30 PM", "Sala ya Jumatano — Saa 12:30 Jioni"),
    ("All rights reserved.", "Haki zote zimehifadhiwa."),
    ("Built with faith.", "Imejengwa kwa imani."),

    # ── base.html ──────────────────────────────────────────────────────────────
    ("Dashboard", "Dashibodi"),
    ("Members", "Wanachama"),
    ("Fellowships", "Ushirika"),
    ("Pledges", "Ahadi"),
    ("Sign out", "Toka"),
    ("Welcome", "Karibu"),
    ("Toggle menu", "Geuza menyu"),
    ("Tenant", "Mkodishaji"),

    # ── login.html ─────────────────────────────────────────────────────────────
    ("Sign in", "Ingia"),
    ("Welcome back", "Karibu tena"),
    ("Sign in to manage members, pledges, and content.", "Ingia ili kusimamia wanachama, ahadi, na maudhui."),
    ("Username", "Jina la Mtumiaji"),
    ("Password", "Nenosiri"),
]

PO_HEADER_EN = """\
# English locale for Digital Msharika (reference — msgstr is empty).
#
msgid ""
msgstr ""
"Project-Id-Version: digital_msharika\\n"
"Report-Msgid-Bugs-To: \\n"
"PO-Revision-Date: 2026-03-11 12:00+0000\\n"
"Language-Team: English\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"""

PO_HEADER_SW = """\
# Swahili (Kiswahili) locale for Digital Msharika.
#
msgid ""
msgstr ""
"Project-Id-Version: digital_msharika\\n"
"Report-Msgid-Bugs-To: \\n"
"PO-Revision-Date: 2026-03-11 12:00+0000\\n"
"Language-Team: Swahili\\n"
"Language: sw\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"""


def _escape(s: str) -> str:
    """Escape a string for use in a .po file."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _po_entry(msgid: str, msgstr: str) -> str:
    return f'msgid "{_escape(msgid)}"\nmsgstr "{_escape(msgstr)}"\n'


def _write_po(path: Path, header: str, entries: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [header]
    for msgid, msgstr in entries:
        lines.append(_po_entry(msgid, msgstr))
    path.write_text("\n".join(lines), encoding="utf-8")


def _compile_po(po_path: Path) -> bool:
    """Compile a .po file to a .mo file. Returns True on success."""
    mo_path = po_path.with_suffix(".mo")
    # Try polib first (pure Python, no system gettext needed)
    try:
        import polib  # type: ignore

        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        return True
    except ImportError:
        pass
    # Fall back to Django's compilemessages (needs system gettext)
    try:
        from django.core.management import call_command

        call_command("compilemessages", locale=[po_path.parts[-3]], verbosity=0)
        return True
    except Exception:
        return False


class Command(BaseCommand):
    help = (
        "Create the locale directory structure, write .po translation files "
        "(English + Swahili), and compile them to binary .mo files.\n\n"
        "Run once after initial setup:\n"
        "    python manage.py setup_locale\n\n"
        "Requires either:\n"
        "  • polib  (pip install polib)  — pure-Python, no system deps\n"
        "  • OR GNU gettext utilities installed on the system\n"
    )

    def handle(self, *args, **options):
        locale_dir = BASE_DIR / "locale"

        en_po = locale_dir / "en" / "LC_MESSAGES" / "django.po"
        sw_po = locale_dir / "sw" / "LC_MESSAGES" / "django.po"

        # English reference (empty msgstr)
        _write_po(en_po, PO_HEADER_EN, [(m, "") for m, _ in TRANSLATIONS])
        self.stdout.write(self.style.SUCCESS(f"Written: {en_po}"))

        # Swahili
        _write_po(sw_po, PO_HEADER_SW, TRANSLATIONS)
        self.stdout.write(self.style.SUCCESS(f"Written: {sw_po}"))

        # Compile
        for po_path in [en_po, sw_po]:
            lang = po_path.parts[-3]
            ok = _compile_po(po_path)
            if ok:
                self.stdout.write(self.style.SUCCESS(f"Compiled .mo for [{lang}]"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not compile .mo for [{lang}]. "
                        "Run: pip install polib && python manage.py setup_locale"
                    )
                )

        self.stdout.write(self.style.SUCCESS("\nLocale setup complete."))
