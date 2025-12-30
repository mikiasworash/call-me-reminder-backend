# Call Me Reminder - Backend

FastAPI backend for the Call Me Reminder application. Handles reminder CRUD operations, scheduling, and Vapi integration for automated voice calls.

## Features

- ✅ RESTful API for reminder management
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Background scheduler for processing due reminders
- ✅ Vapi integration for automated voice calls
- ✅ Phone number validation
- ✅ Date/time validation
- ✅ CORS support for frontend integration

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (with SQLAlchemy)
- **Scheduler:** APScheduler
- **Validation:** Pydantic
- **Phone Validation:** phonenumbers
- **HTTP Client:** httpx

## Getting Started

### Prerequisites

- Python 3.11+
- pip or poetry

### Installation

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:

```bash
cp .env.example .env
```

4. Update `.env` with your configuration:

```env
VAPI_API_KEY=your_vapi_api_key
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id_uuid
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Reminders

- `POST /api/v1/reminders` - Create a new reminder
- `GET /api/v1/reminders` - List reminders (with filters)
- `GET /api/v1/reminders/{id}` - Get a single reminder
- `PATCH /api/v1/reminders/{id}` - Update a reminder
- `DELETE /api/v1/reminders/{id}` - Delete a reminder

### Health

- `GET /api/v1/health` - Health check

## Request/Response Examples

### Create Reminder

```bash
POST /api/v1/reminders
Content-Type: application/json

{
  "title": "Doctor Appointment",
  "message": "Don't forget your doctor appointment at 3 PM",
  "phone_number": "+14155552671",
  "scheduled_at": "2024-01-15T15:00:00Z",
  "timezone": "America/New_York"
}
```

### List Reminders

```bash
GET /api/v1/reminders?status=scheduled&search=doctor&sort=asc
```

## Scheduler

The scheduler runs in the background and checks for due reminders every minute. When a reminder's `scheduled_at` time is reached:

1. The system creates a Vapi call
2. The call delivers the reminder message
3. The reminder status is updated to "completed" or "failed"

## Database Schema

### Reminders Table

- `id` - Primary key
- `title` - Reminder title (max 255 chars)
- `message` - Reminder message (max 1000 chars)
- `phone_number` - Phone number in E.164 format
- `scheduled_at` - Scheduled date/time (UTC)
- `timezone` - Timezone string
- `status` - Status: scheduled, completed, failed
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `completed_at` - Completion timestamp (nullable)
- `failure_reason` - Failure reason (nullable)
- `vapi_call_id` - Vapi call ID (nullable)

## Environment Variables

| Variable               | Description                | Required | Default                    |
| ---------------------- | -------------------------- | -------- | -------------------------- |
| `DATABASE_URL`         | Database connection string | No       | `sqlite:///./reminders.db` |
| `VAPI_API_KEY`         | Vapi API key               | Yes      | -                          |
| `VAPI_PHONE_NUMBER_ID` | Vapi phone number ID       | Yes      | -                          |
| `HOST`                 | Server host                | No       | `0.0.0.0`                  |
| `PORT`                 | Server port                | No       | `8000`                     |
| `CORS_ORIGINS`         | Allowed CORS origins       | No       | `http://localhost:3000`    |

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration settings
├── database.py             # Database setup
├── models/                 # SQLAlchemy models
│   └── reminder.py
├── schemas/                # Pydantic schemas
│   └── reminder.py
├── services/               # Business logic
│   ├── reminder_service.py
│   └── vapi_service.py
├── api/                    # API routes
│   └── routes/
│       ├── reminders.py
│       └── health.py
├── scheduler/              # Background scheduler
│   └── reminder_scheduler.py
└── utils/                  # Utility functions
    └── phone_validator.py
```

## Testing

### Quick Test Flow

1. Start the server
2. Create a reminder for 2-3 minutes in the future using the API
3. Wait for the scheduled time
4. Check the reminder status (should be "completed" or "failed")
5. Verify the Vapi call was made

### Using curl

```bash
# Create a reminder
curl -X POST "http://localhost:8000/api/v1/reminders" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Reminder",
    "message": "This is a test reminder",
    "phone_number": "+14155552671",
    "scheduled_at": "2024-01-15T15:00:00Z",
    "timezone": "America/New_York"
  }'

# List reminders
curl "http://localhost:8000/api/v1/reminders"

# Get a reminder
curl "http://localhost:8000/api/v1/reminders/1"
```

## Notes

- All dates are stored in UTC
- The scheduler checks for due reminders every minute
- Phone numbers must be in E.164 format (e.g., +14155552671)
- Scheduled time must be in the future
- Vapi API configuration is required for calls to work

## Troubleshooting

### Scheduler not running

- Check logs for errors
- Verify database connection
- Ensure Vapi credentials are set

### Calls not being made

- Verify Vapi API key and phone number ID
- Check Vapi service logs
- Ensure reminder is in "scheduled" status

### Database errors

- Check database file permissions
- Verify DATABASE_URL in .env
- Try deleting reminders.db to recreate
