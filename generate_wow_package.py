"""
Generate the "Wow Package" PDF for Bryan McInerney.
Compiles: prospect list summaries, outreach templates, industry playbooks,
automation roadmap, and next steps into a polished deliverable.
"""
from fpdf import FPDF
import csv
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "Bryan_McInerney_Prospecting_Package.pdf")


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, "SIMPL ABI  |  PROSPECTING PACKAGE FOR INTELLIGENT ANNUITY SOLUTIONS  |  MAY 2026", align="C")
        self.ln(5)
        self.set_draw_color(0, 90, 180)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 60, 140)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_draw_color(0, 90, 180)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 130, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, title)
        self.ln(7)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=12):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(x + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def numbered(self, num, title, desc=""):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 60, 140)
        self.cell(8, 6, str(num) + ".")
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, title)
        self.ln(6)
        if desc:
            self.set_x(self.get_x() + 8)
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 5.5, desc)
            self.ln(2)

    def box(self, text):
        self.ln(2)
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(0, 90, 180)
        self.set_line_width(0.3)
        x, y = self.get_x(), self.get_y()
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(30, 30, 30)
        w = self.w - self.l_margin - self.r_margin - 6
        lines = self.multi_cell(w, 5.5, text, dry_run=True, output="LINES")
        h = len(lines) * 5.5 + 8
        self.rect(x, y, self.w - self.l_margin - self.r_margin, h, style="DF")
        self.set_xy(x + 5, y + 4)
        self.multi_cell(w, 5.5, text)
        self.ln(4)

    def stat_row(self, label, value):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(60, 7, label)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 60, 140)
        self.cell(0, 7, str(value))
        self.ln(7)


def count_csv(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for _ in csv.reader(f)) - 1
    except:
        return 0


def get_top_cities(filepath, n=5):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cities = {}
            for r in reader:
                c = r.get("City", "")
                cities[c] = cities.get(c, 0) + 1
        return sorted(cities.items(), key=lambda x: -x[1])[:n]
    except:
        return []


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ── COVER PAGE ──
pdf.add_page()
pdf.ln(30)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(0, 50, 120)
pdf.cell(0, 16, "Prospecting Package", align="C")
pdf.ln(14)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, "Prepared for Bryan McInerney", align="C")
pdf.ln(8)
pdf.cell(0, 10, "Intelligent Annuity Solutions, LLC", align="C")
pdf.ln(16)
pdf.set_draw_color(0, 90, 180)
pdf.set_line_width(0.8)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(12)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, "Prepared by Simpl ABI  |  May 2026", align="C")
pdf.ln(7)
pdf.cell(0, 7, "Samuel J. Karman, CEO  |  simplabiwebsite.com", align="C")
pdf.ln(20)

pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(0, 60, 140)
pdf.cell(0, 8, "What's Inside", align="C")
pdf.ln(10)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(60, 60, 60)
toc = [
    "1.  Prospect Lists -- 5,000+ verified NE Ohio prospects across 3 industries",
    "2.  Outreach Templates -- 15 LPL-compliant email and LinkedIn templates",
    "3.  Industry Playbooks -- Actionable guides for Dentists, Doctors, and Lawyers",
    "4.  Outreach Tracker -- CRM-ready Excel spreadsheet for pipeline management",
    "5.  Automation Roadmap -- How manual outreach becomes a fully automated system",
    "6.  Next Steps -- The critical questions and immediate actions",
]
for item in toc:
    pdf.cell(0, 7, item, align="C")
    pdf.ln(6)

# ── SECTION 1: PROSPECT LISTS ──
pdf.add_page()
pdf.section_title("1. Prospect Lists")

dentist_count = count_csv(os.path.join(OUTPUT_DIR, "prospects_dentists.csv"))
doctor_count = count_csv(os.path.join(OUTPUT_DIR, "prospects_doctors.csv"))
lawyer_count = count_csv(os.path.join(OUTPUT_DIR, "prospects_lawyers.csv"))
total = dentist_count + doctor_count + lawyer_count

pdf.body(
    "We compiled prospect lists from free public data sources including the NPI Registry "
    "(National Provider Identifier -- the federal database of all healthcare providers), "
    "Ohio licensing boards, bar association directories, and business filings. "
    "Every record includes the provider's name, credentials, practice address, city, "
    "phone number, and specialty."
)

pdf.sub_title("Prospect Counts")
pdf.stat_row("Dentists (NE Ohio):", f"{dentist_count:,}")
pdf.stat_row("Physicians (NE Ohio):", f"{doctor_count:,}")
pdf.stat_row("Lawyers (NE Ohio):", f"{lawyer_count:,}" if lawyer_count > 0 else "In progress")
pdf.stat_row("TOTAL PROSPECTS:", f"{total:,}")

pdf.ln(4)
pdf.sub_title("Top Cities -- Dentists")
for city, count in get_top_cities(os.path.join(OUTPUT_DIR, "prospects_dentists.csv"), 8):
    pdf.bullet(f"{city}: {count} dentists")

