"""
LinkedIn Co-Pilot System for Bryan McInerney
=============================================
Generates a daily queue of prospects with pre-written personalized
LinkedIn connection messages. Bryan manually sends them in 5-10 min/day.

Zero automation ON LinkedIn = zero risk of account restriction.

Components:
1. Prospect Scorer - ranks prospects by retirement likelihood / trigger signals
2. LinkedIn URL Generator - builds search URLs to find profiles
3. Message Generator - writes personalized connection notes per prospect
4. Daily Queue - outputs today's 10 targets with everything pre-written
5. Tracker - logs what's been sent, accepted, and followed up
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_DIR = os.path.join(BASE_DIR, "linkedin_queue")
HISTORY_FILE = os.path.join(BASE_DIR, "linkedin_history.json")

DAILY_LIMIT = 10
FOLLOWUP_DELAY_DAYS = 3

# Connection message templates (LinkedIn limit: 300 characters)
# These are designed for Bryan's value prop - annuity/insurance strategies
CONNECTION_TEMPLATES = {
    "dentist_general": [
        "Hi Dr. {last_name}, I work with dentists in {city} on tax-efficient strategies for practice owners — especially around succession and retirement planning. Would love to connect.",
        "Dr. {last_name} — I help dental practice owners in NE Ohio protect more of what they've built through insurance-based financial strategies. Happy to connect here.",
        "Hi Dr. {last_name}, I specialize in working with dentists navigating practice transitions and retirement timing. Always looking to connect with practitioners in {city}.",
    ],
    "dentist_senior": [
        "Dr. {last_name}, I work specifically with established dental practice owners on tax strategies and exit planning. If you're thinking about the next chapter, I'd welcome connecting.",
        "Hi Dr. {last_name} — I help long-tenured dentists evaluate options for reducing tax exposure on practice transitions. Would be glad to connect.",
        "Dr. {last_name}, I partner with dental practice owners who've built something substantial and want to protect it from unnecessary taxes and fees. Happy to connect.",
    ],
    "physician_general": [
        "Dr. {last_name}, I work with physicians in {city} on strategies to reduce hidden fees in retirement plans and manage tax exposure. Would love to connect.",
        "Hi Dr. {last_name} — I specialize in helping physician practice owners with insurance-based financial strategies. Always glad to connect with doctors in NE Ohio.",
        "Dr. {last_name}, I help physicians who feel their current advisory setup isn't optimized for their tax situation. Happy to connect here.",
    ],
    "physician_senior": [
        "Dr. {last_name}, I work with established physicians on reducing 401(k) fees and building tax-efficient retirement income. If that resonates, I'd welcome connecting.",
        "Hi Dr. {last_name} — I help long-tenured physicians evaluate whether their current plan is actually working as hard as they are. Would be glad to connect.",
        "Dr. {last_name}, I specialize in helping physicians approaching retirement protect their earnings from unnecessary tax exposure. Happy to connect.",
    ],
    "attorney_general": [
        "{first_name}, I work with attorneys in {city} on insurance-based strategies for tax management and retirement planning. Would appreciate connecting.",
        "Hi {first_name} — I help attorneys and firm owners in NE Ohio with financial strategies that reduce tax drag and hidden advisory fees. Happy to connect.",
        "{first_name}, I specialize in working with legal professionals on protecting income through strategies most generalist advisors don't offer. Would love to connect.",
    ],
}

# Follow-up message templates (sent after connection is accepted)
FOLLOWUP_TEMPLATES = {
    "dentist": [
        "Thanks for connecting, Dr. {last_name}. I put together a brief piece on how dentists are using insurance-based strategies to reduce taxes on practice sales — happy to share if you're curious. No pressure either way.",
        "Appreciate the connection, Dr. {last_name}. Quick question — have you looked at what the 2026 tax changes might mean for your practice's value? I've been helping dentists model that out. Let me know if that's of interest.",
    ],
    "physician": [
        "Thanks for connecting, Dr. {last_name}. I recently helped a physician in {city} uncover $8K/year in hidden 401(k) fees. I put together a short overview of how that works — happy to share if useful.",
        "Appreciate the connection, Dr. {last_name}. If you're ever curious about what options exist beyond traditional advisory for managing taxes and building retirement income, I'm always glad to chat. No pressure.",
    ],
    "attorney": [
        "Thanks for connecting, {first_name}. I work with several attorneys in NE Ohio on reducing tax exposure through insurance-based strategies. Happy to share a brief overview if that's of interest.",
        "Appreciate the connection, {first_name}. If you've ever felt your financial plan could be more tax-efficient given what you earn, I'd welcome a quick conversation. No pressure at all.",
    ],
}


def load_prospects(industry="dentist"):
    """Load prospect CSV data."""
    filename_map = {
        "dentist": "prospects_dentists.csv",
        "physician": "prospects_doctors.csv",
    }
    filepath = os.path.join(BASE_DIR, filename_map.get(industry, ""))
    if not os.path.exists(filepath):
        print(f"  [!] File not found: {filepath}")
        return []

    prospects = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_industry"] = industry
            prospects.append(row)
    return prospects


def load_history():
    """Load outreach history to avoid contacting same person twice."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"contacted": {}, "accepted": {}, "followed_up": {}}


