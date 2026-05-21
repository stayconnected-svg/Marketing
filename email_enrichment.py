"""
Email Enrichment Engine v2 for Simpl ABI

Enriches prospect CSVs with email addresses using a layered approach:
  Layer 1: Expanded domain discovery (HTTP verification of many patterns)
  Layer 2: Website crawling to extract emails from contact/about pages
  Layer 3: Email pattern generation + SMTP verification (original logic)

Run modes:
  python email_enrichment.py                      -- fast mode (layer 3 only)
  python email_enrichment.py --web-research       -- full mode (all layers)
  python email_enrichment.py --web-research --limit 30  -- test run

Results cached to enrichment_cache.json for resume support.
No third-party API keys required. Fully self-hosted.
"""
import csv
import re
import socket
import smtplib
import time
import os
import sys
import json
import random
import argparse
import threading
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import dns.resolver
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "dnspython"], check=True)
    import dns.resolver

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

JUNK_EMAIL_PREFIXES = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "wordpress",
    "admin", "webmaster", "postmaster", "hostmaster", "mailer-daemon",
    "root", "abuse", "support", "billing", "sales", "marketing",
    "newsletter", "subscribe", "unsubscribe", "test", "example",
    "spam", "junk", "bounce",
}

EXCLUDED_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com", "instagram.com",
    "yelp.com", "healthgrades.com", "zocdoc.com", "vitals.com", "webmd.com",
    "yellowpages.com", "bbb.org", "mapquest.com", "manta.com",
    "npidb.org", "npino.com", "npiprofile.com", "hipaaspace.com",
    "findlaw.com", "avvo.com", "justia.com", "martindale.com",
    "superlawyers.com", "lawyers.com", "law.com",
    "google.com", "maps.google.com", "youtube.com", "wikipedia.org",
    "amazon.com", "pinterest.com", "reddit.com", "tiktok.com",
    "wixsite.com", "squarespace.com", "godaddy.com",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

CONTACT_PATHS = [
    "/contact", "/contact-us", "/contactus",
    "/about", "/about-us", "/aboutus",
    "/team", "/our-team", "/ourteam", "/staff", "/our-staff",
    "/people", "/our-people", "/doctors", "/providers",
    "/attorneys", "/our-attorneys", "/lawyers",
]

# ── Persistent Cache ──

_cache_lock = threading.Lock()
_cache_data = {}
_cache_path = os.path.join(OUTPUT_DIR, "enrichment_cache.json")


def load_cache():
    global _cache_data
    if os.path.exists(_cache_path):
        try:
            with open(_cache_path, "r", encoding="utf-8") as f:
                _cache_data = json.load(f)
            print(f"  Cache loaded: {len(_cache_data)} entries", flush=True)
        except (json.JSONDecodeError, IOError):
            _cache_data = {}


def save_cache():
    with _cache_lock:
        try:
            with open(_cache_path, "w", encoding="utf-8") as f:
                json.dump(_cache_data, f, indent=1)
        except IOError:
            pass


def cache_key(org, city, state, first="", last=""):
    parts = [s.lower().strip() for s in [org, city, state, first, last] if s]
    return "|".join(parts)


def cache_get(key):
    with _cache_lock:
        return _cache_data.get(key)


def cache_set(key, value):
    with _cache_lock:
        _cache_data[key] = value
    # Persist every 25 writes
    if len(_cache_data) % 25 == 0:
        save_cache()


# ── URL Helpers ──

