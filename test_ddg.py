"""Quick test of DDG search to diagnose why dentist/doctor sites aren't found."""
import sys
sys.path.insert(0, ".")
from email_enrichment import search_ddg, extract_domain_from_url, is_practice_domain
import time

tests = [
    '"Zoya Shaikh" dentist Addison IL',
    '"George Appel" dentist Akron OH',
    "Smith Family Dental Akron OH",
    '"Daniel Abood" physician Akron OH',
]

for q in tests:
    print(f"\nQuery: {q}")
    results = search_ddg(q)
    if not results:
        print("  No results returned")
    for url, title in results[:5]:
        domain = extract_domain_from_url(url)
        is_prac = is_practice_domain(domain)
        print(f"  {'[OK]' if is_prac else '[SKIP]'} {domain} - {title[:60]}")
    time.sleep(2)