def save_history(history):
    """Save outreach history."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def score_prospect(prospect):
    """
    Score a prospect 0-100 based on available signals.
    Higher = more likely to be a good fit right now.

    Scoring factors:
    - Credential complexity (multiple degrees = established)
    - City proximity to Hudson (closer = easier meeting)
    - Has organization name (likely practice owner)
    - Specialty (some specialties earn more)
    """
    score = 50  # baseline

    # Practice ownership signal: has organization name
    org = prospect.get("Organization", "").strip()
    if org:
        score += 10

    # High-value specialties
    specialty = prospect.get("Specialty", "").lower()
    high_value_specialties = [
        "oral & maxillofacial surgery", "orthodontics", "periodontics",
        "prosthodontics", "endodontics", "cardiovascular",
        "orthopedic surgery", "dermatology", "ophthalmology",
        "plastic surgery", "gastroenterology", "urology",
    ]
    for hvs in high_value_specialties:
        if hvs in specialty:
            score += 15
            break

    # Proximity to Hudson, OH (Bryan's base)
    close_cities = [
        "hudson", "stow", "twinsburg", "aurora", "macedonia",
        "streetsboro", "kent", "cuyahoga falls", "tallmadge",
        "solon", "brecksville", "broadview heights",
    ]
    medium_cities = [
        "akron", "medina", "fairlawn", "copley", "bath",
        "beachwood", "shaker heights", "chagrin falls",
        "strongsville", "north royalton", "independence",
    ]
    city = prospect.get("City", "").lower()
    if city in close_cities:
        score += 20
    elif city in medium_cities:
        score += 10

    # Multiple credentials = likely more established
    credential = prospect.get("Credential", "")
    if "," in credential or "&" in credential:
        score += 5

    # General practice dentists are more likely to own their practice
    if "general practice" in specialty:
        score += 5

    return min(score, 100)


def generate_linkedin_search_url(prospect):
    """
    Generate a LinkedIn search URL to find this person's profile.
    Bryan clicks this URL and it takes him to LinkedIn search results
    pre-filled with the person's name and location.
    """
    first = prospect.get("First Name", "").title()
    last = prospect.get("Last Name", "").title()
    city = prospect.get("City", "").title()

    # LinkedIn people search URL format
    keywords = f"{first} {last} {city} Ohio"
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords.replace(' ', '%20')}"
    return search_url


def generate_connection_message(prospect):
    """Generate a personalized connection message (max 300 chars)."""
    industry = prospect.get("_industry", "dentist")
    specialty = prospect.get("Specialty", "").lower()

    # Determine template category
    # TODO: Once we have license issue dates, use that to determine "senior"
    # For now, use specialty and credential as proxy
    credential = prospect.get("Credential", "")
    is_senior = "," in credential or len(credential) > 6

    if industry == "dentist":
        template_key = "dentist_senior" if is_senior else "dentist_general"
    elif industry == "physician":
        template_key = "physician_senior" if is_senior else "physician_general"
    else:
        template_key = "attorney_general"

    templates = CONNECTION_TEMPLATES.get(template_key, CONNECTION_TEMPLATES["dentist_general"])
    template = random.choice(templates)

    message = template.format(
        first_name=prospect.get("First Name", "").title(),
        last_name=prospect.get("Last Name", "").title(),
        city=prospect.get("City", "").title(),
        credential=credential,
        organization=prospect.get("Organization", ""),
    )

    # Ensure under 300 chars (LinkedIn limit for connection notes)
    if len(message) > 300:
        message = message[:297] + "..."

    return message


def generate_followup_message(prospect):
    """Generate a follow-up DM for after connection is accepted."""
    industry = prospect.get("_industry", "dentist")
    templates = FOLLOWUP_TEMPLATES.get(industry, FOLLOWUP_TEMPLATES["dentist"])
    template = random.choice(templates)

    message = template.format(
        first_name=prospect.get("First Name", "").title(),
        last_name=prospect.get("Last Name", "").title(),
        city=prospect.get("City", "").title(),
    )
    return message


def generate_daily_queue(industries=None, daily_limit=None):
    """
    Generate today's LinkedIn outreach queue.

    Returns a list of prospects with:
    - Their info
    - LinkedIn search URL
    - Pre-written connection message
    - Score / reason they're a good fit
    """
    if industries is None:
        industries = ["dentist", "physician"]
    if daily_limit is None:
        daily_limit = DAILY_LIMIT

    history = load_history()
    all_prospects = []

    for industry in industries:
        prospects = load_prospects(industry)
        all_prospects.extend(prospects)

    # Filter out already-contacted prospects
    contacted_npis = set(history.get("contacted", {}).keys())
    available = [p for p in all_prospects if p.get("NPI", "") not in contacted_npis]

    if not available:
        print("  [!] All prospects have been contacted. Consider refreshing your lists.")
        return []

    # Filter out non-Ohio (some NPI results leak in from other states)
    available = [p for p in available if p.get("State", "").upper() == "OH"]

    # Score and sort
    for p in available:
        p["_score"] = score_prospect(p)

    available.sort(key=lambda x: x["_score"], reverse=True)

    # Take top N with some randomization in the top tier
    # (don't always send to the exact same scored order — looks more natural)
    top_pool = available[:daily_limit * 3]
    random.shuffle(top_pool)
    selected = sorted(top_pool[:daily_limit], key=lambda x: x["_score"], reverse=True)

    # Generate queue entries
    queue = []
    for prospect in selected:
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "npi": prospect.get("NPI", ""),
            "full_name": prospect.get("Full Name", ""),
            "credential": prospect.get("Credential", ""),
            "organization": prospect.get("Organization", ""),
            "specialty": prospect.get("Specialty", ""),
            "city": prospect.get("City", ""),
            "phone": prospect.get("Phone", ""),
            "industry": prospect.get("_industry", ""),
            "score": prospect.get("_score", 0),
            "linkedin_search_url": generate_linkedin_search_url(prospect),
            "connection_message": generate_connection_message(prospect),
            "followup_message": generate_followup_message(prospect),
            "status": "pending",
        }
        queue.append(entry)

    return queue


def generate_followup_queue(history=None):
    """
    Generate follow-up messages for connections that were accepted.
    Returns prospects who accepted but haven't been followed up yet,
    and whose acceptance was at least FOLLOWUP_DELAY_DAYS ago.
    """
    if history is None:
        history = load_history()

    accepted = history.get("accepted", {})
    followed_up = set(history.get("followed_up", {}).keys())

    followups = []
    cutoff = datetime.now() - timedelta(days=FOLLOWUP_DELAY_DAYS)

    for npi, data in accepted.items():
        if npi in followed_up:
            continue
        accepted_date = datetime.strptime(data.get("accepted_date", "2020-01-01"), "%Y-%m-%d")
        if accepted_date <= cutoff:
            followups.append(data)

    return followups


def save_queue_to_file(queue, followups=None):
    """Save today's queue as a readable text file Bryan can reference."""
    os.makedirs(QUEUE_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(QUEUE_DIR, f"queue_{today}.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  LINKEDIN DAILY QUEUE — {today}\n")
        f.write(f"  Intelligent Annuity Solutions | Bryan McInerney\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"  Today's targets: {len(queue)} new connections\n")
        if followups:
            f.write(f"  Follow-ups ready: {len(followups)} accepted connections to message\n")
        f.write(f"  Estimated time: {len(queue) * 1 + (len(followups) if followups else 0)} minutes\n")
        f.write("\n" + "-" * 70 + "\n")
        f.write("  NEW CONNECTION REQUESTS\n")
        f.write("-" * 70 + "\n\n")

        for i, entry in enumerate(queue, 1):
            f.write(f"  [{i}] {entry['full_name']}, {entry['credential']}\n")
            f.write(f"      {entry['specialty']} | {entry['city']}, OH\n")
            if entry['organization']:
                f.write(f"      Practice: {entry['organization']}\n")
            f.write(f"      Phone: {entry['phone']}\n")
            f.write(f"      Score: {entry['score']}/100\n")
            f.write(f"\n")
            f.write(f"      FIND PROFILE:\n")
            f.write(f"      {entry['linkedin_search_url']}\n")
            f.write(f"\n")
            f.write(f"      CONNECTION MESSAGE (copy/paste):\n")
            f.write(f"      \"{entry['connection_message']}\"\n")
            f.write(f"\n")
            f.write(f"      [ ] Sent  [ ] Not on LinkedIn  [ ] Skip\n")
            f.write(f"\n" + "  " + "." * 60 + "\n\n")

        if followups:
            f.write("\n" + "-" * 70 + "\n")
            f.write("  FOLLOW-UP MESSAGES (accepted connections)\n")
            f.write("-" * 70 + "\n\n")

            for i, entry in enumerate(followups, 1):
                f.write(f"  [{i}] {entry.get('full_name', 'Unknown')}\n")
                f.write(f"      Accepted on: {entry.get('accepted_date', 'Unknown')}\n")
                f.write(f"\n")
                f.write(f"      FOLLOW-UP MESSAGE (copy/paste):\n")
                f.write(f"      \"{entry.get('followup_message', '')}\"\n")
                f.write(f"\n")
                f.write(f"      [ ] Sent  [ ] Skip\n")
                f.write(f"\n" + "  " + "." * 60 + "\n\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("  AFTER SENDING:\n")
        f.write("  Run: python linkedin_copilot.py --mark-sent 1,2,3,4,5,6,7,8,9,10\n")
        f.write("  Or:  python linkedin_copilot.py --mark-sent all\n")
        f.write("=" * 70 + "\n")

    print(f"\n  Queue saved to: {filepath}")
    return filepath


def save_queue_to_csv(queue):
    """Also save as CSV for easy import/tracking."""
    os.makedirs(QUEUE_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(QUEUE_DIR, f"queue_{today}.csv")

    fieldnames = [
        "date", "full_name", "credential", "organization", "specialty",
        "city", "phone", "industry", "score", "linkedin_search_url",
        "connection_message", "status",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(queue)

    print(f"  CSV saved to: {filepath}")
    return filepath


def mark_sent(indices, queue_date=None):
    """Mark prospects as sent in history (prevents re-contacting)."""
    if queue_date is None:
        queue_date = datetime.now().strftime("%Y-%m-%d")

    queue_csv = os.path.join(QUEUE_DIR, f"queue_{queue_date}.csv")
    if not os.path.exists(queue_csv):
        print(f"  [!] No queue found for {queue_date}")
        return

    # Load queue
    with open(queue_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        queue = list(reader)

    # Load history
    history = load_history()
    if "contacted" not in history:
        history["contacted"] = {}

    # Mark selected indices
    if indices == "all":
        indices = list(range(1, len(queue) + 1))

    for idx in indices:
        if 1 <= idx <= len(queue):
            entry = queue[idx - 1]
            npi = entry.get("npi", entry.get("full_name", f"unknown_{idx}"))
            history["contacted"][npi] = {
                "full_name": entry.get("full_name", ""),
                "city": entry.get("city", ""),
                "industry": entry.get("industry", ""),
                "date_sent": queue_date,
                "connection_message": entry.get("connection_message", ""),
                "followup_message": entry.get("followup_message", ""),
            }
            print(f"  Marked as sent: {entry.get('full_name', f'#{idx}')}")

    save_history(history)
    print(f"\n  Total contacted: {len(history['contacted'])}")


def mark_accepted(names_or_npis):
    """Mark connections as accepted (moves them to follow-up queue)."""
    history = load_history()
    if "accepted" not in history:
        history["accepted"] = {}

    contacted = history.get("contacted", {})

    for identifier in names_or_npis:
        # Try to find in contacted history
        found = False
        for npi, data in contacted.items():
            if identifier.lower() in data.get("full_name", "").lower() or identifier == npi:
                history["accepted"][npi] = {
                    **data,
                    "accepted_date": datetime.now().strftime("%Y-%m-%d"),
                }
                print(f"  Marked as accepted: {data.get('full_name', identifier)}")
                found = True
                break
        if not found:
            print(f"  [!] Not found in contacts: {identifier}")

    save_history(history)


def print_stats():
    """Print outreach statistics."""
    history = load_history()
    contacted = len(history.get("contacted", {}))
    accepted = len(history.get("accepted", {}))
    followed_up = len(history.get("followed_up", {}))

    print("\n" + "=" * 50)
    print("  LINKEDIN CO-PILOT STATS")
    print("=" * 50)
    print(f"  Connection requests sent:  {contacted}")
    print(f"  Connections accepted:      {accepted}")
    print(f"  Follow-ups sent:           {followed_up}")
    if contacted > 0:
        print(f"  Acceptance rate:           {accepted/contacted*100:.1f}%")
    print("=" * 50)


def main():
    import sys

    print("\n" + "=" * 60)
    print("  LINKEDIN CO-PILOT — Intelligent Annuity Solutions")
    print("=" * 60)

    args = sys.argv[1:]

    if "--mark-sent" in args:
        idx = args.index("--mark-sent")
        if idx + 1 < len(args):
            val = args[idx + 1]
            if val.lower() == "all":
                mark_sent("all")
            else:
                indices = [int(x.strip()) for x in val.split(",")]
                mark_sent(indices)
        return

    if "--mark-accepted" in args:
        idx = args.index("--mark-accepted")
        if idx + 1 < len(args):
            names = args[idx + 1:]
            mark_accepted(names)
        return

    if "--stats" in args:
        print_stats()
        return

    # Default: generate today's queue
    print("\n  Generating daily queue...")
    print(f"  Daily limit: {DAILY_LIMIT} new connection requests")
    print(f"  Industries: Dentists, Physicians")

    queue = generate_daily_queue()

    if not queue:
        print("\n  [!] No prospects available for today's queue.")
        return

    followups = generate_followup_queue()

    print(f"\n  Generated {len(queue)} prospects for today:")
    for i, entry in enumerate(queue, 1):
        print(f"    {i}. {entry['full_name']} ({entry['specialty']}, {entry['city']}) — Score: {entry['score']}")

    save_queue_to_file(queue, followups)
    save_queue_to_csv(queue)
    print_stats()


if __name__ == "__main__":
    main()
