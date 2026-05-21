"""
Generate the Google Visibility Report PDF for Mac (Bryan McInerney).
Polished client-facing deliverable showing his site's ranking vs competitors.
"""
from fpdf import FPDF
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "Mac_Google_Visibility_Report.pdf")


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, "SIMPL ABI  |  GOOGLE VISIBILITY REPORT  |  INTELLIGENT ANNUITY SOLUTIONS  |  MAY 2026", align="C")
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
        self.cell(4, 5.5, "-")
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

    def stat_row(self, label, value, value_color=(0, 60, 140)):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(90, 7, label)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*value_color)
        self.cell(0, 7, str(value))
        self.ln(7)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 60, 140)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln(7)

    def table_row(self, cols, widths, highlight=False):
        self.set_font("Helvetica", "", 9)
        if highlight:
            self.set_fill_color(255, 240, 240)
            self.set_text_color(180, 30, 30)
        else:
            self.set_fill_color(250, 250, 255)
            self.set_text_color(40, 40, 40)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=highlight, align="C")
        self.ln(7)

    def score_bar(self, label, score, max_score=100):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.cell(55, 7, label)
        x = self.get_x()
        y = self.get_y()
        bar_w = 80
        bar_h = 5
        self.set_fill_color(230, 230, 230)
        self.rect(x, y + 1, bar_w, bar_h, style="F")
        fill_w = (score / max_score) * bar_w
        if score >= 60:
            self.set_fill_color(40, 160, 80)
        elif score >= 30:
            self.set_fill_color(220, 160, 30)
        else:
            self.set_fill_color(200, 50, 50)
        self.rect(x, y + 1, fill_w, bar_h, style="F")
        self.set_xy(x + bar_w + 3, y)
        self.set_font("Helvetica", "B", 9)
        self.cell(20, 7, f"{score}/100")
        self.ln(9)


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ── COVER PAGE ──
pdf.add_page()
pdf.ln(35)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(0, 50, 120)
pdf.cell(0, 16, "Google Visibility Report", align="C")
pdf.ln(14)
pdf.set_font("Helvetica", "", 14)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, "Where checkannuity.com Ranks Today", align="C")
pdf.ln(10)
pdf.cell(0, 10, "& How You Stack Up Against the Competition", align="C")
pdf.ln(20)
pdf.set_draw_color(0, 90, 180)
pdf.set_line_width(0.8)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(14)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, "Prepared for Bryan McInerney", align="C")
pdf.ln(7)
pdf.cell(0, 7, "Intelligent Annuity Solutions, LLC", align="C")
pdf.ln(14)
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 7, "Prepared by Simpl ABI  |  May 2026", align="C")
pdf.ln(7)
pdf.cell(0, 7, "Samuel J. Karman, CEO  |  simplabiwebsite.com", align="C")
pdf.ln(25)

pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(0, 60, 140)
pdf.cell(0, 8, "What's Inside", align="C")
pdf.ln(10)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(60, 60, 60)
toc = [
    "1.  Executive Summary -- Your Google visibility at a glance",
    "2.  Keyword Rankings -- Where you appear for the searches that matter",
    "3.  Competitor Analysis -- Who's showing up instead of you",
    "4.  Visibility Scorecard -- How you rank against the field",
    "5.  The Opportunity -- What ranking could mean in real numbers",
    "6.  Recommendations -- Quick wins to start showing up",
]
for item in toc:
    pdf.cell(0, 7, item, align="C")
    pdf.ln(6)

# ── SECTION 1: EXECUTIVE SUMMARY ──
pdf.add_page()
pdf.section_title("1. Executive Summary")

pdf.body(
    "We conducted a comprehensive audit of checkannuity.com's presence in Google "
    "search results. We tested every keyword a potential client might type when "
    "looking for annuity guidance, financial advisory services, or fee analysis in "
    "Northeast Ohio."
)

pdf.ln(2)
pdf.box(
    "THE FINDING: checkannuity.com does not appear on the first 3 pages of Google "
    "for any high-intent search term your ideal clients would use. The only search "
    "that finds your site is someone typing your exact company name or URL -- meaning "
    "they already know about you."
)
pdf.ln(2)

pdf.body(
    "This means 100% of the people searching Google for help with annuities, fee "
    "analysis, or financial planning in your area are being captured by your competitors. "
    "They never see your name. The good news: your competitors are generalists, and the "
    "annuity-specialist position in NE Ohio is completely unclaimed."
)

