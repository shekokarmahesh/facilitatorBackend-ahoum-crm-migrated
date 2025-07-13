# 📱 WhatsApp Integration Setup Guide

## 🎯 Overview

This guide will help you set up WhatsApp integration in your facilitatorBackend using the WasenderAPI. You'll be able to:

- ✅ Create and manage courses
- ✅ Send course details via WhatsApp to students
- ✅ Send bulk messages to all students
- ✅ Test WhatsApp connectivity

## 🚀 Step 1: Environment Configuration

Create a `.env` file in the `facilitatorBackend` directory with the following content:

```env
# Database Configuration
POSTGRES_URL=postgres://postgres:FBDzSdCB7f1BRS4QoqBURgA7POdcKhUBg7GIA016Rxyp8nAFUmqmUCaSFcsRA2QK@82.29.162.1:5438/postgres

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production

# WhatsApp Configuration (WasenderAPI)
WASENDER_API_KEY=c254174f0fa60983e14d43c6ecdbe6ae054865c858a15ecc408c25456b822c23
WASENDER_PHONE_NUMBER=+917777055014
WASENDER_SESSION_NAME=Ahoum

# Application Settings
FLASK_ENV=development
DEBUG=True
```

## 🔧 Step 2: Install Dependencies

The required dependencies have been added to `pyproject.toml`. Install them:

```bash
cd facilitatorBackend
pip install wasenderapi
# or if using uv:
# uv pip install wasenderapi
```

## 🗄️ Step 3: Database Setup

Run the setup script to create the courses table:

```bash
python setup_unified_system.py
```

This will:
- Create the `courses` table in your database
- Set up proper indexes
- Run necessary migrations

## 🏃‍♂️ Step 4: Start the Backend

```bash
python main.py
```

The server will start on `http://localhost:5000` with these new endpoints:

## 📋 API Endpoints

### Course Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/courses/` | Get all courses |
| `POST` | `/api/courses/` | Create a new course |
| `GET` | `/api/courses/{id}` | Get specific course |
| `PUT` | `/api/courses/{id}` | Update course |
| `DELETE` | `/api/courses/{id}` | Delete course |

### WhatsApp Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/courses/{id}/send-whatsapp` | Send course to selected numbers |
| `POST` | `/api/courses/{id}/send-to-all-students` | Send course to all students |
| `POST` | `/api/courses/test-whatsapp` | Test WhatsApp service |
| `GET` | `/api/courses/whatsapp-status` | Check WhatsApp status |

## 🧪 Step 5: Test the Integration

### 5.1 Test WhatsApp Connection

```bash
curl -X GET "http://localhost:5000/api/courses/whatsapp-status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5.2 Test WhatsApp Message

```bash
curl -X POST "http://localhost:5000/api/courses/test-whatsapp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone_number": "+917777055014"
  }'
```

### 5.3 Create a Course

```bash
curl -X POST "http://localhost:5000/api/courses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Yoga for Beginners",
    "timing": "Monday & Wednesday 6:00 PM - 7:00 PM",
    "prerequisite": "No prior experience needed",
    "description": "A gentle introduction to yoga focusing on basic poses, breathing techniques, and relaxation. Perfect for complete beginners looking to start their wellness journey."
  }'
```

### 5.4 Send Course via WhatsApp

```bash
curl -X POST "http://localhost:5000/api/courses/1/send-whatsapp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone_numbers": ["+919876543210", "+919123456789"]
  }'
```

## 📱 WhatsApp Message Format

When you send a course via WhatsApp, students will receive a beautifully formatted message:

```
🎯 *Yoga for Beginners*

📅 *Timing:* Monday & Wednesday 6:00 PM - 7:00 PM

📋 *Prerequisites:* No prior experience needed

📝 *Description:*
A gentle introduction to yoga focusing on basic poses, breathing techniques, and relaxation. Perfect for complete beginners looking to start their wellness journey.

---
✨ *Ahoum - Your Wellness Journey*

For more information or to register, please reply to this message or contact us directly.

Thank you! 🙏
```

## 🔍 Troubleshooting

### Common Issues

1. **WhatsApp Service Not Available**
   - Check your `.env` file has the correct `WASENDER_API_KEY`
   - Verify your WasenderAPI session is active
   - Check the logs for initialization errors

2. **Phone Number Format Issues**
   - Ensure phone numbers include country code: `+917777055014`
   - Indian numbers should start with `+91`
   - The service automatically cleans and formats numbers

3. **Database Connection Issues**
   - Verify your `POSTGRES_URL` is correct
   - Run `python test_db_connection.py` to test database connectivity
   - Check if the `courses` table exists

### Debug Commands

```bash
# Check database connection
python test_db_connection.py

# Check WhatsApp service logs
tail -f logs/whatsapp_service.log

# Test course creation directly
python -c "
from models.database import DatabaseManager, CourseRepository
db = DatabaseManager()
repo = CourseRepository(db)
course_id = repo.create_course(1, {
    'title': 'Test Course',
    'timing': 'Test Time',
    'description': 'Test Description'
})
print(f'Created course: {course_id}')
"
```

## 🎯 Features Implemented

### ✅ Course Management
- **CRUD operations** for courses
- **Input validation** for required fields
- **Soft deletion** with `is_active` flag
- **Ownership verification** (users can only manage their courses)

### ✅ WhatsApp Integration
- **WasenderAPI SDK** integration with [wasenderapi](https://pypi.org/project/wasenderapi/)
- **Phone number cleaning** and formatting
- **Bulk messaging** to multiple recipients
- **Message formatting** with emojis and structure
- **Error handling** and logging
- **Connection testing** capabilities

### ✅ Security & Validation
- **JWT authentication** required for all endpoints
- **Input sanitization** and validation
- **Ownership checks** on all operations
- **CORS configuration** for frontend integration

## 🔄 Next Steps

1. **Frontend Integration**: Create React components to manage courses and send WhatsApp messages
2. **Message Templates**: Add support for custom message templates
3. **Scheduling**: Implement scheduled WhatsApp campaigns
4. **Analytics**: Track message delivery and engagement
5. **Rich Media**: Add support for images, documents, and other media types

## 📞 Support

If you encounter any issues:

1. Check the console logs for error messages
2. Verify your WasenderAPI session is active at [https://wasenderapi.com/](https://wasenderapi.com/)
3. Test with your own phone number first
4. Check the [WasenderAPI documentation](https://wasenderapi.com/api-docs) for API limits

## 🎉 Success!

Your WhatsApp integration is now ready! You can:

- ✅ Create courses with details
- ✅ Send beautiful WhatsApp messages to students
- ✅ Manage bulk communications
- ✅ Test the integration easily

Happy messaging! 🚀📱 