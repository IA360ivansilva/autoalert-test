# 🤖 HERMES CLOUD - KAI INTEGRATION ARCHITECTURE

**Target:** Kai (Hermes Super Agent on Cloud VPS 178.105.41.161)

---

## 📋 MISSION

Send personalized Ivan's Agent messages to Kia dealership leads via:
1. **WhatsApp** (Zap) - Primary channel
2. **SMS Dialpad** - Fallback/secondary
3. **Landing Page** - Already deployed at askivan.co

---

## 🏗️ ARCHITECTURE

### Phase 1: Verify Cloud Connection
```
✅ Hermes Cloud Status
   └─ Dialpad Integration: VERIFY CONNECTED
   └─ Composio API: VERIFY KEY ACTIVE (ak_5MbHYIv9pnaipo1HpJMc)
   └─ WhatsApp Connection: VERIFY ACTIVE
```

### Phase 2: Workflow
```
CSV Input (2,907 leads)
   ↓
Landing Page Generator (generate-lead-pages.py)
   ├─ Creates personalized HTML per lead
   ├─ Deploys to askivan.co/lead-{phone}.html
   └─ Generates SMS content + WhatsApp message
   ↓
Message Delivery (via Hermes Cloud)
   ├─ PRIMARY: WhatsApp (Zap) - auto-reply ready
   ├─ SECONDARY: SMS (Dialpad) - fallback
   └─ Track: SMS log + responses
   ↓
Lead Tracking
   └─ Log responses in manifest.json
```

### Phase 3: Data Flow
```
Input CSV Fields:
   ├─ Primeiro Nome (First name)
   ├─ Cell/Telefone Principal (Phone)
   ├─ Carro Atual (Current vehicle)
   ├─ Data Vencimento Leasing (Lease end date)
   └─ Nao Ligar (Do-not-call flag)

Generated Output:
   ├─ HTML landing page (personalized)
   ├─ WhatsApp message (auto-reply template)
   ├─ SMS content (70-160 chars)
   └─ manifest.json (tracking)
```

---

## 🎯 KAI INSTRUCTIONS

### Step 1: Verify Cloud Status
```bash
# On Hermes Cloud (178.105.41.161)
hermes status
hermes integrations --check dialpad
hermes integrations --check whatsapp
echo $COMPOSIO_API_KEY  # Should show: ak_5MbHYIv9pnaipo1HpJMc
```

### Step 2: Test SMS via Dialpad
```bash
# Send test SMS to 9548600537
hermes send-sms \
  --phone "9548600537" \
  --message "Test from Hermes Cloud Kai. Dialpad integration working! -Ivan's Agent 🤖"
```

### Step 3: Test WhatsApp
```bash
# Send test WhatsApp to your number
hermes send-whatsapp \
  --phone "9548600537" \
  --message "Test WhatsApp from Hermes Cloud. If you got this, WhatsApp integration WORKS! -Ivan 💬"
```

### Step 4: Run Landing Page Generator
```bash
python3 generate-lead-pages.py \
  --csv /path/to/AUTOALERT_2907_CLIENTES.csv \
  --limit 5 \
  --output /var/www/askivan.co/
```

### Step 5: Send Batch Messages
```bash
# Send WhatsApp + SMS to first 5 leads
hermes send-batch \
  --csv /path/to/AUTOALERT_2907_CLIENTES.csv \
  --limit 5 \
  --channels "whatsapp,sms" \
  --template "ivan-agent-personalized" \
  --track manifest.json
```

---

## 📱 MESSAGE TEMPLATES

### WhatsApp (Primary)
```
Hi {FIRST_NAME}! 👋

Your {VEHICLE} lease ends soon.
We found an option at ${NEW_PRICE}/mo (save ${SAVINGS})

See details: askivan.co/lead-{PHONE}.html

Reply YES to schedule, or call (954) 860-0537 📞
```

### SMS Dialpad (Fallback)
```
Hi {FIRST_NAME}, lease ends soon! 
Found ${SAVINGS}/mo savings on your Kia.
Details: askivan.co/lead-{PHONE}.html
Call (954) 860-0537 -Ivan
```

### Landing Page
```
URL: askivan.co/lead-{PHONE}.html
Status: DEPLOYED ✅
Content: Personalized (vehicle, lease date, savings)
CTA: Call button + Online booking
```

---

## ✅ SUCCESS CRITERIA

- [ ] Hermes Cloud confirms Dialpad connected
- [ ] Hermes Cloud confirms WhatsApp connected  
- [ ] Test SMS sent to 9548600537 ✅ RECEIVED
- [ ] Test WhatsApp sent to 9548600537 ✅ RECEIVED
- [ ] Landing page deploys correctly
- [ ] Batch of 5 leads sends successfully
- [ ] Manifest.json logs all deliveries
- [ ] Scale to 100 leads (then 2,907)

---

## 🔑 CREDENTIALS (Cloud Already Has)

```
API_KEY: ak_5MbHYIv9pnaipo1HpJMc (Composio)
DIALPAD: Connected via Composio
WHATSAPP: Connected (Hermes integrations)
TEST_PHONE: 9548600537
```

---

## 📊 DELIVERABLES

1. **Landing Pages** - 2,907 personalized HTML files at askivan.co
2. **SMS Log** - sms-log-TIMESTAMP.json (all sends + responses)
3. **Manifest** - manifest.json (tracking + lead status)
4. **Reports** - Delivery success rate, engagement metrics

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Kai reviews architecture
- [ ] Kai verifies Cloud integrations
- [ ] Kai sends test SMS (yours)
- [ ] Kai sends test WhatsApp (yours)
- [ ] Kai confirms both received ✅
- [ ] Kai deploys landing pages (5 leads)
- [ ] Kai sends batch (5 leads)
- [ ] Kai monitors logs
- [ ] Scale to 100, then 2,907

---

## ⚠️ NOTES

- **Dialpad API Key**: Already configured in Hermes Cloud (ak_5MbHYIv9pnaipo1HpJMc)
- **Do-Not-Call**: Script respects "Nao Ligar" flag - skips those leads
- **Opt-Outs**: Track in manifest.json for compliance
- **Landing Page**: Already created for test (edson-david-lower-payment.html)
- **Scaling**: Start 5 → 10 → 50 → 100 → 2,907

---

## 📞 TEST CONTACT

Send test messages to: **9548600537**

Expected:
1. SMS arrives from Dialpad
2. WhatsApp arrives from Hermes Cloud
3. Both with "from Kai/Ivan's Agent" signature

---

**Ready for Kai to execute! 🚀**
