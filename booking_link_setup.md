# Meeting Booking Setup

**INTERNAL ONLY** -- how we get meetings on Mac's calendar with minimal friction.

---

## Approach: Ask Mac First

In the onboarding call, we ask Mac:

> "Do you have a Calendly or booking link you use, or do you prefer we just put things directly on your calendar? We can set one up for you if that's easier."

Three possible answers and what to do for each:

---

## Option A: Mac Already Has a Booking Link

If Mac already uses Calendly, Cal.com, Acuity, or similar:

1. Get the link from him
2. Test it ourselves -- book a fake meeting, confirm it shows up on his calendar
3. Use this link in the warm handoff email when a prospect responds positively
4. Done. No setup needed.

**Warm handoff integration:**
In the handoff email, replace the manual scheduling with:
> "You can book a time directly here: [Mac's booking link]"

---

## Option B: Mac Wants Us to Handle It (No Booking Link)

If Mac says "just put things on my calendar":

1. Get calendar access -- Mac shares his Google/Outlook calendar with us (editor access)
2. We manually create calendar invites when a prospect confirms interest
3. Attach the meeting brief to the invite body
4. This works fine for trial week volume (2-3 meetings)

**For trial week this is the simplest path.** No new tool for Mac to learn.

Long-term: we automate this with a booking link anyway so prospects can self-schedule.

---

## Option C: Mac Wants Us to Set One Up

If Mac says "set something up for me":

### Recommended: Calendly (Free Tier)

**Why Calendly:**
- Free tier handles everything we need
- Mac doesn't need to manage it -- we set it up, he just shows up
- Integrates with Google Calendar and Outlook
- Prospects self-book, reducing our manual work
- Automatable long-term (API available)

**Setup Steps:**

1. Go to [calendly.com](https://calendly.com) and create an account using Mac's email
   - Or: create under our admin email and connect Mac's calendar

2. Connect Mac's calendar:
   - Settings > Calendar Connections > Connect Google Calendar (or Outlook)
   - Grant read/write access so Calendly can check availability and create events

3. Create one event type:
   - **Name:** "Complimentary Retirement Review"
   - **Duration:** 30 minutes (or 15 if Mac prefers shorter)
   - **Location:** Phone call (Mac calls them, or they call Mac -- confirm his preference)
   - **Availability:** Based on Mac's answer from onboarding (e.g., Tue-Thu, 10am-3pm)
   - **Buffer:** 15 minutes between meetings (so Mac isn't back-to-back)
   - **Max per day:** Match Mac's stated capacity (e.g., 2-3/day max)

4. Customize the confirmation email:
   - Keep it simple: "Your meeting with Bryan McInerney is confirmed for [date/time]."
   - Include Mac's phone number or meeting dial-in
   - Don't include marketing language or links to our systems

5. Customize the reminder:
   - 24 hours before: email reminder
   - 1 hour before: email reminder (optional)

6. Get the booking link -- looks like: `calendly.com/mac-mcinerney/retirement-review`

7. Test it end-to-end:
   - Book a test meeting through the link
   - Confirm it shows up on Mac's calendar
   - Confirm the prospect gets a confirmation email
   - Confirm the reminder fires

**Share the link with Mac:** "Here's your booking link -- [link]. Prospects will use this to schedule time with you directly."

### Alternative: Cal.com (Free, Open Source)

If we want more control or don't want to use Calendly:
- Free tier, similar features
- Self-hostable if we want (not necessary)
- Setup is nearly identical to Calendly

---

## How the Booking Link Fits the System

```
Prospect responds positively to email/LinkedIn
        |
        v
We send warm handoff email (introduces Mac)
        |
        v
Handoff email includes booking link
        |
        v
Prospect self-books on Mac's calendar
        |
        v
Mac gets calendar invite + our meeting brief
        |
        v
Mac shows up. That's it.
```

Long-term automation: the warm handoff + booking link insertion gets triggered automatically by the reply classifier. Zero human involvement from prospect response to meeting on calendar.

---

## What to Do Right Now

**Before onboarding call:** Nothing. Wait to hear Mac's preference.

**After onboarding call:**
- If Option A: get his link, test it, integrate into warm handoff template
- If Option B: get calendar access, plan to create invites manually during trial week
- If Option C: set up Calendly (15 minutes), connect his calendar, test, share link

---

## Blocked Until

- [ ] Mac onboarding call completed
- [ ] Mac's scheduling preference confirmed
- [ ] Mac's calendar access or booking link obtained