def extract_domain_from_url(url):
    """Pull the root domain from a URL, stripping www."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


# ── HTTP Domain Discovery ──

_http_domain_cache = {}


def check_domain_http(domain, timeout=3):
    """Check if a domain resolves to a real website via HTTP."""
    if domain in _http_domain_cache:
        return _http_domain_cache[domain]

    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        resp = requests.get(
            f"https://{domain}",
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
        )
        ctype = resp.headers.get("Content-Type", "")
        if resp.status_code == 200 and "text/html" in ctype and len(resp.text) > 500:
            _http_domain_cache[domain] = True
            return True
    except Exception:
        pass

    # Only try HTTP if HTTPS failed
    try:
        resp = requests.get(
            f"http://{domain}",
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
        )
        ctype = resp.headers.get("Content-Type", "")
        if resp.status_code == 200 and "text/html" in ctype and len(resp.text) > 500:
            _http_domain_cache[domain] = True
            return True
    except Exception:
        pass

    _http_domain_cache[domain] = False
    return False


def generate_expanded_domains(first, last, org, city, industry):
    """
    Generate a broad set of candidate domains based on name, org, city, industry.
    More aggressive than the original generate_domains -- tries HTTP resolution.
    """
    candidates = []
    f = re.sub(r"[^a-z]", "", first.lower()) if first else ""
    l = re.sub(r"[^a-z]", "", last.lower()) if last else ""
    fi = f[0] if f else ""
    city_clean = re.sub(r"[^a-z]", "", city.lower()) if city else ""

    if l:
        # Name-based patterns
        candidates.extend([
            f"dr{l}.com",
            f"{f}{l}.com",
            f"{l}{f}.com",
            f"dr{f}{l}.com",
        ])

    if "dentist" in industry or "dds" in industry or "dmd" in industry:
        if l:
            candidates.extend([
                f"{l}dental.com",
                f"{l}dentistry.com",
                f"{l}dds.com",
                f"{l}familydentistry.com",
                f"{l}familydental.com",
                f"dr{l}dds.com",
                f"{f}{l}dds.com",
            ])
        if city_clean:
            candidates.extend([
                f"{city_clean}dental.com",
                f"{city_clean}dentistry.com",
                f"{city_clean}familydental.com",
                f"{city_clean}familydentistry.com",
            ])

    elif "physician" in industry or "md" in industry or "do" in industry:
        if l:
            candidates.extend([
                f"{l}md.com",
                f"{l}medical.com",
                f"{l}medicine.com",
                f"dr{l}md.com",
                f"{l}health.com",
                f"{l}clinic.com",
            ])

    elif "lawyer" in industry or "attorney" in industry or "esq" in industry:
        if l:
            candidates.extend([
                f"{l}law.com",
                f"{l}legal.com",
                f"{l}lawfirm.com",
                f"{l}attorney.com",
                f"{l}lawoffice.com",
                f"{l}andassociates.com",
            ])

    # Organization-name based patterns
    org_slugs = clean_org_name(org)
    for slug in org_slugs:
        candidates.append(f"{slug}.com")
        if city_clean:
            candidates.append(f"{slug}{city_clean}.com")

    return list(dict.fromkeys(candidates))[:20]


def discover_domain_http(first, last, org, city, industry):
    """
    Try to find a practice website by checking expanded domain candidates.
    Pass 1: MX records (fast DNS, no HTTP).
    Pass 2: HTTP resolution (slower, catches sites without MX).
    Returns (domain, website_url) or (None, None).
    """
    candidates = generate_expanded_domains(first, last, org, city, industry)

    # Pass 1: check MX records (fast)
    for domain in candidates:
        if domain_accepts_mail(domain):
            return domain, f"https://{domain}"

    # Pass 2: try HTTP for domains that had no MX
    for domain in candidates:
        if _http_domain_cache.get(domain) is True:
            return domain, f"https://{domain}"
        elif _http_domain_cache.get(domain) is False:
            continue
        if check_domain_http(domain):
            return domain, f"https://{domain}"

    return None, None


# ── Website Crawler ──

_last_crawl_time = {}
_crawl_lock = threading.Lock()


def _rate_limit_crawl(domain):
    """Enforce minimum 1s between requests to the same domain."""
    with _crawl_lock:
        now = time.time()
        last = _last_crawl_time.get(domain, 0)
        if now - last < 1.0:
            time.sleep(1.0 - (now - last))
        _last_crawl_time[domain] = time.time()


def fetch_page(url, timeout=6):
    """Fetch a page and return its HTML, or None on failure."""
    domain = extract_domain_from_url(url)
    _rate_limit_crawl(domain)

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout,
                            allow_redirects=True)
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None
        if resp.status_code != 200:
            return None
        return resp.text
    except requests.RequestException:
        return None


def extract_emails_from_html(html):
    """Extract all email addresses from HTML content."""
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style tags to avoid false positives
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Also check href="mailto:" links directly
    mailto_emails = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            email = href[7:].split("?")[0].strip()
            if email:
                mailto_emails.append(email.lower())

    regex_emails = [e.lower() for e in EMAIL_RE.findall(text)]

    all_emails = list(dict.fromkeys(mailto_emails + regex_emails))

    # Filter out junk
    filtered = []
    for email in all_emails:
        prefix = email.split("@")[0]
        domain = email.split("@")[1] if "@" in email else ""
        if prefix in JUNK_EMAIL_PREFIXES:
            continue
        if domain in EXCLUDED_DOMAINS:
            continue
        # Filter image file false-positives (e.g., "logo@2x.png")
        if any(domain.endswith(ext) for ext in [".png", ".jpg", ".gif", ".svg", ".css"]):
            continue
        filtered.append(email)

    return filtered


def extract_meta_description(html):
    """Pull meta description for personalization data."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()[:200]
    return ""


