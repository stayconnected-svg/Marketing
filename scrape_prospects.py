"""
Prospect list builder for Bryan McInerney - Tier 1 Industries
Uses free public data sources: NPI Registry API, and web searches.
Outputs clean CSV files per industry for CRM import.
"""
import csv
import json
import os
import time
import urllib.request
import urllib.parse
import ssl

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
ssl._create_default_https_context = ssl._create_unverified_context

NE_OHIO_CITIES = [
    "Hudson", "Akron", "Cleveland", "Canton", "Medina",
    "Cuyahoga Falls", "Stow", "Kent", "Wadsworth", "Brunswick",
    "Strongsville", "Westlake", "Lakewood", "Parma", "Mentor",
    "Elyria", "Lorain", "Barberton", "Massillon", "North Canton",
    "Green", "Fairlawn", "Bath", "Copley", "Tallmadge",
    "Twinsburg", "Solon", "Aurora", "Macedonia", "Streetsboro",
    "Ravenna", "Alliance", "Wooster", "Beachwood", "Shaker Heights",
    "Rocky River", "Avon", "Avon Lake", "North Olmsted", "Berea",
    "Broadview Heights", "Brecksville", "Independence", "Seven Hills",
    "North Royalton", "Middleburg Heights", "Olmsted Falls",
    "Chagrin Falls", "Chardon", "Painesville", "Willoughby"
]

NE_OHIO_ZIPS_SUMMIT = [
    "44203", "44221", "44223", "44224", "44236", "44240",
    "44256", "44260", "44264", "44278", "44281", "44301",
    "44302", "44303", "44304", "44305", "44306", "44307",
    "44308", "44310", "44311", "44312", "44313", "44314",
    "44319", "44320", "44321", "44333",
]

NE_OHIO_ZIPS_CUYAHOGA = [
    "44101", "44102", "44103", "44104", "44105", "44106",
    "44107", "44108", "44109", "44110", "44111", "44112",
    "44113", "44114", "44115", "44116", "44117", "44118",
    "44119", "44120", "44121", "44122", "44123", "44124",
    "44125", "44126", "44127", "44128", "44129", "44130",
    "44131", "44132", "44133", "44134", "44135", "44136",
    "44137", "44138", "44139", "44140", "44141", "44142",
    "44143", "44144", "44145", "44146", "44147", "44149",
]


def query_npi(taxonomy_desc, city=None, state="OH", postal_code=None, limit=200, skip=0):
    """Query the NPI Registry API."""
    base = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "state": state,
        "taxonomy_description": taxonomy_desc,
        "limit": str(limit),
        "skip": str(skip),
        "enumeration_type": "NPI-1",
    }
    if city:
        params["city"] = city
    if postal_code:
        params["postal_code"] = postal_code

    url = base + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SimplABI-Prospecting/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data.get("results", [])
    except Exception as e:
        print(f"  Error querying NPI ({taxonomy_desc}, {city or postal_code}): {e}")
        return []


def parse_npi_result(r):
    """Extract useful fields from an NPI result."""
    basic = r.get("basic", {})
    addresses = r.get("addresses", [])
    taxonomies = r.get("taxonomies", [])

    practice_addr = None
    for a in addresses:
        if a.get("address_purpose") == "LOCATION":
            practice_addr = a
            break
    if not practice_addr and addresses:
        practice_addr = addresses[0]

    first = basic.get("first_name", "")
    last = basic.get("last_name", "")
    credential = basic.get("credential", "")
    org = basic.get("organization_name", "")
    npi = r.get("number", "")

    addr_line = practice_addr.get("address_1", "") if practice_addr else ""
    city = practice_addr.get("city", "") if practice_addr else ""
    state = practice_addr.get("state", "") if practice_addr else ""
    zipcode = practice_addr.get("postal_code", "")[:5] if practice_addr else ""
    phone = practice_addr.get("telephone_number", "") if practice_addr else ""
    fax = practice_addr.get("fax_number", "") if practice_addr else ""

    specialty = ""
    if taxonomies:
        specialty = taxonomies[0].get("desc", "")

    return {
        "NPI": npi,
        "First Name": first,
        "Last Name": last,
        "Credential": credential,
        "Full Name": f"{first} {last}".strip(),
        "Organization": org,
        "Specialty": specialty,
        "Address": addr_line,
        "City": city,
        "State": state,
        "ZIP": zipcode,
        "Phone": phone,
        "Fax": fax,
    }


def dedupe(records):
    """Deduplicate by NPI number."""
    seen = set()
    unique = []
    for r in records:
        npi = r.get("NPI", "")
        if npi and npi not in seen:
            seen.add(npi)
            unique.append(r)
    return unique


def write_csv(records, filename, fieldnames=None):
    """Write records to CSV."""
    if not records:
        print(f"  No records to write for {filename}")
        return
    if not fieldnames:
        fieldnames = list(records[0].keys())
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"  Wrote {len(records)} records to {path}")


