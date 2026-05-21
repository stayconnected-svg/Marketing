# Sending Infrastructure Status

**INTERNAL ONLY** -- tracks readiness for trial week email sends.
Full setup instructions: see `Domain_Setup_Guide.md`

---

## Readiness Summary

| Component | Status | Blocking Trial Week? |
|---|---|---|
| Domains purchased (5x .com) | NOT STARTED | YES |
| Google Workspace account | NOT STARTED | YES |
| Mailboxes created (10 total) | NOT STARTED | YES |
| DNS records (SPF/DKIM/DMARC) | NOT STARTED | YES |
| Hetzner VPS + Postfix | NOT STARTED | No (Track 2, parallel) |
| Email warmup started | NOT STARTED | YES — 2-3 weeks minimum |
| Google Postmaster Tools | NOT STARTED | No (monitoring) |
| MXToolbox monitoring | NOT STARTED | No (monitoring) |
| CAN-SPAM physical address | NOT CONFIRMED | YES |
| Test sends successful | NOT STARTED | YES |

**Current blocker: Nothing has been purchased or configured yet. Warmup takes 2-3 weeks minimum, so Day 0 needs to happen ASAP.**

---

## Critical Path (Minimum Viable for Trial Week)

These are the ONLY things needed to send 75 emails in the trial week. Everything else can come later.

### Must-Have (Week 1 send capability)

1. **Buy 1-2 domains** -- `trysimplabi.com` and `simplabihq.com` are enough to start
   - Cost: ~$20 one-time
   - Time: 10 minutes
   - Where: Cloudflare Registrar

2. **Set up Google Workspace** -- 2-4 mailboxes on those domains
   - Cost: ~$29/month (4 mailboxes)
   - Time: 30 minutes
   - Creates: `sam@trysimplabi.com`, `team@trysimplabi.com`, `sam@simplabihq.com`, `team@simplabihq.com`

3. **Configure DNS** -- SPF, DKIM, DMARC for both domains
   - Cost: $0
   - Time: 20 minutes + propagation wait
   - See Domain_Setup_Guide.md Section 4

4. **Start warmup immediately** -- manual warm sends OR sign up for Instantly ($30/month)
   - Week 1: 5-10 emails/day per mailbox (to friends, colleagues, personal accounts)
   - Week 2: 15-25/day, mix in 2-4 cold sends
   - Week 3: ready for trial week volume (50-75 total across mailboxes)

5. **Get a CAN-SPAM physical address** -- PO Box or virtual mailbox
   - Cost: ~$10-20/month
   - Time: 1 day (USPS PO Box) or instant (virtual mailbox service)
   - Options: USPS PO Box, iPostal1, Anytime Mailbox

6. **Send test emails** -- verify inbox placement before going live
   - Send to a Gmail, Outlook, and Yahoo test account you control
   - Confirm: lands in inbox (not spam), DKIM passes, SPF passes

### Can Wait (Not needed for trial week)

- Hetzner VPS + Postfix (Track 2 -- build in parallel, not blocking)
- Remaining 3 domains (scale up after trial week works)
- Remaining 6 mailboxes (scale up later)
- Microsoft SNDS registration
- DMARC policy upgrade (stays at p=none for now)

---

## Timeline to Trial Week Readiness

| Day | Action | Who |
|---|---|---|
| Day 0 | Buy 2 domains on Cloudflare | Jacob |
| Day 0 | Create Google Workspace, add domains, create 4 mailboxes | Jacob |
| Day 0 | Configure DNS (SPF, DKIM, DMARC, MX) | Jacob |
| Day 0 | Sign up for Instantly or start manual warmup | Jacob |
| Day 0 | Get CAN-SPAM physical address (virtual mailbox signup) | Jacob or Sam |
| Day 1 | Verify DNS propagation, send test emails | Jacob |
| Day 1 | Register Google Postmaster Tools | Jacob |
| Day 1 | Set up mailbox profiles (name, photo, signature) | Jacob |
| Days 1-7 | Warmup: 5-10 emails/day per mailbox to known contacts | Jacob/Sam |
| Days 8-14 | Warmup: 15-25/day, start mixing in cold sends | Jacob/Sam |
| Day 14 | Test sends to Gmail/Outlook/Yahoo -- verify inbox placement | Jacob |
| Day 15+ | **TRIAL WEEK CAN START** | Team |

**Earliest possible trial week: ~15-21 days from Day 0.**

---

## Sending Tool Options

For the trial week, choose ONE:

| Tool | Cost | Pros | Cons |
|---|---|---|---|
| **Instantly** | $30/month | Built-in warmup + sending + reply tracking. Fastest to production. | Monthly cost |
| **Gmail direct** (manual) | $0 (just GWS cost) | No extra tool, full control | Manual send, no tracking, painful at 75 emails |
| **Lemlist** | $59/month | Good personalization, built-in warmup | More expensive, more features than we need right now |
| **Smartlead** | $39/month | Multi-mailbox rotation built-in, good deliverability | Slightly more complex setup |

**Recommendation for trial week: Instantly.** $30/month, handles warmup + sending + reply detection. Connects to Google Workspace mailboxes. Can be automated later. Drop it if we build custom sending.

---

## Action Items

- [ ] Jacob: Buy `trysimplabi.com` and `simplabihq.com` on Cloudflare
- [ ] Jacob: Create Google Workspace account, verify domains
- [ ] Jacob: Create 4 mailboxes with profiles and signatures
- [ ] Jacob: Configure DNS records for both domains
- [ ] Jacob: Sign up for Instantly (or alternative) and connect mailboxes
- [ ] Jacob/Sam: Start warmup sends Day 1
- [ ] Jacob/Sam: Get CAN-SPAM physical address sorted
- [ ] Jacob: Send test emails Day 1, verify inbox placement
- [ ] Jacob: Register Google Postmaster Tools for both domains
- [ ] Jacob: Run DNS verification checks (dig commands in Domain_Setup_Guide.md Section 4)
