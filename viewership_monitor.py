"""
Viewership Monitor for checkannuity.com (GA4)

Pulls daily traffic data from Google Analytics 4 and detects rising viewership.
Outputs a weekly trend report and flags spikes for the lead pipeline.

Setup:
  1. Create a GA4 property at https://analytics.google.com
  2. Enable the GA4 Data API in Google Cloud Console
  3. Create a service account and download the JSON key file
  4. Add the service account email as a Viewer on your GA4 property
  5. Set env vars: GA4_PROPERTY_ID, GA4_CREDENTIALS_PATH

Requirements:
  pip install google-analytics-data python-dotenv
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "")
GA4_CREDENTIALS_PATH = os.getenv("GA4_CREDENTIALS_PATH", "ga4_credentials.json")
TREND_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewership_trend.json")


def get_ga4_client():
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GA4_CREDENTIALS_PATH
        return BetaAnalyticsDataClient()
    except ImportError:
        print("[GA4] Missing dependency: pip install google-analytics-data")
        return None
    except Exception as e:
        print(f"[GA4] Auth error: {e}")
        return None


def fetch_daily_traffic(client, days_back=30):
    """Pull daily sessions, users, and pageviews for the last N days."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(
            start_date=f"{days_back}daysAgo",
            end_date="today"
        )],
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="newUsers"),
            Metric(name="averageSessionDuration"),
        ],
        order_bys=[{"dimension": {"dimension_name": "date"}}],
    )

    response = client.run_report(request)

    daily = []
    for row in response.rows:
        daily.append({
            "date": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "pageviews": int(row.metric_values[2].value),
            "new_users": int(row.metric_values[3].value),
            "avg_duration_sec": float(row.metric_values[4].value),
        })

    return daily


def fetch_traffic_sources(client, days_back=30):
    """Break down traffic by source/medium for the period."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(
            start_date=f"{days_back}daysAgo",
            end_date="today"
        )],
        dimensions=[
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="sessionSource"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
        ],
        order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        limit=20,
    )

    response = client.run_report(request)

    sources = []
    for row in response.rows:
        sources.append({
            "channel": row.dimension_values[0].value,
            "source": row.dimension_values[1].value,
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
        })

    return sources


def detect_trends(daily_data):
    """
    Compare recent week vs prior week to detect rising viewership.
    Returns trend analysis with percentage changes and spike detection.
    """
    if len(daily_data) < 14:
        return {
            "status": "insufficient_data",
            "message": f"Need 14+ days of data, have {len(daily_data)}",
            "recommendation": "Keep tracking — trends will appear after 2 weeks."
        }

    recent_7 = daily_data[-7:]
    prior_7 = daily_data[-14:-7]

    def week_totals(week):
        return {
            "sessions": sum(d["sessions"] for d in week),
            "users": sum(d["users"] for d in week),
            "pageviews": sum(d["pageviews"] for d in week),
            "new_users": sum(d["new_users"] for d in week),
            "avg_duration": sum(d["avg_duration_sec"] for d in week) / max(len(week), 1),
        }

    recent = week_totals(recent_7)
    prior = week_totals(prior_7)

    def pct_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    changes = {
        "sessions": pct_change(recent["sessions"], prior["sessions"]),
        "users": pct_change(recent["users"], prior["users"]),
        "pageviews": pct_change(recent["pageviews"], prior["pageviews"]),
        "new_users": pct_change(recent["new_users"], prior["new_users"]),
    }

    # Detect daily spikes (any day > 2x the 30-day average)
    if len(daily_data) >= 7:
        avg_daily_sessions = sum(d["sessions"] for d in daily_data) / len(daily_data)
        spikes = [
            d for d in daily_data
            if d["sessions"] > avg_daily_sessions * 2 and avg_daily_sessions > 0
        ]
    else:
        avg_daily_sessions = 0
        spikes = []

    rising = changes["sessions"] > 10 or changes["users"] > 10
    surging = changes["sessions"] > 50 or changes["users"] > 50

    if surging:
        status = "SURGING"
        message = f"Traffic is surging — sessions up {changes['sessions']}% week-over-week"
    elif rising:
        status = "RISING"
        message = f"Viewership is rising — sessions up {changes['sessions']}% week-over-week"
    elif changes["sessions"] > 0:
        status = "STABLE_GROWTH"
        message = f"Slight uptick — sessions up {changes['sessions']}% week-over-week"
    elif changes["sessions"] == 0:
        status = "FLAT"
        message = "Traffic is flat week-over-week"
    else:
        status = "DECLINING"
        message = f"Traffic down {abs(changes['sessions'])}% week-over-week"

    return {
        "status": status,
        "message": message,
        "period": {
            "recent_week": {
                "start": recent_7[0]["date"],
                "end": recent_7[-1]["date"],
                **recent,
            },
            "prior_week": {
                "start": prior_7[0]["date"],
                "end": prior_7[-1]["date"],
                **prior,
            },
        },
        "changes_pct": changes,
        "avg_daily_sessions": round(avg_daily_sessions, 1),
        "spikes": spikes,
        "spike_count": len(spikes),
    }


def fetch_top_pages(client, days_back=30):
    """Which pages are getting the most views."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(
            start_date=f"{days_back}daysAgo",
            end_date="today"
        )],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
            Metric(name="averageSessionDuration"),
        ],
        order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        limit=10,
    )

    response = client.run_report(request)

    pages = []
    for row in response.rows:
        pages.append({
            "page": row.dimension_values[0].value,
            "pageviews": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "avg_duration_sec": float(row.metric_values[2].value),
        })

    return pages