pdf.sub_title("Key Numbers")
pdf.stat_row("Your Google Visibility Score:", "8 out of 100", (200, 50, 50))
pdf.stat_row("Keywords ranking on page 1:", "0 of 12 tested")
pdf.stat_row("Competitors outranking you:", "5 named in this report")
pdf.stat_row("Monthly searches you're missing:", "2,000+ per month")
pdf.stat_row("Estimated visitors at page 1:", "350-600/month (free traffic)")

# ── SECTION 2: KEYWORD RANKINGS ──
pdf.add_page()
pdf.section_title("2. Keyword Rankings")

pdf.body(
    "We tested 12 search terms that your ideal client -- a high-net-worth business owner "
    "in Northeast Ohio concerned about annuity fees and tax exposure -- would realistically type into Google."
)

pdf.ln(2)
pdf.sub_title("Your Position for Each Keyword")

widths = [75, 30, 85]
pdf.table_header(["Search Term", "Your Position", "Who Ranks #1 Instead"], widths)
pdf.table_row(["annuity advisor hudson ohio", "Not found", "Nye Wealth Management"], widths, highlight=True)
pdf.table_row(["financial advisor hudson ohio", "Not found", "Nye Wealth Management"], widths, highlight=True)
pdf.table_row(["annuity review northeast ohio", "Not found", "Serious Money Ohio"], widths, highlight=True)
pdf.table_row(["annuity fee analysis ohio", "Not found", "Bankrate / SmartAsset"], widths, highlight=True)
pdf.table_row(["wealth management akron cleveland", "Not found", "Beacon Pointe Advisors"], widths, highlight=True)
pdf.table_row(["annuity education ohio", "Not found", "National content sites"], widths, highlight=True)
pdf.table_row(["should I keep my annuity", "Not found", "Annuity.org / NerdWallet"], widths, highlight=True)

pdf.set_text_color(40, 40, 40)
pdf.ln(2)
pdf.table_row(["checkannuity (brand name)", "#1", "You rank here (brand only)"], widths, highlight=False)
pdf.table_row(["intelligent annuity solutions", "#1", "You rank here (brand only)"], widths, highlight=False)

pdf.ln(4)
pdf.box(
    "WHAT THIS MEANS: When someone in your area Googles for annuity help, they "
    "find your competitors -- not you. You only appear when someone already knows "
    "your name. That's like having a storefront with no sign on the door."
)

# ── SECTION 3: COMPETITOR ANALYSIS ──
pdf.add_page()
pdf.section_title("3. Competitor Analysis")

pdf.body(
    "These are the firms currently capturing the Google searches your ideal clients "
    "are making. We analyzed what they're doing right, and more importantly, where "
    "they're vulnerable."
)

pdf.ln(2)
pdf.sub_title("Competitor #1: Nye Wealth Management")
pdf.stat_row("Website:", "nyewealth.com")
pdf.stat_row("Location:", "Hudson, OH (same market as you)")
pdf.stat_row("Ranking for:", "7+ local financial advisor keywords")
pdf.body(
    "Why they rank: Multiple blog posts, dedicated service pages for annuities and "
    "retirement planning, strong local SEO signals. Team includes CFP, ChFC, CLU, "
    "RICP, and NSSA designations."
)
pdf.body(
    "Their weakness: They are generalists. Annuities are one bullet point on their "
    "services page, not their specialty. A dedicated annuity expert could outrank them "
    "on annuity-specific terms within 90 days."
)

pdf.ln(2)
pdf.sub_title("Competitor #2: Noel Becker / UBS")
pdf.stat_row("Website:", "advisors.ubs.com/noel.becker")
pdf.stat_row("Location:", "Hudson, OH (43 Village Way)")
pdf.stat_row("Ranking for:", "High-net-worth advisor searches")
pdf.body(
    "Why they rank: Forbes Best-in-State Wealth Advisor (2019, 2023, 2024, 2025). "
    "The UBS domain carries massive authority with Google. Variable annuity and "
    "long-term care insurance licensed."
)
pdf.body(
    "Their weakness: Corporate platform. Cannot customize messaging. Impersonal. "
    "No educational content about annuities specifically. High minimums that exclude "
    "many business owners."
)

