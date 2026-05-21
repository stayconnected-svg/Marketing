from fpdf import FPDF
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "Bryan_McInerney_Deal_Overview.pdf")


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "SIMPL ABI  |  INTERNAL STRATEGY DOCUMENT  |  MAY 15, 2026", align="C")
        self.ln(6)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 70, 150)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 120, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, title)
        self.ln(7)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(x + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def numbered_item(self, num, title, desc):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 70, 150)
        self.cell(8, 6, str(num) + ".")
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, title)
        self.ln(6)
        if desc:
            self.set_x(self.get_x() + 8)
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 5.5, desc)
            self.ln(2)

    def callout_box(self, text):
        self.ln(2)
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.4)
        x = self.get_x()
        y = self.get_y()
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(x + 3)
        # Calculate height needed
        w = self.w - self.l_margin - self.r_margin - 6
        lines = self.multi_cell(w, 5.5, text, split_only=True)
        h = len(lines) * 5.5 + 8
        self.rect(x, y, self.w - self.l_margin - self.r_margin, h, style="DF")
        self.set_xy(x + 5, y + 4)
        self.multi_cell(w, 5.5, text)
        self.ln(4)


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(0, 50, 120)
pdf.cell(0, 14, "First Customer Deal Overview", align="C")
pdf.ln(12)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Bryan McInerney  /  Intelligent Annuity Solutions, LLC", align="C")
pdf.ln(14)

# ── SECTION 1: WHO IS BRYAN ──
pdf.section_title("1. Who Is Bryan McInerney?")

pdf.body_text(
    "Bryan \"Mac\" McInerney is the founder of Intelligent Annuity Solutions, LLC, "
    "based in Hudson, Ohio. He is a financial advisor who offers securities through "
    "LPL Financial (the largest independent broker-dealer in the U.S., regulated by "
    "FINRA and the SEC). His business website is www.checkannuity.com."
)
pdf.body_text(
    "Bryan specializes in annuity and insurance-based financial strategies. He helps "
    "clients manage taxes, reduce fees, and optimize portfolio returns while reducing "
    "risk. He met Sam for coffee on May 15, 2026, was enthusiastic about what Simpl ABI "
    "does, and explicitly asked to engage us to assist his prospecting efforts."
)

pdf.sub_title("Contact Information")
pdf.bullet("Email: bryan.mcinerney@lpl.com")
pdf.bullet("Phone (voice only): (614) 404-3829")
pdf.bullet("Toll-free: 866-614-2828")
pdf.bullet("Address: 20 Fox Trace Lane, Hudson, Ohio")
pdf.bullet("Website: www.checkannuity.com")

# ── SECTION 2: WHAT BRYAN DOES ──
pdf.section_title("2. What Bryan Does (His Business)")

pdf.body_text(
    "Bryan sells annuity and insurance products to help clients in three main ways:"
)
pdf.bullet("Manage taxes using insurance-based strategies")
pdf.bullet("Eliminate unnecessary fees that traditional wealth managers charge")
pdf.bullet("Increase overall portfolio returns while reducing risk exposure")

pdf.body_text(
    "His pitch to prospects: \"You probably already have a wealth manager, but are you "
    "really getting the value for the fees you're paying? I can use insurance solutions "
    "to do better.\""
)

# ── SECTION 3: HIS IDEAL CLIENTS ──
pdf.section_title("3. Bryan's Ideal Client Profiles")

pdf.numbered_item(1, "High Net Worth Business Owners",
    "Tax-sensitive and fee-conscious. Already have a wealth manager but may not be "
    "getting adequate value. Bryan positions insurance solutions as a better alternative "
    "for tax management and fee elimination.")

pdf.numbered_item(2, "Near-Retirees Needing Growth Without Risk",
    "People in or approaching retirement who need to stay invested for growth but "
    "absolutely cannot afford a market loss. Annuities provide downside protection.")

pdf.numbered_item(3, "Retirees Needing More Income",
    "People in or near retirement who need additional income streams. Annuity products "
    "can provide guaranteed income.")

pdf.numbered_item(4, "People with Existing Annuities",
    "Prospects who already own annuities but could benefit from refinancing into better, "
    "more fee-sensitive contracts. This is a comparison/upgrade play.")

# ── SECTION 4: TARGET INDUSTRIES ──
pdf.section_title("4. Target Industries")

pdf.body_text(
    "Bryan identified 7 specific industries to target. The common thread: all are "
    "business-owner-heavy industries where the owners tend to be high net worth, "
    "tax-sensitive, and likely already have advisors who may be underperforming."
)

industries = [
    "Doctors / Medical Practices",
    "Dentists / Dental Practices",
    "Lawyers / Law Firms",
    "Car Dealerships",
    "Powersports Dealers",
    "Apparel and Promotional Companies",
    "Trucking Companies",
]
for ind in industries:
    pdf.bullet(ind)

# ── SECTION 5: WHAT HE NEEDS FROM US ──
pdf.add_page()
pdf.section_title("5. What Bryan Needs From Simpl ABI")

