"""
Event Monitor — Automatically finds relevant NE Ohio events on Eventbrite
and kicks off attendee scraping via Apify.

Run daily via Task Scheduler or cron.
Finds events → stores event details → triggers attendee scraping.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTS_FILE = os.path.join(OUTPUT_DIR, "monitored_events.json")


# Search queries that find events Mac's ideal clients attend
SEARCH_QUERIES = [
    "business networking northeast ohio",
    "financial planning akron cleveland",
    "dental association ohio",
    "medical society northeast ohio",
    "bar association akron cleveland",
    "business owner summit ohio",
    "retirement planning seminar ohio",
    "chamber of commerce hudson akron",
    "wealth management event cleveland",
    "professional networking summit county",
]

# Locations to search
LOCATIONS = [
    "Akron, OH",
    "Cleveland, OH",
    "Hudson, OH",
    "Canton, OH",
    "Medina, OH",
]


def search_eventbrite_events(query, location, max_events=5):
    """
    Search Eventbrite for events via Apify scraper.
    Returns event URLs and metadata.
    """
    if not APIFY_API_TOKEN:
        print("[Apify] No token. Set APIFY_API_TOKEN in .env")
        return []

    url = "https://api.apify.com/v2/acts/drobnikj~eventbrite-scraper/run-sync-get-dataset-items"
    
    params = {"token": APIFY_API_TOKEN}
    payload = {
        "searchQuery": query,
        "location": location,
        "maxEvents": max_events,
        "startDate": datetime.now().strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    }

    try:
        resp = requests.post(url, json=payload, params=params, timeout=120)
        if resp.status_code == 200:
            events = resp.json()
            print(f"  Found {len(events)} events for '{query}' in {location}")
            return events
        else:
            print(f"  [Error] Status {resp.status_code} for '{query}'")
            return []
    except requests.exceptions.RequestException as e:
        print(f"  [Error] {e}")
        return []


def search_meetup_events(query, location):
    """
    Search Meetup.com for relevant events.
    Uses Meetup's public search (no API key needed for basic search).
    """
    # Meetup doesn't require auth for basic event discovery
    # We can use their public search endpoint
    url = "https://api.meetup.com/find/upcoming_events"
    params = {
        "text": query,
        "lat": 41.24,   # Hudson, OH
        "lon": -81.44,
        "radius": 50,   # miles
        "page": 10,
    }
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("events", [])
            return [{
                "name": e.get("name", ""),
                "url": e.get("link", ""),
                "date": e.get("local_date", ""),
                "venue": e.get("venue", {}).get("name", ""),
                "city": e.get("venue", {}).get("city", ""),
                "rsvp_count": e.get("yes_rsvp_count", 0),
                "group": e.get("group", {}).get("name", ""),
                "source": "meetup",
            } for e in events]
        return []
    except requests.exceptions.RequestException:
        return []


def load_monitored_events():
    """Load previously found events to avoid duplicates."""
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_monitored_events(events):
    """Save events list to file."""
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)


def is_relevant_event(event):
    """
    Filter events for relevance to Mac's target audience.
    Returns True if the event likely has HNW business owners attending.
    """
    name = (event.get("name") or "").lower()
    desc = (event.get("description") or "").lower()
    text = name + " " + desc
    
    # High-relevance keywords
    high_relevance = [
        "business owner", "entrepreneur", "executive",
        "dental", "dentist", "physician", "medical", "attorney", "lawyer",
        "financial planning", "retirement", "wealth",
        "chamber of commerce", "rotary", "networking",
        "cpa", "accounting", "tax planning",
    ]
    
    # Low-relevance (filter out)
    exclude = [
        "student", "intern", "job fair", "hiring",
        "free food", "happy hour only", "yoga",
        "kids", "children", "family fun",
    ]
    
    if any(ex in text for ex in exclude):
        return False
    
    return any(rel in text for rel in high_relevance)


def run_event_monitor():
    """
    Main event monitoring routine.
    Searches for events, filters for relevance, stores new finds.
    """
    print("\n" + "=" * 50)
    print("EVENT MONITOR")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    existing = load_monitored_events()
    existing_urls = {e.get("url") for e in existing}
    new_events = []
    
    # Search Eventbrite
    print("\n[Eventbrite] Searching...")
    for query in SEARCH_QUERIES[:5]:  # Limit to avoid rate limits
        for location in LOCATIONS[:2]:
            events = search_eventbrite_events(query, location, max_events=3)
            for event in events:
                url = event.get("url", "")
                if url and url not in existing_urls and is_relevant_event(event):
                    event["source"] = "eventbrite"
                    event["found_at"] = datetime.now().isoformat()
                    event["attendees_scraped"] = False
                    new_events.append(event)
                    existing_urls.add(url)
    
    # Search Meetup
    print("\n[Meetup] Searching...")
    for query in SEARCH_QUERIES[:3]:
        events = search_meetup_events(query, "Akron, OH")
        for event in events:
            url = event.get("url", "")
            if url and url not in existing_urls and is_relevant_event(event):
                event["found_at"] = datetime.now().isoformat()
                event["attendees_scraped"] = False
                new_events.append(event)
                existing_urls.add(url)
    
    # Save all events
    all_events = existing + new_events
    save_monitored_events(all_events)
    
    print(f"\n{'=' * 50}")
    print(f"New events found: {len(new_events)}")
    print(f"Total events tracked: {len(all_events)}")
    
    if new_events:
        print("\nNew events:")
        for e in new_events[:10]:
            print(f"  - {e.get('name', 'Untitled')} ({e.get('source')}) — {e.get('date', 'TBD')}")
            print(f"    {e.get('url', '')}")
    
    print("=" * 50)
    return new_events


if __name__ == "__main__":
    run_event_monitor()
