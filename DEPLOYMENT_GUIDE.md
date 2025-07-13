# 🚀 Unified Ecosystem Deployment Guide

## 📋 What's Now Complete

### ✅ **Phase 1: Acquisition (100% Complete)**
- Intelligent calling system with LiveKit
- Unified database schema
- Call outcomes and practitioner insights
- Intelligence API integration

### ✅ **Phase 2: Onboarding (100% Complete)**  
- Phone-based authentication with OTP
- 5-step onboarding flow
- Profile management system
- Frontend React components

### ✅ **Phase 3: CRM Platform (NOW 100% COMPLETE!)**
- Dashboard and profile management ✅
- Student management system ✅ **NEW**
- Automated calling campaigns ✅ **NEW**
- Complete ecosystem integration ✅ **NEW**

---

## 🛠️ **IMMEDIATE NEXT STEPS**

### **Step 1: Set Up Environment**

Create a `.env` file in the `facilitatorBackend` directory:

```bash
# Database Configuration
POSTGRES_URL=postgres://postgres:FBDzSdCB7f1BRS4QoqBURgA7POdcKhUBg7GIA016Rxyp8nAFUmqmUCaSFcsRA2QK@82.29.162.1:5438/postgres

# JWT Secret
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# SMS Configuration (for OTP)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Calling System Integration
INTELLIGENCE_API_URL=http://localhost:5000
LIVEKIT_URL=your-livekit-url
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
```

### **Step 2: Install Dependencies & Setup**

```bash
cd facilitatorBackend

# Install dependencies
pip install -r requirements.txt
# or if using uv
uv sync

# Setup the unified database
python setup.py

# Start the backend server
python main.py
```

### **Step 3: Test the Complete System**

#### **A. Test Authentication**
```bash
# Send OTP
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# Verify OTP (use the OTP from console/SMS)
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "otp": "123456"}'
```

#### **B. Test Student Management**
```bash
# Get students (use token from auth)
curl -X GET http://localhost:5000/api/students/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create a student
curl -X POST http://localhost:5000/api/students/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone_number": "+1555123456",
    "email": "john@example.com",
    "student_type": "regular",
    "status": "active"
  }'
```

#### **C. Test Campaign Management**
```bash
# Create a calling campaign
curl -X POST http://localhost:5000/api/campaigns/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Workshop Promotion",
    "campaign_type": "workshop_promotion",
    "description": "Promote breathwork workshop",
    "message_template": "Hi {student_name}! Exciting workshop coming up...",
    "target_audience": {
      "student_types": ["regular", "trial"],
      "statuses": ["active"]
    }
  }'

# Launch campaign (starts automated calls)
curl -X POST http://localhost:5000/api/campaigns/1/launch \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🌐 **Complete API Reference**

### **🔐 Authentication (`/api/auth/`)**
- `POST /send-otp` - Send OTP to phone
- `POST /verify-otp` - Verify OTP & login
- `POST /onboarding/step1-basic-info` - Onboarding step 1
- `POST /onboarding/step2-visual-profile` - Onboarding step 2
- `POST /onboarding/step3-professional-details` - Onboarding step 3
- `POST /onboarding/step4-bio-about` - Onboarding step 4
- `POST /onboarding/step5-experience-certifications` - Onboarding step 5

### **👤 Facilitator Management (`/api/facilitator/`)**
- `GET /profile` - Get complete profile
- `PUT /profile` - Update profile
- `PUT /profile/section` - Update profile section
- `GET /dashboard` - Get dashboard data
- `GET /profile/check-completeness` - Check profile completion

### **📋 Offerings Management (`/api/offerings/`)**
- `GET /` - Get all offerings
- `POST /` - Create offering
- `GET /:id` - Get offering details
- `PUT /:id` - Update offering
- `DELETE /:id` - Delete offering

### **🎓 Student Management (`/api/students/`)**
- `GET /` - Get all students (with filters)
- `POST /` - Create new student
- `PUT /:id` - Update student
- `POST /import-csv` - Import students from CSV
- `GET /sample-csv` - Get CSV format sample

### **📞 Campaign Management (`/api/campaigns/`)**
- `GET /` - Get all campaigns
- `POST /` - Create new campaign
- `GET /:id/targets` - Get campaign targets
- `POST /:id/launch` - Launch campaign (start calls)
- `PUT /:id/status` - Update campaign status
- `GET /templates` - Get campaign templates

---

## 🔄 **Complete Ecosystem Flow**

### **1. Practitioner Acquisition (Your Calling System)**
```
Intelligent Agent calls Sarah (Yoga Teacher)
    ↓