def rank_emails(emails, first_name="", last_name=""):
    """
    Rank extracted emails by quality.
    Name-match > info/office/contact > generic
    Returns the best email.
    """
    if not emails:
        return None

    first = first_name.lower().strip()
    last = last_name.lower().strip()

    name_matches = []
    generic_good = []
    other = []

    for email in emails:
        prefix = email.split("@")[0]
        if first and last:
            if first in prefix and last in prefix:
                name_matches.insert(0, email)
            elif first in prefix or last in prefix:
                name_matches.append(email)
            elif prefix in ("info", "office", "contact", "hello", "front",
                            "frontdesk", "reception", "inquiries"):
                generic_good.append(email)
            else:
                other.append(email)
        elif prefix in ("info", "office", "contact", "hello", "front",
                        "frontdesk", "reception", "inquiries"):
            generic_good.append(email)
        else:
            other.append(email)

    ranked = name_matches + generic_good + other
    return ranked[0] if ranked else None


def crawl_website_for_emails(domain, first_name="", last_name=""):
    """
    Crawl a domain's key pages looking for email addresses.
    Returns (best_email, all_emails, meta_description).
    Stops early once emails are found to save time.
    """
    base = f"https://{domain}"
    all_emails = []
    meta_desc = ""

    html = fetch_page(base)
    if html:
        all_emails.extend(extract_emails_from_html(html))
        meta_desc = extract_meta_description(html)

    if not all_emails:
        # Only crawl sub-pages if homepage didn't have emails
        priority_paths = [
            "/contact", "/contact-us", "/about", "/about-us",
            "/team", "/our-team", "/staff",
        ]
        for path in priority_paths:
            url = base + path
            html = fetch_page(url)
            if html:
                page_emails = extract_emails_from_html(html)
                all_emails.extend(page_emails)
                if not meta_desc:
                    meta_desc = extract_meta_description(html)
                if all_emails:
                    break  # found emails, stop crawling

    all_emails = list(dict.fromkeys(all_emails))

    best = rank_emails(all_emails, first_name, last_name)
    return best, all_emails, meta_desc


# ── Domain Generation ──

def clean_org_name(org_name):
    """Convert organization name into candidate domain slugs."""
    if not org_name:
        return []

    name = org_name.lower().strip()
    # Remove common suffixes
    for suffix in [", llc", " llc", ", ltd", " ltd", ", inc", " inc", ", pc",
                   " pc", ", pllc", " pllc", ", pa", " pa", ", md", " md",
                   ", dds", " dds", ", dmd", " dmd", ", do", " do",
                   ", esq", " esq", ", llp", " llp", ", co", " co",
                   " & associates", " and associates", " associates",
                   " group", " partners", " practice", " clinic",
                   " professional", " professionals", " services"]:
        name = name.replace(suffix, "")

    name = name.strip().strip(",").strip()
    name = re.sub(r"[''`]", "", name)
    slug_nodash = re.sub(r"[^a-z0-9]", "", name)
    slug_dash = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    words = re.sub(r"[^a-z0-9\s]", "", name).split()

    candidates = set()
    if slug_nodash:
        candidates.add(slug_nodash)
    if slug_dash and slug_dash != slug_nodash:
        candidates.add(slug_dash)

    # dr + lastname patterns (common for medical/dental)
    if len(words) >= 2:
        candidates.add(words[0] + words[-1])
        candidates.add(words[-1] + words[0])
        if words[0] == "dr" and len(words) >= 2:
            candidates.add("dr" + words[-1])

    # first initials + last word
    if len(words) >= 2:
        initials = "".join(w[0] for w in words[:-1])
        candidates.add(initials + words[-1])

    return [c for c in candidates if len(c) >= 3]


