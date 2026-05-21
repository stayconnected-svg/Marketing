# Automated Lead Pipeline — Setup Guide

## Overview

This is the fully automated lead generation system for Mac (and future clients). No OpenClaw required — runs on standard tools with built-in automation.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              AUTOMATED (runs daily)                   │
│                                                      │
│  lead_pipeline.py ──→ Searches Apollo.io             │
│                  ──→ Checks RB2B visitors             │
│                  ──→ Loads event attendees            │
│                  ──→ Scores all leads                 │
│                  ──→ Drafts personalized messages     │
│                  ──→ Pushes to Instantly.ai           │
│                  ──→ Outputs daily_leads_YYYY-MM-DD   │
│                                                      │
│  event_monitor.py ─→ Searches Eventbrite/Meetup      │
│                   ─→ Finds relevant NE Ohio events    │
│                   ─→ Stores for attendee scraping     │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          ALWAYS-ON SERVICES                          │
│                                                      │
│  Instantly.ai ─── Sends emails automatically         │
│                   Warms up mailboxes                  │
│                   Auto follow-ups on schedule         │
│                                                      │
│  RB2B ─────────── Identifies site visitors 24/7      │
│                   Sends webhooks on new visitors      │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          MANUAL (15 min/day by Jacob)                 │
│                                                      │
│  LinkedIn ─────── Open daily_leads CSV               │
│                   Copy pre-written messages           │
│                   Send 10-15 connection requests      │
│                   Send 3-5 InMails (Sales Nav)        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Setup Steps

### 1. Sign up for services


| Service         | URL                                                                                            | Plan         | Cost              |
| --------------- | ---------------------------------------------------------------------------------------------- | ------------ | ----------------- |
| Apollo.io       | [https://app.apollo.io](https://app.apollo.io)                                                 | Professional | $79/mo            |
| Instantly.ai    | [https://instantly.ai](https://instantly.ai)                                                   | Growth       | $37/mo            |
| Apify           | [https://apify.com](https://apify.com)                                                         | Free tier    | $0 (5$/mo credit) |
| RB2B            | [https://rb2b.com](https://rb2b.com)                                                           | Free tier    | $0 (150 IDs/mo)   |
| Sales Navigator | [https://business.linkedin.com/sales-solutions](https://business.linkedin.com/sales-solutions) | Core         | $99/mo            |


**Total: ~$215/mo**

### 2. Get API keys

Copy `.env.example` to `.env` and fill in:

```
APOLLO_API_KEY=your_key
APIFY_API_TOKEN=your_token
INSTANTLY_API_KEY=your_key
```

### 3. Configure Apollo.io searches

In Apollo's dashboard:

- Create saved searches for each vertical (dentists, doctors, lawyers)
- Filter: Location = NE Ohio cities, Title = Owner/Partner/President
- Industry tags will vary — note the IDs and update `lead_pipeline.py`

### 4. Set up Instantly.ai

1. Buy 2 sending domains (per Domain_Setup_Guide.md)
2. Set up Google Workspace mailboxes
3. Add mailboxes to Instantly for warmup (takes 14-21 days)
4. Create campaign with email sequence from outreach_templates.md
5. Note the campaign_id for the pipeline script

### 5. Install tracking on checkannuity.com

**Google Analytics 4 (viewership trends):**

1. Go to https://analytics.google.com → Admin → Create Property
2. Name it "checkannuity.com", set timezone/currency
3. Copy the Measurement ID (e.g. `G-ABC123XYZ`)
4. Replace `G-XXXXXXXXXX` in all HTML files under `mac_site_demo/` and `mac-demo-hosted/`
5. For the API (viewership_monitor.py):
   - Enable "Google Analytics Data API" in Google Cloud Console
   - Create a service account, download the JSON key as `ga4_credentials.json`
   - Add the service account email as a Viewer on your GA4 property
   - Set `GA4_PROPERTY_ID` and `GA4_CREDENTIALS_PATH` in `.env`

**RB2B (visitor identification):**

1. Sign up at https://rb2b.com (free: 150 IDs/mo)
2. Copy your pixel ID from the RB2B dashboard
3. Replace `YOUR_PIXEL_ID` in all HTML files under `mac_site_demo/` and `mac-demo-hosted/`
4. Configure webhook in RB2B dashboard to POST to your endpoint (or write to `rb2b_visitors.json` locally)

### 6. Schedule daily runs

**Windows Task Scheduler:**

- `viewership_monitor.py` — Run daily at 4:30 AM (before lead pipeline)
- `event_monitor.py` — Run daily at 5:00 AM
- `lead_pipeline.py` — Run daily at 6:00 AM

**Or use a server cron (if deployed):**

```
30 4 * * * cd /path/to/Marketing && python viewership_monitor.py
0  5 * * * cd /path/to/Marketing && python event_monitor.py
0  6 * * * cd /path/to/Marketing && python lead_pipeline.py
```

---

## Daily Workflow (Jacob's 15 minutes)

1. Check email for the daily_leads CSV (or open it directly)
2. Open LinkedIn Sales Navigator
3. For top 10-15 leads:
  - View their profile (warms the connection)
  - Copy the pre-written LinkedIn message from the CSV
  - Send connection request with the personalized note
4. For top 3-5 high-score leads:
  - Send InMail with longer personalized message
5. Done. Emails are sending automatically via Instantly.

---

## Lead Scoring (how priority is determined)


| Signal                                          | Points |
| ----------------------------------------------- | ------ |
| Business owner/partner title                    | +30    |
| Target industry (dental/medical/legal)          | +25    |
| Visited checkannuity.com (RB2B)                 | +25    |
| Located in priority cities (Hudson, Stow, etc.) | +20    |
| Located in tier-2 cities (Akron, Cleveland)     | +15    |
| Event attendee                                  | +15    |
| Director/VP level title                         | +20    |
| Apollo database match                           | +10    |
| Has verified email                              | +5     |
| Has LinkedIn URL                                | +5     |


**Score 70+** = Top priority (InMail + email + LinkedIn)
**Score 50-69** = High priority (email + LinkedIn)
**Score 30-49** = Standard (email sequence only)
**Score <30** = Low priority (batch email only)

---

## Scaling to Future Clients

To add a new client:

1. Duplicate `lead_pipeline.py` or add client config
2. Change search filters (industry, location, titles)
3. Change message templates
4. Create new Instantly campaign
5. Same infrastructure, new targeting

The whole system is client-agnostic. Swap the filters and templates = new client pipeline in 30 minutes.

---

## What Happens When OpenClaw Arrives

OpenClaw replaces the cron jobs + adds AI decision-making:

- Smarter lead scoring (learns from which leads convert)
- Dynamic message personalization (uses recent LinkedIn posts/news)
- Auto-decides when to escalate (email only → add LinkedIn → add InMail)
- Monitors reply sentiment and adjusts sequences
- Single dashboard for all clients

But nothing is blocked on it. The current stack works fully without it.