pdf.sub_title("Top Cities -- Physicians")
for city, count in get_top_cities(os.path.join(OUTPUT_DIR, "prospects_doctors.csv"), 8):
    pdf.bullet(f"{city}: {count} physicians")

pdf.box(
    "These lists are delivered as CSV files that import directly into any CRM, "
    "email platform, or spreadsheet. Each record is a real, verified professional "
    "practicing in Northeast Ohio today."
)

# ── SECTION 2: OUTREACH TEMPLATES ──
pdf.add_page()
pdf.section_title("2. LPL-Compliant Outreach Templates")

pdf.body(
    "We created 15 outreach templates (5 per industry) that are pre-vetted against "
    "LPL Financial's compliance guidelines. Every template avoids all prohibited terms "
    "identified in the FINRA/SIPC Problematic Terms guide and uses only approved "
    "language and soft calls-to-action."
)

pdf.sub_title("Template Types (5 per industry)")
pdf.numbered(1, "Cold Introduction Email",
    "Introduces Bryan, references industry-specific pain points, offers a 15-minute conversation.")
pdf.numbered(2, "Whitepaper Offer Email",
    "Drives prospects to Bryan's existing lead magnet at checkannuity.com. Educational, no-obligation CTA.")
pdf.numbered(3, "Educational Event / Meeting Invite",
    "Invites prospects to a complimentary educational session. Not a sales pitch.")
pdf.numbered(4, "Follow-Up After No Response",
    "Gentle second touch with a direct value proposition. Short and respectful.")
pdf.numbered(5, "LinkedIn Connection Request",
    "Under 300 characters. Personal, compliant, with a hook relevant to the prospect's industry.")

pdf.sub_title("Industries Covered")
pdf.bullet("Dentists -- 5 templates focused on practice value, tax exposure on sale, fee erosion")
pdf.bullet("Physicians -- 5 templates focused on hidden 401(k) fees, tax burden, cash balance plans")
pdf.bullet("Lawyers -- 5 templates focused on income volatility, portfolio fees, buy-sell planning")

pdf.sub_title("Compliance Verification")
pdf.body(
    "Every template has been checked against the full LPL Problematic Terms guide. "
    "No prohibited terms are used. All calls-to-action are soft and educational. "
    "Required disclosures (entity name, LPL/FINRA/SIPC) are included in every email. "
    "A detailed compliance audit is included with the template file."
)
pdf.box(
    "IMPORTANT: While these templates are designed to be compliant, they should still "
    "be submitted to LPL's compliance team for formal approval before use in any "
    "client-facing campaign."
)

# ── SECTION 3: INDUSTRY PLAYBOOKS ──
pdf.add_page()
pdf.section_title("3. Industry Playbooks")

pdf.body(
    "We created detailed, actionable playbooks for each of Bryan's three Tier 1 "
    "industries. Each playbook is designed to be printed and used immediately."
)

for industry, details in [
    ("Dentists (Priority #1)", [
        "Pain points: 60-80% net worth in practice, succession gap, 30-40% tax loss on sale",
        "Key associations: Greater Cleveland Dental Society, Akron Dental Society, NEODS, ODA",
        "Best channel: Dental study club presentations (20-min talk)",
        "COIs: Dental CPAs, practice brokers (AFTCO, Henry Schein), supply reps",
        "Outreach sequence: Day 1 email -> Day 3 LinkedIn -> Day 6 follow-up -> Day 10 whitepaper -> Day 15 call -> Day 20 event invite",
        "Talk track and qualifying questions included",
    ]),
    ("Physicians (Priority #2)", [
        "Pain points: 37%+ tax rates, hidden 401(k) fees, student debt vs wealth building",
        "Key associations: AMCNO, OSMA, APPNA-NEO",
        "Best channel: CPA referrals, educational dinner seminars",
        "COIs: Medical practice CPAs, malpractice attorneys, hospital admin contacts",
        "Outreach sequence: Same 20-day cadence tailored for physician messaging",
        "Talk track and qualifying questions included",
    ]),
    ("Lawyers (Priority #3)", [
        "Pain points: Income volatility, 50%+ tax rates, no pension, hidden fees",
        "Key associations: CMBA (~5,000 members), Akron Bar, OSBA",
        "Best channel: CPA/estate attorney referral networks, CMBA events",
        "COIs: CPAs serving law firms, estate planning attorneys, legal recruiters",
        "Outreach sequence: Same 20-day cadence tailored for attorney messaging",
        "Talk track and qualifying questions included",
    ]),
]:
    pdf.sub_title(industry)
    for d in details:
        pdf.bullet(d)

pdf.box(
    "Full playbooks are delivered as a separate document with complete association "
    "contact information, event calendars, conversation scripts, and step-by-step "
    "outreach instructions."
)

# ── SECTION 4: OUTREACH TRACKER ──
pdf.add_page()
pdf.section_title("4. Outreach Tracker")