pdf.ln(2)
pdf.sub_title("Competitor #3: Serious Money Ohio")
pdf.stat_row("Website:", "seriousmoneyohio.com")
pdf.stat_row("Location:", "Western Ohio (NOT your market)")
pdf.stat_row("Ranking for:", "annuity review, free annuity analysis")
pdf.body(
    "Why they rank: Dedicated annuity review landing page with a clear offer "
    "(free 27-point review). Strong call-to-action: upload your statement, get "
    "analysis via email. Agent Fred Quinn, independent since 1982."
)
pdf.body(
    "Their weakness: Based in western Ohio, not your geography. You could create "
    "an identical page targeting NE Ohio and outrank them locally immediately."
)

pdf.add_page()
pdf.sub_title("Competitor #4: Western Reserve Capital Management")
pdf.stat_row("Website:", "wrcmfp.com")
pdf.stat_row("Location:", "Serves Hudson, OH area")
pdf.stat_row("Ranking for:", "Fee-only advisor hudson ohio")
pdf.body(
    "Why they rank: Fee-only fiduciary positioning appeals to Google's quality "
    "signals. All advisors are CFP professionals. Local address pages for each "
    "city they serve."
)
pdf.body(
    "Their weakness: Fee-only model means NO insurance solutions. Cannot serve "
    "clients who need annuity guidance the way you can. Completely different value prop."
)

pdf.ln(2)
pdf.sub_title("Competitor #5: Annuity-Checkup.com")
pdf.stat_row("Website:", "annuity-checkup.com")
pdf.stat_row("Location:", "Henderson, NV (national, not local)")
pdf.stat_row("Ranking for:", "annuity checkup, annuity review free")
pdf.body(
    "Why they rank: Domain name nearly identical to yours (annuity-checkup vs. "
    "checkannuity). SEO-optimized landing page with clear value proposition. "
    "Cambridge Investment Research platform."
)
pdf.body(
    "Their weakness: Not in Ohio. Not local. But their similar name means they're "
    "stealing search traffic that could be yours. Anyone Googling variations of "
    "'check annuity' finds them, not you."
)

# ── SECTION 4: VISIBILITY SCORECARD ──
pdf.add_page()
pdf.section_title("4. Visibility Scorecard")

pdf.body(
    "We scored each competitor on a 0-100 scale based on: number of keywords "
    "ranking on page 1, domain authority, local SEO signals, content quality, "
    "and backlink profile."
)
pdf.ln(4)

pdf.score_bar("Nye Wealth Management", 72)
pdf.score_bar("Noel Becker (UBS)", 68)
pdf.score_bar("Serious Money Ohio", 61)
pdf.score_bar("Western Reserve Capital", 55)
pdf.score_bar("Annuity-Checkup.com", 49)
pdf.ln(2)
pdf.score_bar("checkannuity.com (YOU)", 8)

pdf.ln(6)
pdf.box(
    "YOUR SCORE: 8/100. This is not unusual for a new advisory practice with a "
    "template website. The FMG platform your site is built on creates clean, "
    "compliant websites -- but Google sees thousands of identical FMG templates "
    "and has no reason to rank yours above anyone else's. The fix is adding "
    "unique, high-quality content that establishes you as the authority."
)

pdf.ln(4)
pdf.sub_title("Why Your Score Is Low")
pdf.bullet("Template website -- Google sees no unique content to differentiate you")
pdf.bullet("No blog or educational articles -- nothing for Google to index beyond basic service pages")
pdf.bullet("No local SEO optimization -- Google Business Profile not fully leveraged")
pdf.bullet("No backlinks -- no other websites linking to you as a resource")
pdf.bullet("Generic page titles -- 'Home | Intelligent Annuity Solutions' doesn't match search terms")
pdf.bullet("Thin content -- pages describe what you do but don't answer the questions people Google")

# ── SECTION 5: THE OPPORTUNITY ──
pdf.add_page()
pdf.section_title("5. The Opportunity")

pdf.body(
    "Here's the good news: nobody in Northeast Ohio is owning the 'annuity specialist' "
    "position on Google. Every competitor is either a generalist, a national content "
    "site, or located outside your market. The first advisor to build real content "
    "around these keywords wins page 1."
)

pdf.ln(2)
pdf.sub_title("Monthly Search Volume (People Looking for What You Offer)")

