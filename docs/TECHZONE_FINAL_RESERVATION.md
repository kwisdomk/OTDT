# IBM TECHZONE - FINAL RESERVATION GUIDE

**Based on Master Plan + TechZone Search Results**

---

## 🎯 THE ONE RESERVATION YOU NEED

According to your Master Plan, you need **ONE primary reservation** that includes everything:

### **OpenShift 4.14 Cluster + IBM Cloud Pak for Data Demo**

**TechZone ID**: `656e156942c8d2001855e768`

**What it includes**:
- 3-node OpenShift worker cluster
- Helm (for Kubernetes deployments)
- Kafka (for sensor data streaming)
- Databases (TimescaleDB, Redis)
- **watsonx.ai Studio** (for Asenath's LSTM model)
- **watsonx.data** (for Philip's data lakehouse)
- **Maximo MAS 9.1** (for work order management)

**This is your "all-in-one" environment for the entire OTDT project.**

---

## 📋 HOW TO FIND AND RESERVE IT

### Step 1: Search TechZone
```
1. Go to https://techzone.ibm.com
2. In search bar, try these searches:
   - "OpenShift 4.14 Cluster IBM Cloud Pak for Data"
   - "Cloud Pak for Data Demo"
   - "656e156942c8d2001855e768" (exact TechZone ID)
```

### Step 2: Look for This Environment
**Characteristics to identify it**:
- Name contains: "OpenShift 4.14" AND "Cloud Pak for Data"
- Infrastructure: OCP-V (OpenShift Container Platform - Virtual)
- Includes: CP4D (Cloud Pak for Data)
- Region options: Multiple (us-east, eu-de, etc.)

### Step 3: Reserve It
```
Purpose: Technical Education

Purpose Description:
"OT Digital Twin - Industrial Predictive Maintenance System
 8-solution architecture for GDC Kenya geothermal plant
 i3 Technologies CEID 7sq30
 Workshop: March 30-31, 2026 @ IBM Research Lab Africa
 Requires: watsonx.ai Studio, watsonx.data, Maximo MAS 9.1
 7-Layer IEEE ZAHIRA IoT Architecture implementation"

Preferred Geography: eu-de (Frankfurt) or us-east

Duration: 6 weeks (covers workshop + post-event follow-ups)
```

---

## 🔍 IF YOU CAN'T FIND IT

If the exact environment isn't in your search results, here's the **fallback approach**:

### Plan A: Search for "Cloud Pak for Data"
Look for any environment that includes:
- OpenShift 4.14+
- Cloud Pak for Data (CP4D)
- Multiple services bundled

### Plan B: Reserve Individual Components
If the all-in-one isn't available, reserve these separately:

1. **Red Hat OpenShift 4.14**
   - Search: "Red Hat OpenShift 4.14"
   - This is your base cluster

2. **watsonx.ai SaaS** (you found this one)
   - For LSTM model training
   - Collection: Data and AI Technology Sales Enablement

3. **MAS 9.1 SNO- Maximo IT** (you found this one)
   - For work order management
   - Collection: IBM Asset Lifecycle Management

4. **watsonx.data** (search for it)
   - For data lakehouse
   - Philip's component

---

## 🎯 RECOMMENDED ACTION RIGHT NOW

### Option 1: Try to Find the All-in-One (BEST)
```bash
# Search TechZone for:
1. "Cloud Pak for Data 5.1" or "CP4D 5.1"
2. "OpenShift 4.14 Cloud Pak"
3. Look for environments with "Demo" in the name
4. Check if it includes watsonx services
```

### Option 2: Reserve What You Found (GOOD ENOUGH)
If you can't find the all-in-one, reserve these 3:

1. ✅ **watsonx.ai SaaS** (you already found this)
2. ✅ **MAS 9.1 SNO- Maximo IT** (you already found this)
3. 🔍 **Search for "watsonx.data"** and reserve it
4. 🔍 **Search for "Red Hat OpenShift 4.14"** and reserve it

---

## 📊 COMPARISON: ALL-IN-ONE vs INDIVIDUAL

### All-in-One Approach (Preferred)
**Pros**:
- ✅ Everything pre-integrated
- ✅ Single reservation to manage
- ✅ Guaranteed compatibility
- ✅ Faster setup

**Cons**:
- ❌ May not be available
- ❌ Longer provisioning time (8-12 hours)
- ❌ Higher resource usage

### Individual Components (Fallback)
**Pros**:
- ✅ More availability
- ✅ Faster individual provisioning
- ✅ Can start with what's available

**Cons**:
- ❌ More reservations to manage
- ❌ Integration work required
- ❌ Potential compatibility issues

---

## 🚀 IMMEDIATE ACTION PLAN

### Today (Right Now):

**Step 1**: Search for the all-in-one environment
```
Search terms:
- "Cloud Pak for Data 5.1"
- "OpenShift 4.14 CP4D"
- "656e156942c8d2001855e768"
```

**Step 2**: If found → Reserve it immediately (6 weeks duration)

**Step 3**: If NOT found → Reserve these 3 individually:
- [ ] watsonx.ai SaaS (you found it)
- [ ] MAS 9.1 SNO- Maximo IT (you found it)
- [ ] Search and reserve "watsonx.data"

**Step 4**: Continue with Phase 1 local setup while waiting for provisioning

---

## 💡 IMPORTANT NOTES

### About Watson IoT
Your Master Plan mentions Watson IoT, but:
- It's NOT in TechZone search results
- We can use **local MQTT broker** (Eclipse Mosquitto) instead
- This is actually simpler and works perfectly for demo
- No dependency on IBM Cloud availability

### About watsonx.data
Your Master Plan says Philip needs this for "Data Lakehouse":
- Search TechZone for "watsonx.data"
- Should appear in search results
- Reserve it if you're doing individual components
- If using all-in-one, it should be included

### About Local Development
**Good news**: You can build and test 80% of the system locally while waiting for TechZone:
- Docker Compose provides: Kafka, TimescaleDB, Redis
- Python/FastAPI runs locally
- React dashboard runs locally
- Unity runs locally
- Only need IBM Cloud for: watsonx.ai training, Maximo integration

---

## ❓ DECISION TIME

**Tell me which path you want to take:**

### Path A: "I'll search for the all-in-one environment"
→ I'll wait while you search and tell me if you find it

### Path B: "I can't find the all-in-one, let's use individual components"
→ I'll guide you to reserve the 3 individual environments you found

### Path C: "Let's start with local development first"
→ I'll guide you through Phase 1 local setup while TechZone provisions

**Which path do you want to take?**