pdf.body_text(
    "Bryan's core need is simple: he wants his customer outreach and marketing handled "
    "for him so he can focus entirely on closing sales. He does not want to prospect. "
    "He wants warm leads delivered to him."
)

pdf.sub_title("Specifically, he needs:")
pdf.bullet("Automated prospecting targeting his 7 industries in his geographic area")
pdf.bullet("Outreach messaging tailored to his 4 ideal client profiles")
pdf.bullet("A pipeline that identifies, contacts, and warms up prospects without his involvement")
pdf.bullet("All content to be compliant with LPL Financial's strict marketing rules (see Section 6)")

pdf.callout_box(
    "THE VISION: Bryan wakes up, checks his calendar, and sees meetings with "
    "pre-qualified prospects who already understand what he does and want to talk. "
    "Simpl ABI handles everything before that meeting."
)

# ── SECTION 6: THE LPL COMPLIANCE CONSTRAINT ──
pdf.section_title("6. The LPL Compliance Constraint")

pdf.body_text(
    "This is the single most important factor in how we design our service for Bryan."
)

pdf.sub_title("What is LPL Financial?")
pdf.body_text(
    "LPL Financial is the broker-dealer Bryan is registered through. It is the largest "
    "independent broker-dealer in the U.S. Because Bryan offers securities through LPL, "
    "all of his public-facing communications are regulated by FINRA (Financial Industry "
    "Regulatory Authority) and the SEC. LPL enforces these rules on Bryan's behalf."
)

pdf.sub_title("The Rule")
pdf.callout_box(
    "Bryan's exact words: \"I cannot send emails, correspondence, post on social, "
    "or put myself out to the public without first obtaining approval from LPL.\""
)

pdf.body_text(
    "This means every piece of marketing or outreach that goes out with Bryan's name "
    "on it must be reviewed and approved by LPL's compliance team BEFORE it is sent. "
    "This creates a speed bottleneck that directly affects how Simpl ABI delivers value."
)

pdf.sub_title("What This Means for Us")
pdf.body_text(
    "If every individual email or social post needs LPL approval before sending, our "
    "automation cannot run freely. We would generate content and then wait in a queue. "
    "This kills the core value proposition of zero-effort marketing."
)

# ── SECTION 7: THE CRITICAL QUESTION ──
pdf.section_title("7. The Critical Question We Must Answer")

pdf.body_text(
    "Before we can design our service for Bryan, we need to understand exactly how "
    "LPL's approval process works in practice. There may be paths that let us move "
    "fast without hitting the compliance bottleneck every time."
)

pdf.sub_title("Possible paths around the bottleneck:")

pdf.numbered_item(1, "Pre-Approved Templates",
    "Can Bryan get a batch of outreach templates approved by LPL once, and then reuse "
    "them freely? If yes, we build a library of 20-30 compliant templates, get them "
    "approved in one shot, and our automation fills in personalization details and "
    "sends at will. This is the ideal scenario.")

pdf.numbered_item(2, "Correspondence vs. Retail Communications",
    "FINRA distinguishes between \"correspondence\" (1-to-1 or small group messages) "
    "and \"retail communications\" (25+ people in 30 days). Correspondence often has "
    "lighter review requirements -- sometimes only supervisory review after the fact, "
    "not pre-approval. If Bryan's outreach is personalized 1-to-1, the rules may be "
    "significantly looser.")

pdf.numbered_item(3, "Non-Securities Content",
    "If outreach does NOT mention specific investment products, returns, or strategies "
    "-- for example, a simple introduction email saying \"I help business owners in your "
    "industry plan for their financial future, would you like to meet?\" -- does that "
    "even trigger compliance review? There may be a lane for general relationship-building "
    "that avoids securities marketing rules entirely.")

pdf.numbered_item(4, "Insurance-Only Content",
    "Bryan uses \"insurance solutions\" as a core part of his offering. Insurance products "
    "(unless they are variable annuities) are often NOT securities and fall under state "
    "insurance regulations, not FINRA. If some outreach focuses purely on insurance, "
    "LPL's approval process may not apply at all.")

pdf.callout_box(
    "KEY QUESTION FOR BRYAN: \"Can you get outreach templates pre-approved by LPL so "
    "that once a template is cleared, you can send it as many times as you want to "
    "different prospects? And does 1-to-1 personalized correspondence require the same "
    "approval as mass marketing?\""
)

# ── SECTION 8: COMPLIANCE WORD RULES ──
pdf.add_page()
pdf.section_title("8. Compliance Word Rules (Summary)")

pdf.body_text(
    "Bryan provided a 16-page LPL compliance guide listing dozens of words and phrases "
    "that are banned or restricted in marketing materials. We have fully digested this "
    "document. Below is a summary of the most critical rules. Every piece of content "
    "we generate must be checked against these."
)