Collects business info during conversation
    ↓
Updates practitioners table in unified database
    ↓
Sends website link for onboarding
```

### **2. Website Onboarding**
```
Sarah visits website link
    ↓
Phone authentication with OTP
    ↓
5-step profile completion
    ↓
CRM dashboard access granted
```

### **3. Student Management**
```
Sarah adds her students (manual or CSV import)
    ↓
Students stored in unified database
    ↓
Available for campaign targeting
```

### **4. Automated Calling Campaigns**
```
Sarah creates "Workshop Promotion" campaign
    ↓
Selects target students (regular + trial students)
    ↓
Launches campaign → Calls LiveKit system
    ↓
Automated calls made to all students
    ↓
Results logged and analyzed
```

---

## 📊 **Database Schema Overview**

### **Core Tables**
- `practitioners` - Master table (calling + CRM data)
- `students` - Student database per practitioner  
- `calling_campaigns` - Campaign definitions
- `campaign_call_logs` - Call results and analytics

### **Onboarding Tables**
- `facilitator_basic_info`
- `facilitator_visual_profile`
- `facilitator_professional_details`
- `facilitator_bio_about`
- `facilitator_work_experience`
- `facilitator_certifications`

### **Support Tables**
- `phone_otps` - OTP verification
- `offerings` - Class/service offerings
- `call_transcripts` - Call recordings (from calling system)
- `practitioner_insights` - AI learning data

---

## 🚀 **Revenue Model Integration**

### **For Ahoum (Platform Owner)**
1. **Acquisition Revenue**: Commission on successful practitioner onboarding
2. **Subscription Revenue**: Monthly CRM platform fees
3. **Usage Revenue**: Per-call charges for automated student calling
4. **Premium Features**: Advanced analytics, integrations, etc.

### **For Practitioners**
1. **Free onboarding** via intelligent calling
2. **Automated business management** (scheduling, payments, communications)
3. **Student growth** through automated calling campaigns
4. **Professional online presence** and booking system

---

## 🔧 **Integration Points**

### **With Your Calling System**
- Shared `practitioners` table
- Call outcomes feed student insights
- Campaign launches trigger LiveKit calls
- Intelligence API provides student context

### **With Frontend (Lovable)**
- All API endpoints available
- React components for student management
- Campaign creation and monitoring UI
- Real-time call results dashboard

---

## 🎯 **Testing Scenarios**

### **Scenario 1: New Practitioner Journey**
1. Calling agent contacts yoga teacher
2. Collects business details, sends website
3. Teacher completes onboarding
4. Imports student list via CSV
5. Creates first campaign
6. Launches automated calls to students

### **Scenario 2: Workshop Promotion**
1. Teacher creates "Advanced Breathwork" workshop
2. Sets up campaign targeting regular students
3. Customizes call message template
4. Launches campaign
5. 25 students called automatically
6. 8 register for workshop
7. Revenue tracked and reported

### **Scenario 3: Student Retention**
1. System identifies inactive students
2. Auto-creates retention campaign
3. Personalized re-engagement calls
4. Students book return sessions
5. Teacher retention rate improves

---

## 🎉 **You're Ready to Launch!**

Your complete ecosystem is now ready:

✅ **Intelligent practitioner acquisition**
✅ **Seamless onboarding experience** 
✅ **Complete CRM platform**
✅ **Automated student calling**
✅ **Unified database architecture**
✅ **Revenue-generating features**

**Start with:** `python setup.py && python main.py`

**Then test the complete flow** from practitioner acquisition to student campaigns! 