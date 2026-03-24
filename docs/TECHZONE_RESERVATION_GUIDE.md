# IBM TECHZONE - RESERVATION GUIDE

**Priority**: Reserve these TODAY to avoid delays  
**Access**: [techzone.ibm.com](https://techzone.ibm.com)

---

## 🎯 CRITICAL: Reserve These 3 Environments

You need **3 IBM TechZone environments** for this project. Here's what to reserve and in what order:

---

## 1️⃣ WATSON IoT PLATFORM (HIGHEST PRIORITY)

**Why**: Needed for Day 2 (sensor simulator)
**Search Term**: Search for "Watson" then look for IoT-related options
**IMPORTANT**: Watson IoT Platform is NOT in your search results. This is a problem.
**Provisioning Time**: ~2-4 hours

### ⚠️ ALTERNATIVE APPROACH - Watson IoT Not Available

Since Watson IoT Platform doesn't appear in TechZone, we have 2 options:

**Option A: Use IBM Cloud Free Tier (RECOMMENDED)**
1. Go to [cloud.ibm.com](https://cloud.ibm.com)
2. Create free account (no credit card needed for lite tier)
3. Create Watson IoT Platform service (Lite plan - free)
4. This gives you MQTT broker for sensor data

**Option B: Use Local MQTT Broker**
1. We'll use Eclipse Mosquitto (open source MQTT broker)
2. Already included in our docker-compose.yml
3. Works for demo, but less impressive than IBM Cloud

**For now, let's proceed with Option B (local MQTT) and upgrade to IBM Cloud later if needed.**

### Reservation Details:
```
Name: Watson IoT Platform
Purpose: Technical Education
Purpose Description: 
  "OT Digital Twin PoC - i3 Technologies CEID 7sq30
   Geothermal predictive maintenance demo for GDC Kenya
   Demo date: March 30-31, 2026"

Preferred Geography: eu-de (Frankfurt)
End Date: Select maximum available (typically 30 days)
```

### After Provisioning:
1. You'll receive an email with:
   - Organization ID (e.g., `abc123`)
   - Auth Token (long string)
   - MQTT Broker URL

2. Save these to your `.env` file:
```bash
WATSON_IOT_ORG_ID=abc123
WATSON_IOT_AUTH_TOKEN=your_token_here
```

3. Test connection (we'll do this in Phase 2)

**Status**: ⚠️ RESERVE TODAY - Needed for Day 2

---

## 2️⃣ WATSONX.AI (HIGH PRIORITY)

**Why**: Needed for Day 3 (LSTM model training)
**Which One to Reserve**: **"watsonx.ai SaaS"** (first result in your list)
**Collection**: Data and AI Technology Sales Enablement
**Provisioning Time**: ~1-2 hours

### Reservation Details:
```
Environment: watsonx.ai SaaS
Collection: Data and AI Technology Sales Enablement
Purpose: Technical Education
Purpose Description:
  "LSTM neural network training for bearing failure prediction
   OT Digital Twin project - i3 Technologies CEID 7sq30
   Demo: March 30-31, 2026"

Preferred Geography: eu-de (Frankfurt)
End Date: Select maximum available
```

### After Provisioning:
1. Access Watson Studio
2. Create new project: "OTDT-Failure-Prediction"
3. Get API credentials:
   - Click profile icon → API Keys
   - Generate new API key
   - Copy Project ID from project settings

4. Save to `.env`:
```bash
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://eu-de.ml.cloud.ibm.com
```

**Status**: ⚠️ RESERVE TODAY - Needed for Day 3

---

## 3️⃣ IBM MAXIMO MAS 9.1 (MEDIUM PRIORITY)

**Why**: Needed for Day 4 (work order creation)  
**Search Term**: "Maximo Application Suite 9.1" or "MAS 9.1"  
**Provisioning Time**: ~4-8 hours (can take longer)

### Reservation Details:
```
Environment: MAS 9.1 SNO- Maximo IT- Environment with Demo Data - Education purpose Only
Collection: IBM Asset Lifecycle Management - Maximo IT - Maximo Application Suite
Purpose: Technical Education
Purpose Description:
  "Work order management integration for OT Digital Twin
   Automated maintenance scheduling for GDC Kenya geothermal plant
   i3 Technologies CEID 7sq30 - Demo: March 30-31, 2026"

Preferred Geography: us-east, jp-tok, or any available
End Date: Maximum available
```

### After Provisioning:
1. You'll receive:
   - Maximo URL (e.g., `https://your-instance.maximo.com`)
   - Username (typically `maxadmin`)
   - Password

2. Login and configure:
   - Create asset: GDC-TURBINE-01
   - Set site: GDCKENYA
   - Generate API key (Admin → Integration → API Keys)

3. Save to `.env`:
```bash
MAXIMO_BASE_URL=https://your-instance.maximo.com
MAXIMO_USERNAME=maxadmin
MAXIMO_PASSWORD=your_password
MAXIMO_API_KEY=your_api_key
MAXIMO_SITE_ID=GDCKENYA
```

**Status**: ⚠️ RESERVE TODAY - Needed for Day 4

---

## ❌ NOT NEEDED FOR LOCAL DEVELOPMENT

### Red Hat OpenShift 4.14
**Why skip for now**: Only needed for production deployment (Day 7)  
**When to reserve**: Day 6 or 7  
**Note**: You can build and test everything locally without OpenShift

If you want to reserve it anyway:
```
Search: "Red Hat OpenShift 4.14"
Purpose: Technical Education
Description: "Microservices deployment for OT Digital Twin"
Geography: eu-de
Duration: 6 weeks
```

---

## 📋 RESERVATION CHECKLIST

Use this to track your progress:

- [ ] **Watson IoT Platform** - CRITICAL for Day 2
  - [ ] Reserved on TechZone
  - [ ] Received credentials email
  - [ ] Added to `.env` file
  - [ ] Tested connection (Phase 2)

- [ ] **watsonx.ai Sandbox** - CRITICAL for Day 3
  - [ ] Reserved on TechZone
  - [ ] Accessed Watson Studio
  - [ ] Created project
  - [ ] Generated API key
  - [ ] Added to `.env` file

- [ ] **Maximo MAS 9.1** - NEEDED for Day 4
  - [ ] Reserved on TechZone
  - [ ] Received credentials
  - [ ] Logged in successfully
  - [ ] Created test asset
  - [ ] Generated API key
  - [ ] Added to `.env` file

- [ ] **OpenShift 4.14** - OPTIONAL (Day 7)
  - [ ] Reserved (if needed)
  - [ ] Downloaded `oc` CLI
  - [ ] Logged in
  - [ ] Created namespace

---

## 🚨 IMPORTANT NOTES

### Timing
- **Reserve all 3 TODAY** to avoid delays
- Provisioning can take 2-8 hours
- Some environments may be unavailable (high demand)
- If unavailable, try different geography (us-south, us-east)

### Credentials Security
- **NEVER commit credentials to Git**
- Store in `.env` file (already in `.gitignore`)
- Use password manager for backup
- Share credentials securely with team (encrypted)

### Troubleshooting
- **Environment not available**: Try different region or wait 24 hours
- **Provisioning failed**: Contact TechZone support (support@techzone.ibm.com)
- **Credentials not working**: Check email spam folder, regenerate if needed

---

## 🎯 QUICK START GUIDE

### Step 1: Access TechZone
```
1. Go to https://techzone.ibm.com
2. Sign in with IBM ID
3. Click "Environments" in top menu
```

### Step 2: Search and Reserve
```
1. Use search bar (top right)
2. Type exact search term (e.g., "Watson IoT Platform")
3. Click on matching result
4. Click "Reserve" button
5. Fill in form with details above
6. Submit reservation
```

### Step 3: Wait for Provisioning
```
1. Check email for provisioning updates
2. Typical wait: 2-8 hours
3. You'll receive credentials when ready
```

### Step 4: Save Credentials
```
1. Copy credentials from email
2. Open your .env file
3. Paste credentials in correct format
4. Save file
5. NEVER commit .env to Git!
```

---

## 💡 PRO TIPS

1. **Reserve in parallel**: Don't wait for one to finish before reserving the next
2. **Use same geography**: eu-de (Frankfurt) for all - reduces latency
3. **Maximum duration**: Always select maximum available duration
4. **Purpose description**: Be specific - helps with approval
5. **Backup plan**: If TechZone is down, we can use mock data for local development

---

## 🆘 NEED HELP?

If you encounter issues:
1. Check TechZone status page
2. Contact TechZone support: support@techzone.ibm.com
3. Ask in IBM internal Slack channels
4. Come back to me - we can adjust the plan if needed

---

## ✅ WHAT TO DO AFTER RESERVING

1. **Don't wait for provisioning** - Continue with Phase 1 local setup
2. **Check email periodically** for provisioning updates
3. **Save credentials immediately** when you receive them
4. **Test connections** when we reach that phase

You can build and test most of the system locally while waiting for TechZone environments!

---

**Ready to reserve? Go to [techzone.ibm.com](https://techzone.ibm.com) and start with Watson IoT Platform!**