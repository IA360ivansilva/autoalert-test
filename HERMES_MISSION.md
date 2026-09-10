# 🎯 HERMES MISSION - IVAN'S AGENT SMS CAMPAIGN

**Target Agent:** Hermes (Chief of Staff/Orquestrador)  
**Status:** READY FOR DEPLOYMENT  
**Created:** 2026-09-09

---

## 📋 MISSION BRIEF

Deploy Ivan's Agent personalized landing page + SMS campaign to 2,907 Kia dealership leads.

---

## 🔗 LANDING PAGE (READY)

**Page URL (when deployed):**
```
https://askivan.co/edson-david-lower-payment.html
```

**Location:**
- GitHub: https://github.com/IA360ivansilva/autoalert-test/blob/main/edson-david-lower-payment.html
- Raw: https://raw.githubusercontent.com/IA360ivansilva/autoalert-test/main/edson-david-lower-payment.html

**What it does:**
- ✅ Personalized per lead (name, vehicle, lease date, payment savings)
- ✅ Shows current payment vs. estimated new payment
- ✅ Mobile-responsive (sticky footer with call buttons)
- ✅ Direct call buttons: (954) 860-0537
- ✅ Branded as Phil Smith Kia + Ivan Silva Sales

**Example data (Edson):**
- Current: 2023 Kia Sportage
- Lease ends: Sep 17, 2026
- Current payment: $500/mo
- New payment: $447/mo
- Savings: $53/month

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Copy Landing Page to Cloud

Choose ONE:

**Option A - Git (recommended):**
```bash
cd /var/www/askivan.co
git clone https://github.com/IA360ivansilva/autoalert-test.git
cp autoalert-test/edson-david-lower-payment.html ./
```

**Option B - Direct curl:**
```bash
curl -o /var/www/askivan.co/edson-david-lower-payment.html \
  https://raw.githubusercontent.com/IA360ivansilva/autoalert-test/main/edson-david-lower-payment.html
```

**Option C - SCP (if you have local copy):**
```bash
scp /path/to/edson-david-lower-payment.html user@server:/var/www/askivan.co/
```

### Step 2: Verify Deployment

```bash
curl -I https://askivan.co/edson-david-lower-payment.html
# Should return: HTTP 200 OK
```

### Step 3: Test Page

Open in browser:
```
https://askivan.co/edson-david-lower-payment.html
```

Verify:
- [ ] Page loads (dark theme, responsive)
- [ ] Edson's data shows correctly
- [ ] Call buttons work (tel: links)
- [ ] Mobile view works (sticky footer)

---

## 📱 NEXT: SMS CAMPAIGN

After landing page is live, we'll:

1. **Generate 2,907 personalized pages** (one per lead)
2. **Send SMS via Composio + Dialpad:**
   - API Key: `ak_5MbHYIv9pnaipo1HpJMc`
   - Message template: "Hi {NAME}, lease ends soon! Check savings: askivan.co/lead-{PHONE}.html -Ivan"
3. **Track responses** in manifest.json

CSV file has 2,907 leads ready:
- Nome (name)
- Primeiro Nome (first name)
- Cell/Telefone (phone)
- Carro Atual (vehicle)
- Data Vencimento (lease date)
- Nao Ligar (do-not-call flag)

---

## ⚙️ TOOLS AVAILABLE

**Scripts in repo:**
- `generate-lead-pages.py` - Create personalized HTML (2,907x)
- `send-sms-via-composio.py` - Send SMS via Dialpad
- `AUTOALERT_2907_CLIENTES.csv` - Lead data

**Commands ready:**
```bash
# Generate first 5 pages (test)
python3 generate-lead-pages.py --csv AUTOALERT_2907_CLIENTES.csv --limit 5

# Send SMS to 5 leads (test)
python3 send-sms-via-composio.py --csv AUTOALERT_2907_CLIENTES.csv --limit 5

# Send to full 2,907
python3 send-sms-via-composio.py --csv AUTOALERT_2907_CLIENTES.csv --limit 2907
```

---

## ✅ SUCCESS CRITERIA

- [ ] Landing page deployed to askivan.co
- [ ] Page loads and displays correctly
- [ ] Call buttons work
- [ ] 2,907 personalized pages generated
- [ ] SMS sent to leads (with tracking)
- [ ] Responses logged in manifest.json
- [ ] Scale to full campaign

---

## 🔐 CREDENTIALS (You have these)

```
Composio API Key: ak_5MbHYIv9pnaipo1HpJMc
Dialpad Integration: Connected via Composio
Lead Data CSV: AUTOALERT_2907_CLIENTES.csv (2,907 records)
Landing Page: Ready in GitHub
```

---

## 📞 TEST CONTACT

Send test SMS to: **9548600537**

Expected message:
```
Hi there, we found a Kia upgrade opportunity for you!
Check details: askivan.co/edson-david-lower-payment.html
Call (954) 860-0537 -Ivan
```

---

## 📝 FILES

**GitHub repo:**
- https://github.com/IA360ivansilva/autoalert-test

**Key files:**
- `edson-david-lower-payment.html` ← Landing page (READY)
- `generate-lead-pages.py` ← Batch generator
- `send-sms-via-composio.py` ← SMS sender
- `AUTOALERT_2907_CLIENTES.csv` ← Lead data
- `manifest.json` ← Tracking

---

**Ready to deploy! 🚀**

Questions? Check the README or ask directly.
