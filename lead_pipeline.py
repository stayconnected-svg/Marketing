"""
Automated Lead Pipeline for Mac (and future clients).
Pulls leads from multiple sources, enriches, scores, and outputs a daily action list.

Sources:
  1. Apollo.io — B2B contact database (dentists, doctors, lawyers in NE Ohio)
  2. Apify — Event attendee scraping (Eventbrite, Luma, Meetup)
  3. RB2B — Website visitor identification (checkannuity.com)

Output:
  - Daily CSV of scored leads ready for outreach
  - Pre-drafted personalized messages for LinkedIn (manual send)
  - Auto-feed into Instantly.ai for email sequences

Requirements:
  pip install requests python-dotenv pandas
  
Environment variables (.env):
  APOLLO_API_KEY=your_key_here
  APIFY_API_TOKEN=your_token_here
  INSTANTLY_API_KEY=your_key_here (optional, for direct API push)
"""

import os
import json
import csv
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from viewership_monitor import get_viewership_for_pipeline

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────
# SOURCE 1: Apollo.io — Contact Database Search
# ─────────────────────────────────────────────

def apollo_search_leads(
    titles=None,
    industries=None,
    locations=None,
    per_page=25,
    page=1
):
    """
    Search Apollo.io's database for contacts matching criteria.
    Returns enriched contacts with email, phone, company info.
    """
    if not APOLLO_API_KEY:
        print("[Apollo] No API key set. Set APOLLO_API_KEY in .env")
        return []

    url = "https://api.apollo.io/api/v1/mixed_people/search"
    
    payload = {
        "api_key": APOLLO_API_KEY,
        "page": page,
        "per_page": per_page,
        "person_titles": titles or ["Owner", "Partner", "President", "CEO", "Founder"],
        "person_locations": locations or ["Hudson, Ohio", "Akron, Ohio", "Cleveland, Ohio", "Cuyahoga Falls, Ohio", "Stow, Ohio", "Twinsburg, Ohio", "Kent, Ohio", "Medina, Ohio"],
        "organization_industry_tag_ids": industries or [],
        "contact_email_status": ["verified"],
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        leads = []
        for person in data.get("people", []):
            leads.append({
                "source": "apollo",
                "first_name": person.get("first_name", ""),
                "last_name": person.get("last_name", ""),
                "title": person.get("title", ""),
                "company": person.get("organization", {}).get("name", ""),
                "industry": person.get("organization", {}).get("industry", ""),
                "city": person.get("city", ""),
                "state": person.get("state", ""),
                "email": person.get("email", ""),
                "phone": person.get("phone_numbers", [{}])[0].get("sanitized_number", "") if person.get("phone_numbers") else "",
                "linkedin_url": person.get("linkedin_url", ""),
                "company_size": person.get("organization", {}).get("estimated_num_employees", ""),
                "score": 0,
                "scraped_at": datetime.now().isoformat(),
            })
        
        print(f"[Apollo] Found {len(leads)} leads (page {page})")
        return leads
    
    except requests.exceptions.RequestException as e:
        print(f"[Apollo] Error: {e}")
        return []


def apollo_search_by_vertical(vertical="dentists"):
    """Pre-built searches for Mac's target verticals."""
    verticals = {
        "dentists": {
            "titles": ["Owner", "Partner", "Dentist", "DDS", "DMD", "President"],
            "industries": [],  # Apollo industry IDs — configure after signup
            "locations": ["Hudson, Ohio", "Akron, Ohio", "Cleveland, Ohio", "Canton, Ohio", "Youngstown, Ohio", "Medina, Ohio", "Cuyahoga Falls, Ohio"],
        },
        "doctors": {
            "titles": ["Owner", "Partner", "Physician", "MD", "DO", "President", "Medical Director"],
            "industries": [],
            "locations": ["Hudson, Ohio", "Akron, Ohio", "Cleveland, Ohio", "Canton, Ohio", "Youngstown, Ohio", "Medina, Ohio"],
        },
        "lawyers": {
            "titles": ["Owner", "Partner", "Managing Partner", "Attorney", "Principal"],
            "industries": [],
            "locations": ["Hudson, Ohio", "Akron, Ohio", "Cleveland, Ohio", "Canton, Ohio", "Youngstown, Ohio", "Medina, Ohio"],
        },
    }
    
    config = verticals.get(vertical, verticals["dentists"])
    return apollo_search_leads(
        titles=config["titles"],
        industries=config["industries"],
        locations=config["locations"],
        per_page=50
    )


# ─────────────────────────────────────────────
# SOURCE 2: Apify — Event Attendee Scraping
# ─────────────────────────────────────────────

def apify_run_eventbrite_scraper(search_query="business networking", location="Ohio"):
    """
    Run Apify Eventbrite scraper to find events and attendees.
    Uses the Eventbrite scraper actor.
    """
    if not APIFY_API_TOKEN:
        print("[Apify] No API token set. Set APIFY_API_TOKEN in .env")
        return []

    url = "https://api.apify.com/v2/acts/drobnikj~eventbrite-scraper/runs"
    
    payload = {
        "searchQuery": search_query,
        "location": location,
        "maxEvents": 10,
    }
    
    headers = {
        "Authorization": f"Bearer {APIFY_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        run_data = resp.json()
        run_id = run_data.get("data", {}).get("id")
        
        print(f"[Apify] Eventbrite scraper started. Run ID: {run_id}")
        print(f"[Apify] Check results at: https://console.apify.com/runs/{run_id}")
        return run_id
    
    except requests.exceptions.RequestException as e:
        print(f"[Apify] Error: {e}")
        return None


def apify_get_results(run_id):
    """Fetch results from a completed Apify run."""
    if not APIFY_API_TOKEN or not run_id:
        return []
    
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[Apify] Error fetching results: {e}")
        return []


def apify_run_luma_scraper(event_url):
    """
    Run Apify Luma guest list scraper for a specific event.
    Returns attendee names, bios, and social profiles.
    """
    if not APIFY_API_TOKEN:
        print("[Apify] No API token set. Set APIFY_API_TOKEN in .env")
        return []

    url = "https://api.apify.com/v2/acts/oheeriye~luma-guest-scraper/runs"
    
    payload = {
        "eventUrl": event_url,
    }
    
    headers = {
        "Authorization": f"Bearer {APIFY_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        run_data = resp.json()
        run_id = run_data.get("data", {}).get("id")
        
        print(f"[Apify] Luma scraper started. Run ID: {run_id}")
        return run_id
    
    except requests.exceptions.RequestException as e:
        print(f"[Apify] Error: {e}")
        return None


# ─────────────────────────────────────────────
# SOURCE 3: RB2B — Website Visitor Identification
# ─────────────────────────────────────────────

def get_rb2b_visitors():
    """
    Placeholder for RB2B webhook/API integration.
    RB2B sends identified visitors via webhook to your endpoint.
    For now, reads from a local JSON file that the webhook writes to.
    """
    visitors_file = os.path.join(OUTPUT_DIR, "rb2b_visitors.json")
    
    if not os.path.exists(visitors_file):
        print("[RB2B] No visitors file found. Set up webhook to write to rb2b_visitors.json")
        return []
    
    try:
        with open(visitors_file, "r") as f:
            visitors = json.load(f)
        
        leads = []
        for v in visitors:
            leads.append({
                "source": "rb2b_site_visitor",
                "first_name": v.get("first_name", ""),
                "last_name": v.get("last_name", ""),
                "title": v.get("title", ""),
                "company": v.get("company", ""),
                "industry": "",
                "city": v.get("city", ""),
                "state": v.get("state", ""),
                "email": v.get("email", ""),
                "phone": "",
                "linkedin_url": v.get("linkedin_url", ""),
                "company_size": "",
                "score": 0,
                "scraped_at": v.get("visited_at", datetime.now().isoformat()),
            })
        
        print(f"[RB2B] {len(leads)} site visitors identified")
        return leads
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"[RB2B] Error: {e}")
        return []


# ─────────────────────────────────────────────
# LEAD SCORING
# ─────────────────────────────────────────────

def score_lead(lead, viewership=None):
    """
    Score a lead 0-100 based on fit for Mac's ideal client.
    Higher = better fit. Viewership trends boost site visitor scores.
    """
    score = 0
    
    title = (lead.get("title") or "").lower()
    industry = (lead.get("industry") or "").lower()
    city = (lead.get("city") or "").lower()
    source = lead.get("source", "")
    
    # Title signals (business owner = highest value)
    owner_titles = ["owner", "partner", "managing partner", "president", "ceo", "founder", "principal"]
    if any(t in title for t in owner_titles):
        score += 30
    elif any(t in title for t in ["director", "vp", "vice president"]):
        score += 20
    elif any(t in title for t in ["manager", "administrator"]):
        score += 10
    
    # Industry signals
    if any(ind in industry for ind in ["dental", "dentist", "medical", "physician", "health", "legal", "law"]):
        score += 25
    elif any(ind in industry for ind in ["financial", "accounting", "insurance"]):
        score += 15
    
    # Location signals (closer to Hudson = better)
    priority_cities = ["hudson", "stow", "twinsburg", "aurora", "kent", "medina", "cuyahoga falls"]
    tier2_cities = ["akron", "cleveland", "canton", "solon", "beachwood", "westlake"]
    
    if any(c in city for c in priority_cities):
        score += 20
    elif any(c in city for c in tier2_cities):
        score += 15
    elif "ohio" in (lead.get("state") or "").lower():
        score += 5
    
    # Source signals (site visitor = highest intent)
    if source == "rb2b_site_visitor":
        score += 25
    elif source == "event_attendee":
        score += 15
    elif source == "apollo":
        score += 10
    
    # Viewership momentum bonus — when traffic is rising, site visitors
    # are higher-signal (something is driving interest)
    if viewership and source == "rb2b_site_visitor":
        if viewership.get("surging"):
            score += 15
            lead["viewership_flag"] = "SURGING"
        elif viewership.get("rising"):
            score += 10
            lead["viewership_flag"] = "RISING"
        if viewership.get("spike_today"):
            score += 5
            lead["viewership_flag"] = "SPIKE_TODAY"
    
    # Has verified email (required for outreach)
    if lead.get("email"):
        score += 5
    
    # Has LinkedIn (allows multi-channel)
    if lead.get("linkedin_url"):
        score += 5
    
    lead["score"] = min(score, 100)
    return lead


# ─────────────────────────────────────────────
# PERSONALIZATION — AI Message Drafting
# ─────────────────────────────────────────────

def draft_linkedin_message(lead):
    """
    Generate a personalized LinkedIn connection request message.
    Under 290 characters. References a signal. No pitch.
    """
    first_name = lead.get("first_name", "")
    company = lead.get("company", "")
    city = lead.get("city", "")
    title = lead.get("title", "")
    source = lead.get("source", "")
    
    if source == "event_attendee":
        event = lead.get("event_name", "a local event")
        return f"Hi {first_name} — noticed we're both connected to {event} in NE Ohio. I work with business owners on annuity strategy. Always good to connect locally."
    
    if source == "rb2b_site_visitor":
        return f"Hi {first_name} — I help {title.lower()}s in {city} understand what their annuities actually cost them. Happy to connect if that's ever relevant."
    
    # Default: location + industry based
    if company:
        return f"Hi {first_name} — fellow NE Ohio professional here (Hudson). I work with business owners like yourself on annuity education and fee analysis. Great to connect."
    
    return f"Hi {first_name} — based in Hudson, OH working with professionals across NE Ohio on annuity clarity. Always good to build the local network."


def draft_email_first_line(lead):
    """
    Generate a personalized first line for email outreach.
    This feeds into Instantly.ai's personalization variables.
    """
    first_name = lead.get("first_name", "")
    company = lead.get("company", "")
    title = lead.get("title", "")
    city = lead.get("city", "")
    
    if lead.get("source") == "rb2b_site_visitor":
        return f"I noticed you were looking into annuity education resources recently — wanted to reach out personally."
    
    if company and city:
        return f"As a fellow {city} professional, I wanted to introduce myself — I help business owners like yourself understand what their annuities actually cost."
    
    if title:
        return f"I work with {title.lower()}s across NE Ohio who want straight answers about their annuity contracts — thought it was worth connecting."
    
    return f"I help business owners in Northeast Ohio cut through annuity complexity — wanted to briefly introduce myself."


# ─────────────────────────────────────────────
# PIPELINE — Daily Run
# ─────────────────────────────────────────────

def run_daily_pipeline(verticals=None):
    """
    Run the full daily pipeline:
    1. Pull leads from all sources
    2. Deduplicate
    3. Score
    4. Draft messages
    5. Output daily action list
    """
    if verticals is None:
        verticals = ["dentists", "doctors", "lawyers"]
    
    all_leads = []
    
    # Source 1: Apollo
    print("\n" + "=" * 50)
    print("DAILY LEAD PIPELINE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n[1/3] Searching Apollo.io...")
    for vertical in verticals:
        leads = apollo_search_by_vertical(vertical)
        all_leads.extend(leads)
    
    # Source 2: RB2B site visitors
    print("\n[2/3] Checking site visitors (RB2B)...")
    visitors = get_rb2b_visitors()
    all_leads.extend(visitors)
    
    # Source 3: Event attendees (from last Apify run)
    print("\n[3/3] Checking event attendee data...")
    event_file = os.path.join(OUTPUT_DIR, "event_attendees.json")
    if os.path.exists(event_file):
        try:
            with open(event_file, "r") as f:
                event_leads = json.load(f)
            for el in event_leads:
                el["source"] = "event_attendee"
            all_leads.extend(event_leads)
            print(f"[Events] {len(event_leads)} event attendees loaded")
        except (json.JSONDecodeError, IOError):
            print("[Events] No event data available")
    else:
        print("[Events] No event data file found")
    
    # Deduplicate by email
    seen_emails = set()
    unique_leads = []
    for lead in all_leads:
        email = lead.get("email", "").lower().strip()
        if email and email not in seen_emails:
            seen_emails.add(email)
            unique_leads.append(lead)
        elif not email:
            unique_leads.append(lead)
    
    print(f"\n[Dedup] {len(all_leads)} total → {len(unique_leads)} unique leads")
    
    # Check viewership trends (GA4)
    viewership = get_viewership_for_pipeline()
    if viewership["rising"]:
        print(f"\n[GA4] ** Viewership is {viewership['status']} — sessions {viewership['session_change_pct']:+.1f}% WoW **")
        if viewership["spike_today"]:
            print(f"[GA4] ** Traffic spike detected TODAY — prioritizing site visitors **")
    elif viewership["status"] != "no_data":
        print(f"\n[GA4] Viewership: {viewership['status']} ({viewership['session_change_pct']:+.1f}% WoW)")

    # Score all leads (boost RB2B visitors when viewership is rising)
    scored_leads = [score_lead(lead, viewership=viewership) for lead in unique_leads]
    scored_leads.sort(key=lambda x: x["score"], reverse=True)
    
    # Draft messages for top leads
    for lead in scored_leads[:20]:
        lead["linkedin_message"] = draft_linkedin_message(lead)
        lead["email_first_line"] = draft_email_first_line(lead)
    
    # Output daily CSV
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(OUTPUT_DIR, f"daily_leads_{today}.csv")
    
    if scored_leads:
        fieldnames = ["score", "source", "first_name", "last_name", "title", "company", 
                      "industry", "city", "state", "email", "phone", "linkedin_url",
                      "linkedin_message", "email_first_line", "scraped_at"]
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(scored_leads)
        
        print(f"\n{'=' * 50}")
        print(f"OUTPUT: {output_file}")
        print(f"Total leads: {len(scored_leads)}")
        if viewership.get("rising") or viewership.get("surging"):
            boosted = [l for l in scored_leads if l.get("viewership_flag")]
            print(f"Viewership: {viewership['status']} ({viewership['session_change_pct']:+.1f}% WoW) — {len(boosted)} leads boosted")
        print(f"Top 5 leads:")
        print("-" * 50)
        for lead in scored_leads[:5]:
            flag = f" [{lead['viewership_flag']}]" if lead.get("viewership_flag") else ""
            print(f"  [{lead['score']}] {lead['first_name']} {lead['last_name']} — {lead['title']} @ {lead['company']} ({lead['city']}){flag}")
            if lead.get("linkedin_message"):
                print(f"       LI: \"{lead['linkedin_message'][:80]}...\"")
        print("=" * 50)
    else:
        print("\n[Pipeline] No leads found. Check API keys in .env")
    
    return scored_leads


# ─────────────────────────────────────────────
# INSTANTLY.AI — Push leads to email sequences
# ─────────────────────────────────────────────

def push_to_instantly(leads, campaign_id=None):
    """
    Push scored leads to Instantly.ai for automated email sequencing.
    Requires INSTANTLY_API_KEY and a campaign_id.
    """
    api_key = os.getenv("INSTANTLY_API_KEY", "")
    if not api_key:
        print("[Instantly] No API key. Set INSTANTLY_API_KEY in .env")
        return
    
    if not campaign_id:
        print("[Instantly] No campaign_id provided. Create a campaign in Instantly first.")
        return
    
    url = "https://api.instantly.ai/api/v1/lead/add"
    
    added = 0
    for lead in leads:
        if not lead.get("email"):
            continue
        
        payload = {
            "api_key": api_key,
            "campaign_id": campaign_id,
            "skip_if_in_workspace": True,
            "leads": [{
                "email": lead["email"],
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "company_name": lead.get("company", ""),
                "personalization": lead.get("email_first_line", ""),
                "custom_variables": {
                    "title": lead.get("title", ""),
                    "city": lead.get("city", ""),
                    "source": lead.get("source", ""),
                    "score": str(lead.get("score", 0)),
                }
            }]
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                added += 1
        except requests.exceptions.RequestException:
            pass
    
    print(f"[Instantly] Pushed {added}/{len(leads)} leads to campaign {campaign_id}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    leads = run_daily_pipeline()
    
    # Uncomment to auto-push high-scoring leads to Instantly:
    # high_score_leads = [l for l in leads if l["score"] >= 50]
    # push_to_instantly(high_score_leads, campaign_id="YOUR_CAMPAIGN_ID")