pdf.sub_title("Investment-Related Banned Terms (Examples)")
pdf.bullet("\"Guaranteed / Secure / Safe\" -- Use instead: manage risk, preserve, conservative, mitigate")
pdf.bullet("\"Achieve / Realize / Ensure\" -- Use instead: pursue, work toward, seek, aim")
pdf.bullet("\"Trusted / Objective / Unbiased\" -- Use instead: personalized, collaborative, experienced")
pdf.bullet("\"Unique / Innovative / Cutting-edge\" -- Use instead: independent, comprehensive, specialized")
pdf.bullet("\"Peace of mind / Sleep at night\" -- Use instead: confidence, meaningful")
pdf.bullet("\"Maximize / Optimize\" (as certainty) -- OK when framed as a goal, not a promise")
pdf.bullet("\"Eliminate / Minimize risk\" -- Use instead: manage, mitigate, position")
pdf.bullet("\"Best / Superior / Elite / World-class\" -- Use instead: well-regarded, dynamic, quality")
pdf.bullet("\"Expert / Guru\" -- Use instead: professional, specialist, seasoned, qualified")
pdf.bullet("\"Don't miss out / Act fast / Opportunity of a lifetime\" -- Never (false urgency)")
pdf.bullet("\"Always / Never\" (market absolutes) -- Use instead: historically, often, rarely")

pdf.sub_title("Business-Related Banned Terms (Examples)")
pdf.bullet("\"Financial planning firm\" -- Only if the entity is a Registered Investment Advisor (RIA)")
pdf.bullet("\"Affiliated with LPL\" -- Only individuals can say this, not DBA entities")
pdf.bullet("\"We don't sell products\" -- Registered reps are legally salespeople")
pdf.bullet("\"Fully licensed\" -- No such designation exists; list actual licenses instead")
pdf.bullet("Negative remarks about competitors, other advisors, or prior firms -- Never")

pdf.sub_title("Banned Images")
pdf.bullet("Money trees -- Never allowed in any context")
pdf.bullet("Gold bars / coins -- Never allowed in any context")
pdf.bullet("Golden eggs, upward arrows -- Context dependent, generally avoid")

pdf.callout_box(
    "OUR COMPETITIVE ADVANTAGE: Generic marketing agencies do not know these rules. "
    "They would produce content full of banned terms, Bryan would submit it to LPL, "
    "it would get rejected, and weeks would be wasted. We bake compliance into content "
    "generation from day one. This is a genuine moat."
)

# ── SECTION 9: WHY THIS DEAL MATTERS ──
pdf.add_page()
pdf.section_title("9. Why This Deal Matters")

pdf.numbered_item(1, "First Customer = Proof of Concept",
    "Bryan is Simpl ABI's first potential paying customer. Successfully delivering for "
    "him proves our business model works in the real world.")

pdf.numbered_item(2, "Built-In Referral Channel",
    "Bryan explicitly said he wants to \"tell his friends about your business.\" If we "
    "deliver results, he becomes an active evangelist. Financial advisors know other "
    "financial advisors -- this could open an entire vertical.")

pdf.numbered_item(3, "Compliance Expertise as a Moat",
    "If we master FINRA/LPL compliance for Bryan, we can replicate this for every "
    "financial advisor registered through LPL (or any other broker-dealer). There are "
    "roughly 22,000 advisors at LPL alone. The compliance problem is universal in this "
    "industry, and almost nobody solves it well.")

pdf.numbered_item(4, "Repeatable Playbook",
    "Bryan's 7 target industries, 4 client profiles, and compliance constraints give us "
    "a concrete, specific use case to build around. Once we nail it, we can templatize "
    "the entire playbook for the next financial advisor client.")

# ── SECTION 10: NEXT STEPS ──
pdf.section_title("10. Immediate Next Steps")

pdf.numbered_item(1, "Get Clarity on LPL Approval Process",
    "Ask Bryan the critical question: can templates be pre-approved for reuse? What "
    "about 1-to-1 correspondence? What about non-securities or insurance-only content? "
    "This determines our entire service architecture.")

pdf.numbered_item(2, "Review www.checkannuity.com",
    "Study Bryan's existing website to understand his current positioning, tone, and "
    "branding so our outreach content aligns with how he already presents himself.")

pdf.numbered_item(3, "Research the 7 Target Industries",
    "Build prospect lists for Doctors, Dentists, Lawyers, Car Dealers, Powersports, "
    "Apparel/Promo, and Trucking companies in Bryan's geographic area (Hudson, OH / "
    "greater Cleveland-Akron market).")

pdf.numbered_item(4, "Draft Compliant Outreach Templates",
    "Create initial outreach email and messaging templates that are pre-vetted against "
    "the LPL compliance guide. These become the foundation of the automated pipeline.")

pdf.numbered_item(5, "Define Service Scope and Pricing",
    "Based on what we learn from steps 1-4, define exactly what Simpl ABI delivers "
    "to Bryan, how it works, and what it costs. Present a formal proposal.")

pdf.ln(10)
pdf.set_draw_color(0, 102, 204)
pdf.set_line_width(0.6)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Prepared for internal discussion between Sam Karman and Jacob.", align="C")
pdf.ln(6)
pdf.cell(0, 6, "All information sourced from Bryan McInerney's email dated May 15, 2026.", align="C")

pdf.output(OUTPUT_PATH)
print(f"PDF generated: {OUTPUT_PATH}")
