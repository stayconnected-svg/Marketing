# Cold Email Infrastructure Setup Guide

> **Two parallel tracks:** Google Workspace for immediate trusted sending, Hetzner VPS + Postfix for long-term self-hosted capacity.

---

## Table of Contents

1. [Domain Purchase](#1-domain-purchase)
2. [Google Workspace Setup (Track 1)](#2-google-workspace-setup-track-1)
3. [Hetzner VPS + Postfix Setup (Track 2)](#3-hetzner-vps--postfix-setup-track-2)
4. [DNS Configuration (Both Tracks)](#4-dns-configuration-both-tracks)
5. [Email Warming Schedule](#5-email-warming-schedule)
6. [Monitoring Setup](#6-monitoring-setup)
7. [CAN-SPAM Compliance Checklist](#7-can-spam-compliance-checklist)

---

## 1. Domain Purchase

### Why Separate Domains?

**Never use the primary business domain (simplabi.com) for cold outreach.** If a cold outreach domain gets flagged or blacklisted, it burns that domain only — your main brand domain stays clean. There is no recovery path for a primary domain with a destroyed reputation.

### Naming Conventions

Purchase **5 cold outreach domains** using recognizable variations of your brand:


| Domain             | Purpose              |
| ------------------ | -------------------- |
| `trysimplabi.com`  | Primary cold sends   |
| `simplabihq.com`   | Secondary cold sends |
| `getsimplabi.com`  | Campaign rotation    |
| `simplabiteam.com` | Campaign rotation    |
| `meetsimplabi.com` | Meeting/demo invites |


### Purchase Rules

- **TLD:** `.com` only. Avoid `.xyz`, `.info`, `.io` for cold email — `.com` has ~22% lower spam classification rates compared to alternative TLDs.
- **Cost:** ~$10/year each ($50/year total for 5 domains).
- **Registration length:** Buy for at least 1 year. Short registrations (e.g., 1 month) are a spam signal to mail providers.
- **WHOIS privacy:** Enable on every domain. Exposed WHOIS data with newly registered domains looks spammy.

### Step-by-Step: Cloudflare Registrar

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) and log in (or create an account).
2. Click **Domain Registration** → **Register Domains** in the left sidebar.
3. Search for each domain name. If available, add to cart.
4. At checkout:
  - Set registration period to **1 year** minimum.
  - WHOIS privacy is **enabled by default** on Cloudflare (free, non-optional).
  - Payment: ~$10.11/domain/year for `.com`.
5. After purchase, each domain appears under **Websites** in your dashboard.

### Step-by-Step: Namecheap (Alternative)

1. Go to [namecheap.com](https://www.namecheap.com) and log in.
2. Search for each domain and add to cart.
3. At checkout:
  - Enable **WhoisGuard** (free for the first year, included with domain).
  - Set **Auto-Renew** to ON.
  - Registration period: 1 year.
4. After purchase, go to **Domain List** → click domain → **Advanced DNS** to manage records later.

---

## 2. Google Workspace Setup (Track 1)

Google Workspace gives you immediate access to Google's sending infrastructure and trusted IP reputation. This is your primary sending engine from day one.

### Cost Breakdown


| Item                     | Cost             |
| ------------------------ | ---------------- |
| Google Workspace Starter | $7.20/user/month |
| 2 mailboxes × 5 domains  | 10 users total   |
| **Monthly total**        | **~$72/month**   |


### Mailbox Plan


| Domain             | Mailbox 1              | Mailbox 2               |
| ------------------ | ---------------------- | ----------------------- |
| `trysimplabi.com`  | `sam@trysimplabi.com`  | `team@trysimplabi.com`  |
| `simplabihq.com`   | `sam@simplabihq.com`   | `team@simplabihq.com`   |
| `getsimplabi.com`  | `sam@getsimplabi.com`  | `team@getsimplabi.com`  |
| `simplabiteam.com` | `sam@simplabiteam.com` | `team@simplabiteam.com` |
| `meetsimplabi.com` | `sam@meetsimplabi.com` | `team@meetsimplabi.com` |


### Step-by-Step Setup

#### A. Create the Google Workspace Account

1. Go to [workspace.google.com](https://workspace.google.com) → **Get Started**.
2. Enter your business name and number of employees.
3. Enter your first cold outreach domain (e.g., `trysimplabi.com`) when prompted for "a domain you already own."
4. Create the first admin user (e.g., `sam@trysimplabi.com`).
5. Select the **Business Starter** plan ($7.20/user/month).
6. Complete billing setup with a credit card.

#### B. Verify Domain Ownership

1. After signup, Google asks you to verify you own the domain.
2. Google provides a **TXT verification record**. It looks like: `google-site-verification=XXXXXXXXXXXXXXXXXXXXXXX`
3. Go to your domain registrar (Cloudflare or Namecheap):
  - **Cloudflare:** Go to the domain → **DNS** → **Records** → **Add record** → Type: `TXT`, Name: `@`, Content: the verification string.
  - **Namecheap:** Go to **Domain List** → domain → **Advanced DNS** → **Add New Record** → Type: `TXT Record`, Host: `@`, Value: the verification string.
4. Wait 5–15 minutes, then click **Verify** in Google Admin Console.

#### C. Add Remaining Domains

1. In Google Admin Console ([admin.google.com](https://admin.google.com)), go to **Account** → **Domains** → **Manage domains**.
2. Click **Add a domain** → select **Secondary domain**.
3. Enter the next domain (e.g., `simplabihq.com`).
4. Verify ownership with a TXT record (same process as above).
5. Repeat for all 5 domains.

#### D. Create User Accounts (Mailboxes)

1. In Google Admin Console, go to **Directory** → **Users**.
2. Click **Add new user**.
3. Fill in:
  - First name: `Sam` (or the sender persona name)
  - Last name: Your company last name
  - Primary email: `sam@trysimplabi.com`
4. Set a password and click **Add New User**.
5. Repeat to create the second mailbox: `team@trysimplabi.com`.
6. Repeat for all domains until you have 10 users total.

#### E. Generate DKIM Keys (Do This Now)

1. In Google Admin Console, go to **Apps** → **Google Workspace** → **Gmail**.
2. Click **Authenticate email**.
3. Select a domain from the dropdown.
4. Click **Generate New Record**.
  - DKIM key bit length: **2048** (recommended).
  - Prefix selector: leave as `google` (default).
5. Google gives you a TXT record name and value. **Copy both — you'll add them in the DNS section below.**
6. Repeat for each domain.

#### F. Complete Each Mailbox Profile

For each of the 10 mailboxes, log in at [mail.google.com](https://mail.google.com) and:

1. Upload a professional profile photo (headshot or company logo).
2. Set a proper display name (e.g., "Sam at SimplABI").
3. Create an email signature with:
  - Full name
  - Title
  - Company website (use the cold outreach domain, not primary domain)
  - Phone number (optional)

This establishes legitimacy and reduces spam classification.

---

## 3. Hetzner VPS + Postfix Setup (Track 2)

This track runs in parallel. While Google Workspace handles production sends, you're building self-hosted sending capacity that will take over or supplement GWS after warming.

### Why Hetzner?

- **Port 25 is open by default** (unlike AWS, GCP, Azure which block it).
- CX23 instance: 2 vCPU, 4 GB RAM, 40 GB SSD, 20 TB traffic — ~~€3.79/month (~~$4/month).
- Clean IP ranges with reasonable reputation.
- Reverse DNS (PTR record) configurable from the dashboard.

### Step-by-Step: Provision the VPS

#### A. Create a Hetzner Account

1. Go to [hetzner.com/cloud](https://www.hetzner.com/cloud) and sign up.
2. Complete identity verification (they may request ID upload — this is normal and typically resolves within 24 hours).
3. Add a payment method (credit card or PayPal).

#### B. Create the Server

1. In the Hetzner Cloud Console, click **Add Server**.
2. Configure:
  - **Location:** Ashburn (US East) or Falkenstein (EU) — pick the region closest to your recipients.
  - **Image:** Ubuntu 22.04
  - **Type:** Shared vCPU → **CX23** (2 vCPU, 4 GB RAM)
  - **Networking:** Public IPv4 enabled (you need a static IP for mail)
  - **SSH Key:** Add your public SSH key (generate one with `ssh-keygen -t ed25519` if you don't have one)
  - **Name:** `mail-simplabi` (or similar)
3. Click **Create & Buy Now**.
4. Note the **public IPv4 address** — you'll need it everywhere. Referred to as `YOUR_VPS_IP` throughout this guide.

#### C. Set Up Reverse DNS (PTR Record)

This is critical. Mail servers check that your IP's PTR record matches your sending hostname.

1. In Hetzner Cloud Console, click on your server → **Networking**.
2. Find the IPv4 address → click the **"..."** menu → **Edit Reverse DNS**.
3. Set the PTR record to: `mail.trysimplabi.com` (your primary sending hostname).
4. Save.

#### D. Initial Server Setup

SSH into your server:

```bash
ssh root@YOUR_VPS_IP
```

Update the system and set the hostname:

```bash
apt update && apt upgrade -y

hostnamectl set-hostname mail.trysimplabi.com

# Verify
hostname -f
# Should output: mail.trysimplabi.com
```

Edit `/etc/hosts` to map the hostname:

```bash
nano /etc/hosts
```

Add this line (replace with your actual IP):

```
YOUR_VPS_IP    mail.trysimplabi.com    mail
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

#### E. Install Postfix

```bash
apt install postfix -y
```

When the configuration screen appears:

- Select **Internet Site**.
- Set the system mail name to: `trysimplabi.com`

#### F. Configure Postfix

Edit the main configuration:

```bash
nano /etc/postfix/main.cf
```

Replace the contents with (adjust values marked with `CHANGE_ME`):

```ini
# Basic settings
smtpd_banner = $myhostname ESMTP
biff = no
append_dot_mydomain = no
readme_directory = no
compatibility_level = 3.6

# TLS parameters (outbound)
smtp_tls_security_level = may
smtp_tls_CApath = /etc/ssl/certs
smtp_tls_loglevel = 1

# TLS parameters (inbound)
smtpd_tls_cert_file = /etc/letsencrypt/live/mail.trysimplabi.com/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/mail.trysimplabi.com/privkey.pem
smtpd_tls_security_level = may
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_loglevel = 1

# Network settings
myhostname = mail.trysimplabi.com
mydomain = trysimplabi.com
myorigin = $mydomain
mydestination = localhost
mynetworks = 127.0.0.0/8 [::1]/128
inet_interfaces = all
inet_protocols = ipv4

# Virtual mailbox settings
virtual_mailbox_domains = trysimplabi.com, simplabihq.com, getsimplabi.com, simplabiteam.com, meetsimplabi.com
virtual_mailbox_base = /var/mail/vhosts
virtual_mailbox_maps = hash:/etc/postfix/vmailbox
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000
virtual_alias_maps = hash:/etc/postfix/virtual

# Delivery limits (conservative for cold email)
smtp_destination_concurrency_limit = 2
smtp_destination_rate_delay = 5s
default_destination_rate_delay = 5s
initial_destination_concurrency = 1
default_process_limit = 20

# Message size limit (10MB)
message_size_limit = 10240000

# Queue settings
maximal_queue_lifetime = 3d
bounce_queue_lifetime = 1d

# DKIM milter
milter_protocol = 6
milter_default_action = accept
smtpd_milters = inet:localhost:8891
non_smtpd_milters = inet:localhost:8891
```

> **Note:** The TLS certificate lines will error until you install Let's Encrypt (next step). That's fine — complete the steps in order.

#### G. Install Let's Encrypt TLS Certificate

You need a valid TLS certificate for your mail server. First, add a DNS `A` record pointing `mail.trysimplabi.com` → `YOUR_VPS_IP` (see DNS section). Then:

```bash
apt install certbot -y

certbot certonly --standalone -d mail.trysimplabi.com
```

Follow the prompts. The certificate files are stored at:

- `/etc/letsencrypt/live/mail.trysimplabi.com/fullchain.pem`
- `/etc/letsencrypt/live/mail.trysimplabi.com/privkey.pem`

Set up auto-renewal:

```bash
systemctl enable certbot.timer
systemctl start certbot.timer
```

#### H. Create Virtual Mailbox Users

Create the vmail user and directory structure:

```bash
groupadd -g 5000 vmail
useradd -g vmail -u 5000 -d /var/mail/vhosts -s /usr/sbin/nologin -m vmail

mkdir -p /var/mail/vhosts/trysimplabi.com/sam
mkdir -p /var/mail/vhosts/trysimplabi.com/team
mkdir -p /var/mail/vhosts/simplabihq.com/sam
mkdir -p /var/mail/vhosts/simplabihq.com/team
mkdir -p /var/mail/vhosts/getsimplabi.com/sam
mkdir -p /var/mail/vhosts/getsimplabi.com/team
mkdir -p /var/mail/vhosts/simplabiteam.com/sam
mkdir -p /var/mail/vhosts/simplabiteam.com/team
mkdir -p /var/mail/vhosts/meetsimplabi.com/sam
mkdir -p /var/mail/vhosts/meetsimplabi.com/team

chown -R vmail:vmail /var/mail/vhosts
```

Create the virtual mailbox map:

```bash
nano /etc/postfix/vmailbox
```

Add:

```
sam@trysimplabi.com         trysimplabi.com/sam/
team@trysimplabi.com        trysimplabi.com/team/
sam@simplabihq.com          simplabihq.com/sam/
team@simplabihq.com         simplabihq.com/team/
sam@getsimplabi.com         getsimplabi.com/sam/
team@getsimplabi.com        getsimplabi.com/team/
sam@simplabiteam.com        simplabiteam.com/sam/
team@simplabiteam.com       simplabiteam.com/team/
sam@meetsimplabi.com        meetsimplabi.com/sam/
team@meetsimplabi.com       meetsimplabi.com/team/
```

Create the virtual alias map (for catch-all or forwarding, if desired):

```bash
nano /etc/postfix/virtual
```

Add (optional — forwards postmaster to your main admin):

```
postmaster@trysimplabi.com      sam@trysimplabi.com
postmaster@simplabihq.com       sam@simplabihq.com
postmaster@getsimplabi.com      sam@getsimplabi.com
postmaster@simplabiteam.com     sam@simplabiteam.com
postmaster@meetsimplabi.com     sam@meetsimplabi.com
```

Hash the maps and restart:

```bash
postmap /etc/postfix/vmailbox
postmap /etc/postfix/virtual
systemctl restart postfix
```

#### I. Install and Configure OpenDKIM

```bash
apt install opendkim opendkim-tools -y
```

Edit the OpenDKIM config:

```bash
nano /etc/opendkim.conf
```

Replace contents with:

```ini
AutoRestart             Yes
AutoRestartRate         10/1h
Syslog                  Yes
SyslogSuccess           Yes
LogWhy                  Yes

Canonicalization        relaxed/simple
ExternalIgnoreList      refile:/etc/opendkim/TrustedHosts
InternalHosts           refile:/etc/opendkim/TrustedHosts
KeyTable                refile:/etc/opendkim/KeyTable
SigningTable             refile:/etc/opendkim/SigningTable

Mode                    sv
PidFile                 /run/opendkim/opendkim.pid
SignatureAlgorithm      rsa-sha256
UserID                  opendkim:opendkim

Socket                  inet:8891@localhost
```

Create the directory structure:

```bash
mkdir -p /etc/opendkim/keys
```

Create the TrustedHosts file:

```bash
nano /etc/opendkim/TrustedHosts
```

Add:

```
127.0.0.1
localhost
mail.trysimplabi.com
trysimplabi.com
simplabihq.com
getsimplabi.com
simplabiteam.com
meetsimplabi.com
```

Generate DKIM keys for each domain:

```bash
for domain in trysimplabi.com simplabihq.com getsimplabi.com simplabiteam.com meetsimplabi.com; do
    mkdir -p /etc/opendkim/keys/$domain
    opendkim-genkey -b 2048 -d $domain -D /etc/opendkim/keys/$domain -s mail -v
    chown opendkim:opendkim /etc/opendkim/keys/$domain/mail.private
    chmod 600 /etc/opendkim/keys/$domain/mail.private
done
```

Create the KeyTable:

```bash
nano /etc/opendkim/KeyTable
```

Add:

```
mail._domainkey.trysimplabi.com     trysimplabi.com:mail:/etc/opendkim/keys/trysimplabi.com/mail.private
mail._domainkey.simplabihq.com      simplabihq.com:mail:/etc/opendkim/keys/simplabihq.com/mail.private
mail._domainkey.getsimplabi.com     getsimplabi.com:mail:/etc/opendkim/keys/getsimplabi.com/mail.private
mail._domainkey.simplabiteam.com    simplabiteam.com:mail:/etc/opendkim/keys/simplabiteam.com/mail.private
mail._domainkey.meetsimplabi.com    meetsimplabi.com:mail:/etc/opendkim/keys/meetsimplabi.com/mail.private
```

Create the SigningTable:

```bash
nano /etc/opendkim/SigningTable
```

Add:

```
*@trysimplabi.com       mail._domainkey.trysimplabi.com
*@simplabihq.com        mail._domainkey.simplabihq.com
*@getsimplabi.com       mail._domainkey.getsimplabi.com
*@simplabiteam.com      mail._domainkey.simplabiteam.com
*@meetsimplabi.com      mail._domainkey.meetsimplabi.com
```

Retrieve the public keys (you'll add these as DNS records):

```bash
for domain in trysimplabi.com simplabihq.com getsimplabi.com simplabiteam.com meetsimplabi.com; do
    echo "=== DKIM public key for $domain ==="
    cat /etc/opendkim/keys/$domain/mail.txt
    echo ""
done
```

**Save this output.** Each block contains the TXT record value you need for DNS.

Start and enable OpenDKIM:

```bash
systemctl enable opendkim
systemctl start opendkim
systemctl restart postfix
```

#### J. Configure the Firewall

```bash
apt install ufw -y

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 25/tcp    # SMTP
ufw allow 587/tcp   # Submission (for authenticated sending)
ufw allow 993/tcp   # IMAPS (if you add Dovecot later)
ufw allow 80/tcp    # HTTP (for Let's Encrypt renewals)
ufw allow 443/tcp   # HTTPS

ufw enable
```

#### K. Test the Postfix Installation

Send a test email from the command line:

```bash
echo "Test email from Postfix on Hetzner" | mail -s "Postfix Test" -r sam@trysimplabi.com your-personal-email@gmail.com
```

Check the mail log for errors:

```bash
tail -f /var/log/mail.log
```

You should see `status=sent` with a `250` response code. If the test lands in spam, that's expected — the domain is brand new. Warming (Section 5) will fix this.

---

## 4. DNS Configuration (Both Tracks)

Configure the following records for **every** cold outreach domain. Examples use `trysimplabi.com` — repeat identically for all 5 domains.

### A Record (Postfix server hostname)

Only needed once, on the primary Postfix domain:


| Type | Host   | Value         | TTL  |
| ---- | ------ | ------------- | ---- |
| A    | `mail` | `YOUR_VPS_IP` | Auto |


### MX Records

#### For Google Workspace Domains (Track 1 primary)


| Type | Host | Value                     | Priority | TTL  |
| ---- | ---- | ------------------------- | -------- | ---- |
| MX   | `@`  | `ASPMX.L.GOOGLE.COM`      | 1        | Auto |
| MX   | `@`  | `ALT1.ASPMX.L.GOOGLE.COM` | 5        | Auto |
| MX   | `@`  | `ALT2.ASPMX.L.GOOGLE.COM` | 5        | Auto |
| MX   | `@`  | `ALT3.ASPMX.L.GOOGLE.COM` | 10       | Auto |
| MX   | `@`  | `ALT4.ASPMX.L.GOOGLE.COM` | 10       | Auto |


#### For Postfix-Only Domains


| Type | Host | Value                  | Priority | TTL  |
| ---- | ---- | ---------------------- | -------- | ---- |
| MX   | `@`  | `mail.trysimplabi.com` | 10       | Auto |


> **Hybrid approach:** If a domain sends from both GWS and Postfix but you want replies going to GWS, keep the MX records pointed at Google. The Postfix server only needs to *send*, not receive.

### SPF Record


| Scenario               | Type | Host | Value                                                 |
| ---------------------- | ---- | ---- | ----------------------------------------------------- |
| GWS only               | TXT  | `@`  | `v=spf1 include:_spf.google.com ~all`                 |
| Postfix only           | TXT  | `@`  | `v=spf1 ip4:YOUR_VPS_IP ~all`                         |
| **Both (recommended)** | TXT  | `@`  | `v=spf1 include:_spf.google.com ip4:YOUR_VPS_IP ~all` |


> Use `~all` (softfail) during setup. Switch to `-all` (hardfail) after confirming everything works.

### DKIM Record

#### For Google Workspace

After generating the DKIM key in Google Admin Console (Section 2E), add:


| Type | Host                | Value                                    | TTL  |
| ---- | ------------------- | ---------------------------------------- | ---- |
| TXT  | `google._domainkey` | (paste the full value from Google Admin) | Auto |


Then go back to Google Admin Console → **Authenticate email** → click **Start Authentication** for the domain.

#### For Postfix (OpenDKIM)

From the output of the `cat /etc/opendkim/keys/DOMAIN/mail.txt` command (Section 3I), add:


| Type | Host              | Value                          | TTL  |
| ---- | ----------------- | ------------------------------ | ---- |
| TXT  | `mail._domainkey` | (paste the full `p=...` value) | Auto |


> **Important:** The DKIM public key is often split across multiple lines in the file. When entering it in your DNS provider, combine it into a single string with no spaces or line breaks inside the `p=` value.

### DMARC Record


| Type | Host     | Value                                                | TTL  |
| ---- | -------- | ---------------------------------------------------- | ---- |
| TXT  | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@trysimplabi.com` | Auto |


**DMARC Policy Progression:**


| Timeframe       | Policy         | What It Does                        |
| --------------- | -------------- | ----------------------------------- |
| Day 0 – Day 30  | `p=none`       | Monitor only, no action on failures |
| Day 30 – Day 60 | `p=quarantine` | Failed emails go to spam            |
| Day 60+         | `p=reject`     | Failed emails are rejected entirely |


Update the DMARC record as you progress through each phase.

### DNS Checklist Per Domain

Run through this for all 5 domains:

- MX records added (Google or Postfix)
- SPF TXT record added
- DKIM TXT record added (Google and/or Postfix)
- DMARC TXT record added
- A record for `mail.` subdomain (if using Postfix)
- Google domain verification TXT record added

### Verify DNS Propagation

After adding all records, verify them:

```bash
# Check MX
dig MX trysimplabi.com +short

# Check SPF
dig TXT trysimplabi.com +short

# Check DKIM (Google)
dig TXT google._domainkey.trysimplabi.com +short

# Check DKIM (Postfix)
dig TXT mail._domainkey.trysimplabi.com +short

# Check DMARC
dig TXT _dmarc.trysimplabi.com +short
```

All records should resolve within 5–60 minutes (Cloudflare is near-instant, Namecheap can take up to 48 hours).

---

## 5. Email Warming Schedule

Warming builds sender reputation gradually. Both GWS and Postfix mailboxes follow the same schedule — but GWS starts in production (real sends) faster because it inherits Google's infrastructure trust.

### Week 1: Days 1–7 (Foundation)


| Metric                     | Target                                 |
| -------------------------- | -------------------------------------- |
| Emails per mailbox per day | 5–10                                   |
| Recipients                 | Friends, colleagues, personal accounts |
| Reply rate target          | 40%+                                   |


**What to do:**

1. Send conversational emails to people you know. Ask a question they'll naturally reply to.
2. Have recipients:
  - **Open** the email
  - **Reply** to it (even a one-word reply helps)
  - **Move it out of spam** if it lands there (trains the provider)
  - **Star or mark as important** (optional, helps on Gmail)
3. Send from each of the 10 GWS mailboxes and each of the 10 Postfix mailboxes.
4. Vary sending times — don't blast all 10 at 9:00 AM.

### Week 2: Days 8–14 (Expansion)


| Metric                     | Target    |
| -------------------------- | --------- |
| Emails per mailbox per day | 15–25     |
| Warm emails                | 13–21/day |
| Cold test emails           | 2–4/day   |
| Reply rate target          | 25%+      |


**What to do:**

1. Continue warm sends to known contacts.
2. Add 2–4 **real cold emails per day per mailbox** — start with your best prospects.
3. Monitor for bounces. If bounce rate exceeds 3%, slow down.
4. Check the spam folder of a test Gmail/Outlook account you control.

### Week 3: Days 15–21 (Transition)


| Metric                     | Target    |
| -------------------------- | --------- |
| Emails per mailbox per day | 30–50     |
| Warm emails                | 10–15/day |
| Cold emails                | 20–35/day |
| Reply rate target          | 15%+      |


**What to do:**

1. Shift the ratio toward cold sends.
2. Keep a baseline of warm sends to maintain reply metrics.
3. Monitor Google Postmaster Tools for domain reputation (should be "Medium" or "High" by now).

### After Day 21: Full Production


| Metric                     | Target          |
| -------------------------- | --------------- |
| Emails per mailbox per day | 50–100          |
| Warmup volume maintained   | 20–30% of total |
| Cold emails                | 35–70/day       |


**Critical rules for the first 90 days:**

1. **Keep 20–30% warmup volume** running alongside cold sends. This maintains healthy engagement metrics.
2. Never exceed **100 emails/day per mailbox**. Going higher risks throttling or blocks.
3. Rotate sending across mailboxes — don't run all volume through one address.
4. Space emails at least **60–90 seconds apart** (configure in your sending tool or Postfix rate delay).
5. If any domain's reputation drops to "Low" in Google Postmaster Tools, immediately reduce volume by 50% and increase warmup ratio.

### Warming Tools (Optional, Recommended)

Automated warmup services send and receive emails on your behalf to simulate engagement:


| Tool      | Cost              | Notes                               |
| --------- | ----------------- | ----------------------------------- |
| Instantly | $30/month         | Built-in warmup + sending tool      |
| Warmbox   | $15/month         | Dedicated warmup service            |
| Lemwarm   | Free with Lemlist | If you use Lemlist for outreach     |
| Mailwarm  | $69/month         | Aggressive warmup, good for Postfix |


These are optional but reduce manual effort significantly.

---

## 6. Monitoring Setup

### A. Google Postmaster Tools (Free)

Monitors domain reputation, spam rate, and authentication results for mail sent to Gmail recipients.

1. Go to [postmaster.google.com](https://postmaster.google.com).
2. Click **Get Started** and sign in with a Google account.
3. Click **+** to add a domain.
4. Enter `trysimplabi.com`.
5. Google provides a DNS TXT verification record — add it to your domain.
6. After verification, repeat for all 5 domains.
7. **Check weekly.** Key dashboards:
  - **Spam Rate:** Must stay below 0.3%. Above 0.5% triggers throttling.
  - **Domain Reputation:** Target "Medium" or "High."
  - **IP Reputation:** For your Postfix VPS IP.
  - **Authentication:** SPF, DKIM, DMARC pass rates should be 95%+.

### B. Microsoft SNDS (Free)

Monitors reputation for mail sent to Outlook/Hotmail recipients.

1. Go to [sendersupport.olc.protection.outlook.com/snds](https://sendersupport.olc.protection.outlook.com/snds/).
2. Sign in with a Microsoft account.
3. Click **Request Access** and enter your Postfix VPS IP address.
4. Microsoft sends a verification email to the postmaster address — make sure `postmaster@trysimplabi.com` works.
5. After verification, check monthly for:
  - Spam complaint rates
  - Trap hits
  - Filter results

### C. MXToolbox Blacklist Monitoring (Free Tier)

1. Go to [mxtoolbox.com/blacklists.aspx](https://mxtoolbox.com/blacklists.aspx).
2. Enter your Postfix VPS IP address and click **Blacklist Check**.
3. Verify you're not listed on any blacklists.
4. Create a free account and set up **Blacklist Monitoring**:
  - Add your VPS IP address.
  - Add each of your 5 domains.
  - Enable email alerts for new listings.
5. **Check weekly**, or rely on email alerts.

### D. Ongoing Monitoring Cadence


| Task                                          | Frequency                          |
| --------------------------------------------- | ---------------------------------- |
| Google Postmaster Tools check                 | Weekly                             |
| MXToolbox blacklist scan                      | Weekly                             |
| Microsoft SNDS check                          | Monthly                            |
| Bounce rate review (from sending tool)        | Daily                              |
| DMARC aggregate reports review                | Weekly                             |
| Postfix mail log review (`/var/log/mail.log`) | Daily (first 30 days), then weekly |


### E. Quick Health Check Commands (Postfix)

Run these from your VPS to spot issues:

```bash
# Check mail queue (should be near-empty)
mailq

# Count deferred emails
mailq | grep -c "^[A-F0-9]"

# Check for recent errors
grep -i "error\|reject\|blocked" /var/log/mail.log | tail -20

# Check Postfix is running
systemctl status postfix

# Check OpenDKIM is running
systemctl status opendkim
```

---

## 7. CAN-SPAM Compliance Checklist

Every cold email sent from this infrastructure **must** comply with the CAN-SPAM Act (U.S.) to avoid legal penalties of up to **$51,744 per violation**.

### Required Elements in Every Email


| Requirement                             | Details                                                                                                                                                   | Status |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| **Accurate "From" field**               | The sender name and email address must be truthful. No impersonation.                                                                                     | ☐      |
| **Non-deceptive subject line**          | Subject must relate to the content of the email. No bait-and-switch.                                                                                      | ☐      |
| **Physical mailing address**            | Must include a valid postal address. Can be a PO Box or registered agent address.                                                                         | ☐      |
| **Unsubscribe mechanism**               | Must include a clear way to opt out — either a link or "reply STOP to unsubscribe."                                                                       | ☐      |
| **Honor opt-outs within 10 days**       | Process unsubscribe requests within 10 business days. Automated is best.                                                                                  | ☐      |
| **Identified as an ad (if applicable)** | If the email is purely promotional, it should be identifiable as an ad. Business-to-business outreach is generally exempt from this specific requirement. | ☐      |


### Physical Address Options

You don't need to expose your home address. Options:

- **PO Box** from USPS (~$20–$40/6 months)
- **Virtual mailbox** from services like iPostal1, Anytime Mailbox (~$10/month)
- **Registered agent address** if you have an LLC

### Unsubscribe Best Practices

- **Link-based:** Include a one-click unsubscribe link in the email footer. Most cold email tools (Instantly, Lemlist, Smartlead) handle this automatically.
- **Reply-based:** Include text like "Reply STOP to unsubscribe" — simple and effective for plain-text cold emails.
- **Processing:** Use your sending tool's built-in suppression list, or maintain a master suppression list that all mailboxes check before sending.

### Email Footer Template

```
---
{Your Name}
{Your Title} | {Company Name}
{company-website.com}

{Street Address or PO Box}
{City, State ZIP}

Don't want to hear from us? Reply "unsubscribe" or click here: {unsubscribe_link}
```

### Additional Best Practices (Not Legally Required but Protect Deliverability)

- **Never buy email lists.** Build lists from LinkedIn, company websites, and verified sources.
- **Verify emails before sending.** Use tools like NeverBounce, ZeroBounce, or MillionVerifier to remove invalid addresses. Target <2% bounce rate.
- **Respect "no solicitation" signals.** If a company's website says "no cold emails," skip them.
- **Keep records.** Log consent/opt-out status for every contact. You may need to prove compliance.

---

## Quick Reference: Full Setup Timeline


| Day    | Action                                                                       |
| ------ | ---------------------------------------------------------------------------- |
| Day 0  | Purchase 5 domains, enable WHOIS privacy                                     |
| Day 0  | Sign up for Google Workspace, add all domains                                |
| Day 0  | Provision Hetzner VPS, set hostname and PTR record                           |
| Day 1  | Create 10 GWS mailboxes, set up profiles and signatures                      |
| Day 1  | Install Postfix, OpenDKIM, Let's Encrypt on VPS                              |
| Day 1  | Configure all DNS records (SPF, DKIM, DMARC, MX)                             |
| Day 2  | Verify DNS propagation, test sending from both GWS and Postfix               |
| Day 2  | Register with Google Postmaster Tools, Microsoft SNDS                        |
| Day 2  | Set up MXToolbox blacklist monitoring                                        |
| Day 2  | Begin warmup: 5–10 emails/day per mailbox                                    |
| Day 8  | Increase to 15–25/day, add 2–4 cold sends per mailbox                        |
| Day 15 | Increase to 30–50/day, shift toward cold sends                               |
| Day 21 | Full production: 50–100/day with 20–30% warmup maintained                    |
| Day 30 | Review DMARC reports, upgrade to `p=quarantine`                              |
| Day 60 | Review again, upgrade to `p=reject`                                          |
| Day 90 | Evaluate dropping warmup tool — organic engagement should sustain reputation |


---

## Cost Summary


| Item                            | Monthly Cost    | Annual Cost      |
| ------------------------------- | --------------- | ---------------- |
| 5 domains (.com)                | —               | ~$50/year        |
| Google Workspace (10 mailboxes) | ~$72/month      | ~$864/year       |
| Hetzner CX23 VPS                | ~$4/month       | ~$48/year        |
| Warmup tool (optional)          | ~$30/month      | ~$360/year       |
| **Total (with warmup tool)**    | **~$106/month** | **~$1,322/year** |
| **Total (without warmup tool)** | **~$76/month**  | **~$962/year**   |


---

*Last updated: May 15, 2026*