def build_dentist_list():
    """Build dentist prospect list from NPI Registry."""
    print("\n=== BUILDING DENTIST PROSPECT LIST ===")
    all_records = []

    taxonomies = [
        "Dentist",
        "General Practice Dentistry",
        "Dental Public Health",
        "Endodontics",
        "Orthodontics",
        "Pediatric Dentistry",
        "Periodontics",
        "Prosthodontics",
        "Oral & Maxillofacial Surgery",
    ]

    key_cities = [
        "Hudson", "Akron", "Cleveland", "Canton", "Medina",
        "Cuyahoga Falls", "Stow", "Kent", "Wadsworth", "Brunswick",
        "Strongsville", "Westlake", "Lakewood", "Parma", "Mentor",
        "Barberton", "Massillon", "North Canton", "Fairlawn",
        "Twinsburg", "Solon", "Aurora", "Beachwood", "Shaker Heights",
        "Rocky River", "Avon", "North Olmsted", "Brecksville",
        "Broadview Heights", "Middleburg Heights", "Chagrin Falls",
        "Willoughby", "Painesville", "Elyria", "Lorain",
    ]

    for tax in taxonomies[:3]:
        for city in key_cities:
            results = query_npi(tax, city=city)
            if results:
                for r in results:
                    parsed = parse_npi_result(r)
                    parsed["Industry"] = "Dentist"
                    parsed["Source"] = "NPI Registry"
                    all_records.append(parsed)
                print(f"  {tax} in {city}: {len(results)} results")
            time.sleep(0.3)

    all_records = dedupe(all_records)
    all_records.sort(key=lambda x: (x["City"], x["Last Name"]))
    print(f"\n  Total unique dentists: {len(all_records)}")

    fieldnames = [
        "Full Name", "First Name", "Last Name", "Credential",
        "Organization", "Specialty", "Address", "City", "State",
        "ZIP", "Phone", "Fax", "NPI", "Industry", "Source"
    ]
    write_csv(all_records, "prospects_dentists.csv", fieldnames)
    return all_records


def build_doctor_list():
    """Build doctor prospect list from NPI Registry -- focus on practice owners."""
    print("\n=== BUILDING DOCTOR PROSPECT LIST ===")
    all_records = []

    taxonomies = [
        "Internal Medicine",
        "Family Medicine",
        "General Practice",
        "Cardiovascular Disease",
        "Dermatology",
        "Gastroenterology",
        "Orthopedic Surgery",
        "Ophthalmology",
        "Otolaryngology",
        "Urology",
        "Plastic Surgery",
        "Obstetrics & Gynecology",
        "Allergy & Immunology",
        "Rheumatology",
        "Pulmonary Disease",
    ]

    key_cities = [
        "Hudson", "Akron", "Cleveland", "Canton", "Medina",
        "Cuyahoga Falls", "Stow", "Kent", "Strongsville",
        "Westlake", "Lakewood", "Parma", "Mentor", "Beachwood",
        "Solon", "Rocky River", "Avon", "North Olmsted",
        "Broadview Heights", "Brecksville", "Middleburg Heights",
        "Chagrin Falls", "Willoughby", "Elyria",
    ]

    for tax in taxonomies:
        for city in key_cities[:12]:
            results = query_npi(tax, city=city)
            if results:
                for r in results:
                    parsed = parse_npi_result(r)
                    parsed["Industry"] = "Physician"
                    parsed["Source"] = "NPI Registry"
                    all_records.append(parsed)
                print(f"  {tax} in {city}: {len(results)} results")
            time.sleep(0.3)

    all_records = dedupe(all_records)
    all_records.sort(key=lambda x: (x["City"], x["Last Name"]))
    print(f"\n  Total unique physicians: {len(all_records)}")

    fieldnames = [
        "Full Name", "First Name", "Last Name", "Credential",
        "Organization", "Specialty", "Address", "City", "State",
        "ZIP", "Phone", "Fax", "NPI", "Industry", "Source"
    ]
    write_csv(all_records, "prospects_doctors.csv", fieldnames)
    return all_records


def build_lawyer_list():
    """
    Build lawyer prospect list.
    NPI doesn't cover lawyers, so we create a structured template
    with data from public directories that can be filled in.
    We'll also try the OSBA and OH Supreme Court if accessible.
    """
    print("\n=== BUILDING LAWYER PROSPECT LIST ===")
    print("  Lawyers are not in NPI. Building from web sources...")

    all_records = []
    return all_records


if __name__ == "__main__":
    print("=" * 60)
    print("SIMPL ABI - Prospect List Builder")
    print("Target: Bryan McInerney / Intelligent Annuity Solutions")
    print("Region: Northeast Ohio")
    print("=" * 60)

    dentists = build_dentist_list()
    doctors = build_doctor_list()
    lawyers = build_lawyer_list()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  Dentists: {len(dentists)} prospects")
    print(f"  Doctors:  {len(doctors)} prospects")
    print(f"  Lawyers:  (requires manual web research)")
    print("=" * 60)