def generate_domains(org_name, city=""):
    """Generate candidate domain names from an organization name."""
    slugs = clean_org_name(org_name)
    domains = []

    for slug in slugs:
        domains.append(f"{slug}.com")

    # Also try city-based patterns for medical/dental
    if city:
        city_clean = re.sub(r"[^a-z]", "", city.lower())
        if city_clean:
            first_slug = slugs[0] if slugs else ""
            if first_slug:
                domains.append(f"{first_slug}{city_clean}.com")

    return list(dict.fromkeys(domains))[:8]  # dedupe, max 8 candidates


# ── Email Pattern Generation ──

def generate_email_candidates(first_name, last_name, domain):
    """Generate candidate email addresses from name + domain."""
    if not first_name or not last_name or not domain:
        return []

    f = first_name.lower().strip()
    l = last_name.lower().strip()
    fi = f[0] if f else ""

    candidates = [
        f"{f}@{domain}",
        f"{f}.{l}@{domain}",
        f"{f}{l}@{domain}",
        f"{fi}{l}@{domain}",
        f"{fi}.{l}@{domain}",
        f"{l}@{domain}",
        f"{l}.{f}@{domain}",
        f"{l}{fi}@{domain}",
        f"info@{domain}",
        f"office@{domain}",
        f"contact@{domain}",
    ]
    return candidates


# ── DNS/MX Verification ──

_mx_cache = {}

def get_mx_records(domain):
    """Look up MX records for a domain. Returns list of mail server hostnames."""
    if domain in _mx_cache:
        return _mx_cache[domain]

    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_hosts = sorted(answers, key=lambda r: r.preference)
        result = [str(r.exchange).rstrip(".") for r in mx_hosts]
        _mx_cache[domain] = result
        return result
    except Exception:
        _mx_cache[domain] = []
        return []


def domain_accepts_mail(domain):
    """Check if a domain has MX records (accepts email)."""
    return len(get_mx_records(domain)) > 0


# ── SMTP Verification ──

def verify_email_smtp(email, timeout=10):
    """
    Verify an email address exists via SMTP RCPT TO.
    Returns: 'valid', 'invalid', 'catchall', or 'error'

    Note: Many servers are configured as catch-all (accept any address).
    We detect this by testing a random nonexistent address.
    """
    domain = email.split("@")[1]
    mx_hosts = get_mx_records(domain)
    if not mx_hosts:
        return "no_mx"

    mx_host = mx_hosts[0]

    try:
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo("simplabi.com")
        smtp.mail("verify@simplabi.com")
        code, _ = smtp.rcpt(email)
        smtp.quit()

        if code == 250:
            return "valid"
        elif code == 550 or code == 551 or code == 553:
            return "invalid"
        else:
            return "unknown"
    except smtplib.SMTPServerDisconnected:
        return "error"
    except smtplib.SMTPConnectError:
        return "error"
    except socket.timeout:
        return "timeout"
    except ConnectionRefusedError:
        return "refused"
    except Exception:
        return "error"


def check_catchall(domain, timeout=10):
    """Check if a domain is catch-all by testing a random address."""
    random_email = f"zxqj7k9m2w_{int(time.time())}@{domain}"
    result = verify_email_smtp(random_email, timeout)
    return result == "valid"  # If random address is "valid", it's catch-all


# ── Main Enrichment Pipeline ──

def find_domain_for_prospect(org_name, city=""):
    """Try to find a valid email domain for a prospect's organization."""
    candidates = generate_domains(org_name, city)
    for domain in candidates:
        if domain_accepts_mail(domain):
            return domain
    return None


def split_full_name(full_name):
    """Split a full name into first and last name."""
    if not full_name:
        return "", ""
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], parts[0]
    # Handle suffixes like Jr., III, Esq., etc.
    suffixes = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "esq", "esq."}
    while len(parts) > 2 and parts[-1].lower().rstrip(".") in suffixes:
        parts.pop()
    return parts[0], parts[-1]


