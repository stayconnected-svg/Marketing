# Trial Week Runbook

**INTERNAL ONLY — Mac never sees this document.**

Goal: Give Mac the experience of meetings appearing on his calendar with zero effort from him. Target: 2-3 warm leads in one week.

---

## Prerequisites (Before Starting)

- Mac onboarding call completed — answers recorded
- Sending domain purchased and DNS configured (SPF/DKIM/DMARC)
- Mailbox warmed for 2+ weeks (or use a pre-warmed mailbox)
- Mac's calendar access or booking link set up
- Mac's preferred vertical confirmed (default: dentists)
- CAN-SPAM physical address confirmed for email footer
- Simpl ABI outreach sequence reviewed and ready to send

---

## Day-by-Day Execution

### Day 0 (Setup Day — Before Trial Week Starts)

**Jacob:**

- Pull 75 prospects from `prospects_dentists_enriched.csv` (or whichever vertical Mac chose)
- Verify emails are valid (run through enrichment if not already done)
- Load prospects into sending tool
- Queue Email 1 (The Hook) for Day 1 morning send
- Generate LinkedIn queue for the week (50 prospects, 10/day)

**Sam:**

- Confirm Mac's calendar is accessible
- Test booking flow: create a test invite, confirm Mac sees it
- Prepare 3 meeting brief drafts using the template (so we're ready to fire fast when someone responds)

---

### Day 1 (Monday)

**Morning (8 AM):**

- Send Email 1 to Batch A (25 prospects)
- Send 10 LinkedIn connection requests from the daily queue

**Afternoon:**

- Monitor sending mailbox for bounces — remove bounced addresses immediately
- Check LinkedIn for connection acceptances from any prior outreach
- Log all sends in tracker

---

### Day 2 (Tuesday)

**Morning:**

- Send Email 1 to Batch B (25 prospects)
- Send 10 LinkedIn connection requests

**Afternoon:**

- Check for any Email 1 replies from Batch A
- If positive reply: immediately trigger warm handoff (see Reply Handling below)
- Log activity

---

### Day 3 (Wednesday)

**Morning:**

- Send Email 1 to Batch C (25 prospects)
- Send 10 LinkedIn connection requests

**Afternoon:**

- Check for replies from Batches A and B
- Send LinkedIn follow-up messages to anyone who accepted connections on Day 1-2
- Handle any replies

---

### Day 4 (Thursday)

**Morning:**

- Send Email 2 (The Value Add) to Batch A (Day 1 non-responders only)
- Send 10 LinkedIn connection requests

**Afternoon:**

- Monitor all inboxes for replies
- Handle any warm leads immediately
- Send LinkedIn follow-ups to new acceptances

---

### Day 5 (Friday)

**Morning:**

- Send Email 2 to Batch B (Day 2 non-responders only)
- Send 10 LinkedIn connection requests

**Afternoon:**

- Final reply check across all channels
- Compile internal results (Mac doesn't see this)
- If any leads are pending booking, get them on Mac's calendar before the weekend

---

## Reply Handling

### Positive Reply (interested, wants to talk)

1. **Respond within 1 hour** — speed matters
2. Send the warm handoff email from `simpl_abi_outreach_sequence.md` (introduces Mac by name)
3. Propose 2-3 meeting times based on Mac's availability
4. Once confirmed: create calendar invite on Mac's calendar with meeting brief attached
5. Text/message Mac (however he said he wants updates): "Meeting booked with Dr. [Name] on [Day] at [Time] — brief is on the invite"

### Negative Reply (not interested)

1. Reply politely: "Understood — appreciate your time. If anything changes down the road, the offer stands."
2. Add to suppression list — never contact again
3. Don't tell Mac about these

### Unsubscribe Request

1. Remove immediately — same day
2. Add to permanent suppression list
3. Reply confirming removal: "Done — you've been removed. Apologies for the interruption."

### Out of Office

1. Note the return date
2. Re-queue for outreach 2 days after they're back
3. Don't count as a response

### Wrong Person / Bounced

1. Remove from active list
2. If wrong person replies with a referral, treat as a new warm lead

---

## Meeting Booking Process

1. Prospect confirms interest
2. Check Mac's calendar for open slots matching his preferences
3. Propose times to prospect (or send booking link if Mac has one)
4. Once confirmed:
  - Create calendar invite
  - Write meeting brief using template (`meeting_brief_template.md`)
  - Paste brief into calendar invite body
  - Notify Mac via his preferred channel
5. Day before meeting: send Mac a reminder text with the prospect's name and one-line context

---

## What We Track (Internal Only)


| Metric                          | Where                   |
| ------------------------------- | ----------------------- |
| Emails sent per day             | Sending tool dashboard  |
| Open rate                       | Sending tool            |
| Reply rate                      | Manual count from inbox |
| Positive replies                | Manual count            |
| Meetings booked                 | Calendar                |
| LinkedIn connections sent       | LinkedIn queue tracker  |
| LinkedIn connections accepted   | Manual check            |
| LinkedIn replies                | Manual check            |
| Mac's feedback (thumbs up/down) | Text thread             |


---

## Emergency Scenarios

**Mac asks "how's the campaign going?"**

> "Going well — you've got [X] meetings coming up this week. We'll keep them coming."

Don't share metrics, open rates, or send volumes. Results = meetings.

**No replies by Day 4:**

- Don't panic. This is normal for a cold start.
- Accelerate Email 2 sends
- Increase LinkedIn volume to 15/day
- Consider sending to a second batch of 25 new prospects

**Mac gets an angry reply forwarded to him:**

- Apologize to Mac briefly: "We'll make sure that person isn't contacted again."
- Add to suppression list immediately
- Don't over-explain or make it a big deal

**LPL compliance question comes up:**

- All Simpl ABI emails (1-5) do NOT name Mac — compliant
- Only the warm handoff names Mac — that email has full LPL disclosures
- If Mac asks, say: "Everything goes out under Simpl ABI until someone's interested, then we introduce you with proper disclosures."

---

## Post-Trial-Week

After the trial week, compile results internally:

- How many sent, how many replied, how many meetings booked
- Mac's feedback on lead quality
- What worked, what didn't
- Adjust targeting, messaging, or volume for the ongoing engagement

Share with Mac: "We got you [X] meetings this week. Want us to keep going?" That's the only report he needs.