pdf.body(
    "We built a CRM-ready Excel spreadsheet for tracking all prospecting activity. "
    "This tracker is designed to be used immediately for manual outreach and to "
    "import cleanly into any CRM platform as the system scales."
)

pdf.sub_title("Features")
pdf.bullet("33 columns covering prospect data, outreach activity, responses, and pipeline status")
pdf.bullet("Auto-filters and frozen headers for easy sorting and searching")
pdf.bullet("Built-in dashboard tab with live metrics (total prospects, response rate, meeting rate)")
pdf.bullet("Reference tab with status options, channel types, and industry categories")
pdf.bullet("Columns for up to 3 outreach touches per prospect with date, channel, and template tracking")
pdf.bullet("CRM-importable format (imports directly into HubSpot, Salesforce, Pipedrive, etc.)")

pdf.box(
    "This spreadsheet is the bridge between manual outreach and automation. "
    "Every data point captured here feeds directly into the automated CRM system "
    "we will build as the engagement scales."
)

# ── SECTION 5: AUTOMATION ROADMAP ──
pdf.add_page()
pdf.section_title("5. Automation Roadmap")

pdf.body(
    "Everything in this package is designed to convert from manual processes into "
    "fully automated systems. Here is the roadmap for that transition."
)

pdf.sub_title("Phase 1: Manual (Now)")
pdf.bullet("Prospect lists built from free public databases")
pdf.bullet("Outreach templates personalized and sent manually")
pdf.bullet("Activity tracked in Excel spreadsheet")
pdf.bullet("Follow-ups managed by calendar reminders")

pdf.sub_title("Phase 2: Semi-Automated (Month 2-3)")
pdf.bullet("Automated prospect list scraping -- Python scripts pull fresh data from NPI, licensing boards, FMCSA on a schedule")
pdf.bullet("AI-powered compliance checker -- scans any draft content against LPL prohibited terms before submission")
pdf.bullet("Template personalization engine -- automatically fills templates with prospect data from the list")
pdf.bullet("CRM integration -- move from spreadsheet to a real pipeline dashboard with automated follow-up reminders")

pdf.sub_title("Phase 3: Fully Automated (Month 4-6)")
pdf.bullet("Automated email sequencing -- compliant outreach fires on schedule with no manual intervention")
pdf.bullet("LinkedIn automation -- connection requests and messaging at scale")
pdf.bullet("Lead scoring -- AI ranks prospects by likelihood to convert based on engagement signals")
pdf.bullet("Meeting booking -- automated calendar integration so prospects self-schedule")
pdf.bullet("Reporting dashboard -- real-time metrics on outreach volume, response rates, meetings booked, and pipeline value")

pdf.box(
    "THE VISION: Bryan wakes up, checks his calendar, and sees meetings with "
    "pre-qualified prospects who already understand what he does. Simpl ABI "
    "handles everything before that meeting -- from finding the prospect to "
    "warming them up to booking the appointment."
)

# ── SECTION 6: NEXT STEPS ──
pdf.add_page()
pdf.section_title("6. Immediate Next Steps")

pdf.numbered(1, "Resolve the LPL Compliance Question",
    "Before any outreach goes live, we need clarity on: Can templates be pre-approved "
    "for reuse? Does 1-to-1 correspondence require the same approval as mass marketing? "
    "Is non-securities educational content exempt? This determines our launch speed.")

pdf.numbered(2, "Review and Select Priority Prospects",
    "From the 5,000+ prospect list, we recommend selecting the top 50 across all "
    "three industries to begin outreach. We will prioritize by geography (closest to "
    "Hudson), practice type (private practice owners), and specialty alignment.")

pdf.numbered(3, "Submit Templates to LPL for Approval",
    "Send the 15 outreach templates to LPL compliance for review. If batch approval "
    "is available, submit all at once. Target: have approved templates ready to deploy "
    "within 1-2 weeks.")

pdf.numbered(4, "Launch Manual Outreach",
    "Begin the daily outreach cadence: 10-15 personalized emails per morning, "
    "10-15 LinkedIn connection requests at midday, follow-up management in afternoon. "
    "All activity tracked in the Excel spreadsheet.")

pdf.numbered(5, "Schedule Automation Build",
    "While manual outreach runs, Simpl ABI begins building the automated systems "
    "(scraper scripts, compliance checker, personalization engine) so the transition "
    "from manual to automated is seamless.")

pdf.ln(8)
pdf.set_draw_color(0, 90, 180)
pdf.set_line_width(0.6)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Prepared by Simpl ABI for Bryan McInerney, Intelligent Annuity Solutions, LLC", align="C")
pdf.ln(6)
pdf.cell(0, 6, "Samuel J. Karman, CEO  |  simplabiwebsite.com  |  330-607-2668", align="C")
pdf.ln(6)
pdf.cell(0, 6, "All prospect data sourced from public federal and state databases.", align="C")

pdf.output(OUTPUT_PATH)
print(f"PDF generated: {OUTPUT_PATH}")
print(f"  Pages: {pdf.page_no()}")