def enrich_prospect(row, web_research=False):
    """
    Enrich a single prospect row with email candidates.
    If web_research=True, uses DuckDuckGo search + website crawling first.
    """
    first = row.get("First Name", "").strip()
    last = row.get("Last Name", "").strip()

    if not first or not last:
        full = row.get("Full Name", "").strip()
        if full:
            f, l = split_full_name(full)
            first = first or f
            last = last or l

    org = row.get("Organization", row.get("Firm Name", "")).strip()
    city = row.get("City", "").strip()
    state = row.get("State", "").strip()
    industry = row.get("Industry", "").lower()
    website = row.get("Website", "").strip()

    result = {
        "domain_found": "",
        "email_candidates": "",
        "best_email": "",
        "email_status": "no_domain",
        "email_source": "",
        "is_catchall": "",
        "website_url": "",
        "linkedin_url": "",
        "meta_description": "",
    }

    if not org and not last:
        return result

    # ── Check cache first ──
    ck = cache_key(org, city, state, first, last)
    cached = cache_get(ck)
    if cached:
        return cached

    domain = None
    found_website_url = ""
    linkedin_url = ""
    meta_desc = ""

    # ── Layer 0: Use existing Website column ──
    if website:
        clean_url = website.lower().replace("https://", "").replace("http://", "")
        clean_url = clean_url.replace("www.", "").split("/")[0].strip()
        if "." in clean_url:
            domain = clean_url
            found_website_url = website

            if web_research:
                best_scraped, all_scraped, meta_desc = crawl_website_for_emails(
                    domain, first, last)
                if best_scraped:
                    result["domain_found"] = domain
                    result["best_email"] = best_scraped
                    result["email_status"] = "website_scraped"
                    result["email_source"] = "website_scraped"
                    result["email_candidates"] = "; ".join(all_scraped[:5])
                    result["website_url"] = found_website_url
                    result["meta_description"] = meta_desc
                    cache_set(ck, result)
                    return result

    # ── Layer 1: Expanded domain discovery via HTTP ──
    if web_research and not domain:
        disc_domain, disc_url = discover_domain_http(
            first, last, org, city, industry)
        if disc_domain:
            domain = disc_domain
            found_website_url = disc_url or f"https://{disc_domain}"

    # ── Layer 2: Crawl the found website ──
    if web_research and domain and not result["best_email"]:
        best_scraped, all_scraped, meta_desc = crawl_website_for_emails(
            domain, first, last)
        if best_scraped:
            result["domain_found"] = domain
            result["best_email"] = best_scraped
            result["email_status"] = "website_scraped"
            result["email_source"] = "website_scraped"
            result["email_candidates"] = "; ".join(all_scraped[:5])
            result["website_url"] = found_website_url
            result["linkedin_url"] = linkedin_url
            result["meta_description"] = meta_desc
            cache_set(ck, result)
            return result

    # ── Layer 3: Domain guessing (original logic) ──
    if not domain:
        domain = find_domain_for_prospect(org, city)

    if not domain and last:
        last_clean = re.sub(r"[^a-z]", "", last.lower())
        solo_domains = []

        if "dentist" in industry or "dds" in row.get("Credential", "").lower() or "dmd" in row.get("Credential", "").lower():
            solo_domains = [
                f"dr{last_clean}.com",
                f"{last_clean}dental.com",
                f"{last_clean}dentistry.com",
                f"{last_clean}dds.com",
                f"{last_clean}familydentistry.com",
            ]
        elif "physician" in industry or "md" in row.get("Credential", "").lower() or "do" in row.get("Credential", "").lower():
            solo_domains = [
                f"dr{last_clean}.com",
                f"{last_clean}md.com",
                f"{last_clean}medical.com",
                f"{last_clean}medicine.com",
            ]
        elif "lawyer" in industry or "attorney" in industry or "esq" in row.get("Title", "").lower():
            solo_domains = [
                f"{last_clean}law.com",
                f"{last_clean}legal.com",
                f"{last_clean}lawfirm.com",
                f"{last_clean}attorney.com",
            ]
        else:
            solo_domains = [
                f"dr{last_clean}.com",
                f"{last_clean}.com",
            ]

        for d in solo_domains:
            if domain_accepts_mail(d):
                domain = d
                break

    if not domain:
        result["linkedin_url"] = linkedin_url
        result["website_url"] = found_website_url
        cache_set(ck, result)
        return result

    if not result["domain_found"]:
        result["domain_found"] = domain
    result["website_url"] = found_website_url or result.get("website_url", "")
    result["linkedin_url"] = linkedin_url

    candidates = generate_email_candidates(first, last, domain)
    result["email_candidates"] = "; ".join(candidates[:5])

    # ── Layer 3b: SMTP verification ──
    for email in candidates[:4]:
        status = verify_email_smtp(email)
        if status == "valid":
            result["best_email"] = email
            result["email_status"] = "verified"
            result["email_source"] = "smtp_verified"
            break
        elif status == "invalid":
            continue
        elif status in ("error", "timeout", "refused"):
            result["best_email"] = candidates[0]
            result["email_status"] = "pattern_match"
            result["email_source"] = "pattern_match"
            break
    else:
        if candidates:
            result["best_email"] = candidates[0]
            result["email_status"] = "pattern_match"
            result["email_source"] = "pattern_match"

    result["meta_description"] = meta_desc
    cache_set(ck, result)
    return result