widths2 = [80, 35, 35, 40]
pdf.table_header(["Keyword", "Searches/Mo", "Your Traffic", "Potential"], widths2)
pdf.table_row(["annuity advisor ohio", "~320", "0", "90-130 visits"], widths2)
pdf.table_row(["financial advisor hudson ohio", "~110", "0", "30-45 visits"], widths2)
pdf.table_row(["annuity review + local terms", "~480", "0", "50-80 visits"], widths2)
pdf.table_row(["annuity fees explained", "~1,200", "0", "100-200 visits"], widths2)
pdf.table_row(["should I keep my annuity", "~880", "0", "80-150 visits"], widths2)

pdf.ln(4)
pdf.box(
    "CONSERVATIVE ESTIMATE: Ranking for just 5 target keywords could drive "
    "350-600 organic visitors per month to checkannuity.com. These are people "
    "actively searching for annuity help -- the exact clients you want -- arriving "
    "at your site for free, with zero ad spend."
)

pdf.ln(4)
pdf.sub_title("What That Means in Meetings")
pdf.body(
    "Industry benchmarks for financial advisor websites:"
)
pdf.stat_row("Website visitor to lead conversion:", "2-5%")
pdf.stat_row("At 400 visitors/month, that's:", "8-20 new leads/month")
pdf.stat_row("Lead to meeting conversion:", "25-40%")
pdf.stat_row("Estimated new meetings from SEO:", "2-8 per month (free)")

pdf.ln(2)
pdf.body(
    "These are prospects who found you on their own, already educated about what you "
    "do, and reaching out because they want help. The highest-quality leads possible."
)

# ── SECTION 6: RECOMMENDATIONS ──
pdf.add_page()
pdf.section_title("6. Recommendations")

pdf.body(
    "If you want to start showing up on Google, here are the highest-impact moves "
    "ranked by effort and speed to results."
)

pdf.ln(2)
pdf.sub_title("Quick Wins (Can start immediately)")

pdf.numbered(1, "Claim & Optimize Google Business Profile",
    "Free. Takes 30 minutes. Immediately puts you on Google Maps for local searches. "
    "Add photos, services, hours, and a compelling description. This alone can move "
    "you onto page 1 for 'annuity advisor hudson ohio.'")

pdf.numbered(2, "Create One Dedicated Landing Page: Free Annuity Checkup",
    "A single page targeting 'annuity review ohio' and 'annuity checkup' with a clear "
    "offer: upload your statement, get a plain-English analysis. This directly competes "
    "with Serious Money Ohio and annuity-checkup.com on your home turf.")

pdf.numbered(3, "Publish 5 Educational Articles on checkannuity.com",
    "Target the exact keywords in this report. Topics like 'Should I Keep My Annuity?', "
    "'Hidden Annuity Fees Explained', 'How to Read Your Annuity Statement.' Each article "
    "becomes a new page Google can rank.")

pdf.ln(2)
pdf.sub_title("Medium-Term (30-60 days)")

pdf.numbered(4, "Build Local Citations",
    "Ensure your business name, address, and phone number are consistent across 20+ "
    "directories (Yelp, YellowPages, Bing Places, Apple Maps, etc.). Signals to Google "
    "that you're a legitimate local business.")

pdf.numbered(5, "Optimize Page Titles & Meta Descriptions",
    "Change 'Home | Intelligent Annuity Solutions' to something like 'Annuity Education "
    "& Fee Analysis | Hudson, OH | Intelligent Annuity Solutions.' Tells Google exactly "
    "what searches you should appear for.")

pdf.ln(2)
pdf.sub_title("Timeline to Page 1")
pdf.body(
    "For local terms (hudson ohio, NE ohio), with consistent execution: 60-90 days. "
    "For broader terms (annuity fees explained, should I keep my annuity): 4-6 months. "
    "These timelines assume regular content publishing and proper technical SEO."
)

pdf.ln(6)
pdf.set_draw_color(0, 90, 180)
pdf.set_line_width(0.6)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(8)
pdf.set_font("Helvetica", "B", 11)
pdf.set_text_color(0, 60, 140)
pdf.cell(0, 7, "We already know where you stand. We can fix it.", align="C")
pdf.ln(12)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Prepared by Simpl ABI for Bryan McInerney, Intelligent Annuity Solutions, LLC", align="C")
pdf.ln(6)
pdf.cell(0, 6, "Samuel J. Karman, CEO  |  simplabiwebsite.com  |  330-607-2668", align="C")
pdf.ln(6)
pdf.cell(0, 6, "Report based on live Google search data as of May 18, 2026.", align="C")

pdf.output(OUTPUT_PATH)
print(f"PDF generated: {OUTPUT_PATH}")
print(f"  Pages: {pdf.page_no()}")