def run_viewership_report():
    """Full viewership report — call daily or weekly."""
    if not GA4_PROPERTY_ID:
        print("[Viewership Monitor] GA4_PROPERTY_ID not set in .env")
        print("  1. Create GA4 property at https://analytics.google.com")
        print("  2. Copy the numeric property ID (e.g. 123456789)")
        print("  3. Add GA4_PROPERTY_ID=123456789 to your .env file")
        return None

    client = get_ga4_client()
    if not client:
        return None

    print(f"[Viewership Monitor] Pulling GA4 data for property {GA4_PROPERTY_ID}...")

    daily = fetch_daily_traffic(client, days_back=30)
    trends = detect_trends(daily)
    sources = fetch_traffic_sources(client, days_back=30)
    pages = fetch_top_pages(client, days_back=30)

    report = {
        "generated_at": datetime.now().isoformat(),
        "property_id": GA4_PROPERTY_ID,
        "trend_analysis": trends,
        "traffic_sources": sources,
        "top_pages": pages,
        "daily_data": daily,
    }

    with open(TREND_OUTPUT, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  VIEWERSHIP REPORT — checkannuity.com")
    print(f"  Generated: {report['generated_at'][:10]}")
    print(f"{'='*60}")
    print(f"\n  Status:  {trends['status']}")
    print(f"  Summary: {trends['message']}")

    if trends.get("changes_pct"):
        ch = trends["changes_pct"]
        print(f"\n  Week-over-Week Changes:")
        print(f"    Sessions:  {ch['sessions']:+.1f}%")
        print(f"    Users:     {ch['users']:+.1f}%")
        print(f"    Pageviews: {ch['pageviews']:+.1f}%")
        print(f"    New Users: {ch['new_users']:+.1f}%")

    if trends.get("spike_count", 0) > 0:
        print(f"\n  ** {trends['spike_count']} traffic spike(s) detected **")
        for spike in trends["spikes"]:
            print(f"    {spike['date']}: {spike['sessions']} sessions (avg: {trends['avg_daily_sessions']})")

    if sources:
        print(f"\n  Top Traffic Sources:")
        for s in sources[:5]:
            print(f"    {s['channel']:20s} {s['source']:20s} {s['sessions']:>5d} sessions")

    if pages:
        print(f"\n  Top Pages:")
        for p in pages[:5]:
            print(f"    {p['page']:40s} {p['pageviews']:>5d} views")

    print(f"\n  Full report saved to: {TREND_OUTPUT}")
    print(f"{'='*60}\n")

    return report


def get_viewership_for_pipeline():
    """
    Called by lead_pipeline.py to check if viewership is rising.
    Returns a dict with current status and whether to boost lead scores.
    """
    if os.path.exists(TREND_OUTPUT):
        with open(TREND_OUTPUT) as f:
            report = json.load(f)

        generated = report.get("generated_at", "")
        if generated:
            gen_date = datetime.fromisoformat(generated).date()
            if gen_date >= (datetime.now().date() - timedelta(days=1)):
                trend = report.get("trend_analysis", {})
                return {
                    "status": trend.get("status", "unknown"),
                    "rising": trend.get("status") in ("RISING", "SURGING"),
                    "surging": trend.get("status") == "SURGING",
                    "session_change_pct": trend.get("changes_pct", {}).get("sessions", 0),
                    "spike_today": any(
                        s["date"] == datetime.now().strftime("%Y%m%d")
                        for s in trend.get("spikes", [])
                    ),
                }

    return {"status": "no_data", "rising": False, "surging": False, "session_change_pct": 0, "spike_today": False}


if __name__ == "__main__":
    run_viewership_report()