def process_csv(input_path, output_path, max_prospects=None, threads=5,
                default_industry="", web_research=False):
    """Process a prospect CSV and enrich with email data."""
    print(f"\n{'='*60}", flush=True)
    print(f"Processing: {os.path.basename(input_path)}", flush=True)
    mode_label = "WEB RESEARCH + DNS/SMTP" if web_research else "DNS/SMTP only"
    print(f"  Mode: {mode_label}", flush=True)
    print(f"{'='*60}", flush=True)

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        original_fields = reader.fieldnames

    if max_prospects:
        rows = rows[:max_prospects]

    if default_industry:
        for row in rows:
            if not row.get("Industry", ""):
                row["Industry"] = default_industry

    new_fields = ["Domain Found", "Best Email", "Email Status", "Email Source",
                  "Email Candidates", "Is Catchall", "Website URL",
                  "LinkedIn URL", "Meta Description"]
    all_fields = list(original_fields) + new_fields

    enriched_rows = []
    stats = {
        "total": len(rows), "domain_found": 0, "email_found": 0,
        "verified": 0, "pattern_match": 0, "website_scraped": 0,
        "cached": 0, "no_domain": 0,
    }

    effective_threads = threads

    print(f"  Enriching {len(rows)} prospects...", flush=True)
    if web_research:
        print(f"  Using {effective_threads} threads (HTTP + crawl + DNS/SMTP)", flush=True)
    else:
        print(f"  Using {threads} threads for parallel processing", flush=True)
    sys.stdout.flush()

    def process_one(i_row):
        i, row = i_row
        result = enrich_prospect(row, web_research=web_research)
        return i, row, result

    with ThreadPoolExecutor(max_workers=effective_threads) as executor:
        futures = {executor.submit(process_one, (i, row)): i
                   for i, row in enumerate(rows)}

        completed = 0
        for future in as_completed(futures):
            i, row, result = future.result()
            completed += 1

            row["Domain Found"] = result.get("domain_found", "")
            row["Best Email"] = result.get("best_email", "")
            row["Email Status"] = result.get("email_status", "")
            row["Email Source"] = result.get("email_source", "")
            row["Email Candidates"] = result.get("email_candidates", "")
            row["Is Catchall"] = result.get("is_catchall", "")
            row["Website URL"] = result.get("website_url", "")
            row["LinkedIn URL"] = result.get("linkedin_url", "")
            row["Meta Description"] = result.get("meta_description", "")
            enriched_rows.append((i, row))

            if result.get("domain_found"):
                stats["domain_found"] += 1
            if result.get("best_email"):
                stats["email_found"] += 1

            src = result.get("email_source", "")
            if src == "website_scraped":
                stats["website_scraped"] += 1
            elif src == "smtp_verified":
                stats["verified"] += 1
            elif src == "pattern_match":
                stats["pattern_match"] += 1
            elif not result.get("best_email"):
                stats["no_domain"] += 1

            if completed % 10 == 0 or completed == len(rows):
                pct = completed / len(rows) * 100
                scraped = stats["website_scraped"]
                print(f"  Progress: {completed}/{len(rows)} ({pct:.0f}%) | "
                      f"Emails: {stats['email_found']} "
                      f"(scraped:{scraped} verified:{stats['verified']} "
                      f"pattern:{stats['pattern_match']})", flush=True)

    enriched_rows.sort(key=lambda x: x[0])
    sorted_rows = [row for _, row in enriched_rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted_rows)

    total = stats["total"]
    print(f"\n  Results:", flush=True)
    print(f"    Total prospects:    {total}", flush=True)
    print(f"    Domains found:     {stats['domain_found']} ({stats['domain_found']/total*100:.1f}%)", flush=True)
    print(f"    Emails found:      {stats['email_found']} ({stats['email_found']/total*100:.1f}%)", flush=True)
    print(f"    - Website scraped: {stats['website_scraped']}", flush=True)
    print(f"    - SMTP verified:   {stats['verified']}", flush=True)
    print(f"    - Pattern match:   {stats['pattern_match']}", flush=True)
    print(f"    No email found:    {stats['no_domain']}", flush=True)
    print(f"  Output: {output_path}", flush=True)

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simpl ABI Email Enrichment Engine v2")
    parser.add_argument("--web-research", action="store_true",
                        help="Enable web search + website crawling (slower, higher accuracy)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max prospects per file (for testing)")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print("SIMPL ABI - Email Enrichment Engine v2", flush=True)
    if args.web_research:
        print("MODE: Web Research (HTTP Discovery + Website Crawling + DNS/SMTP)", flush=True)
    else:
        print("MODE: Fast (DNS/SMTP only)", flush=True)
    print("Self-hosted. No API keys. No third-party dependencies.", flush=True)
    print("=" * 60, flush=True)

    if args.limit:
        print(f"  Limiting to {args.limit} prospects per file", flush=True)

    load_cache()

    files = [
        ("prospects_dentists.csv", "prospects_dentists_enriched.csv", "Dentist"),
        ("prospects_lawyers.csv", "prospects_lawyers_enriched.csv", "Lawyer"),
        ("prospects_doctors.csv", "prospects_doctors_enriched.csv", "Physician"),
    ]

    all_stats = {}
    for input_name, output_name, default_industry in files:
        input_path = os.path.join(OUTPUT_DIR, input_name)
        output_path = os.path.join(OUTPUT_DIR, output_name)

        if not os.path.exists(input_path):
            print(f"\n  Skipping {input_name} (file not found)", flush=True)
            continue

        stats = process_csv(input_path, output_path,
                           max_prospects=args.limit, threads=5,
                           default_industry=default_industry,
                           web_research=args.web_research)
        all_stats[input_name] = stats

    # Final cache save
    save_cache()

    print(f"\n{'='*60}", flush=True)
    print("ENRICHMENT SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    total_prospects = 0
    total_emails = 0
    total_scraped = 0
    total_verified = 0
    total_pattern = 0
    for name, stats in all_stats.items():
        total_prospects += stats["total"]
        total_emails += stats["email_found"]
        total_scraped += stats["website_scraped"]
        total_verified += stats["verified"]
        total_pattern += stats["pattern_match"]
        print(f"  {name}: {stats['email_found']}/{stats['total']} emails "
              f"({stats['email_found']/stats['total']*100:.1f}%) "
              f"[scraped:{stats['website_scraped']} "
              f"verified:{stats['verified']} "
              f"pattern:{stats['pattern_match']}]", flush=True)
    if total_prospects:
        print(f"\n  TOTAL: {total_emails}/{total_prospects} emails "
              f"({total_emails/total_prospects*100:.1f}%)", flush=True)
        print(f"    Website scraped: {total_scraped}", flush=True)
        print(f"    SMTP verified:   {total_verified}", flush=True)
        print(f"    Pattern match:   {total_pattern}", flush=True)
    print(f"\n  Cache entries: {len(_cache_data)}", flush=True)
    print(f"{'='*60}", flush=True)
