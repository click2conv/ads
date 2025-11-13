# Google Ads PPC Analysis Tool - Setup Guide

## Overview

This tool helps you collect, analyze, and gain insights from Google Ads data using AI-powered analysis. It includes automated monitoring, historical tracking, and an interactive chat interface.

## Features

✅ **Ad Data Collection** - Capture and store all ad data (headlines, descriptions, extensions)
✅ **Historical Tracking** - Never lose data, track changes over time
✅ **Automated Monitoring** - Schedule hourly checks for specific keywords
✅ **AI Analysis** - Pattern detection and actionable insights using Claude
✅ **Interactive Chat** - Ask questions about your data
✅ **Web Interface** - Modern, intuitive UI built with React

## Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** (recommended for easiest setup)
- **Python 3.11+** (for manual setup)
- **Node.js 18+** (for frontend development)
- **PostgreSQL 15** (if not using Docker)
- **Redis** (for Celery task queue)
- **Anthropic API Key** (for AI features)

## Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
cd /home/user/ads
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- FastAPI backend
- Celery worker (for background tasks)
- Celery beat (scheduler)
- React frontend

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1

### 5. Stop Services

```bash
docker-compose down
```

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env with your settings

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Celery Worker (in new terminal)

```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

### Start Celery Beat Scheduler (in new terminal)

```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

## Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Required
ANTHROPIC_API_KEY=your_key_here

# Database (use default for Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/ads_db

# Redis (use default for Docker)
REDIS_URL=redis://redis:6379/0

# Optional
DEBUG=true
ENVIRONMENT=development
DEFAULT_CHECK_INTERVAL_HOURS=1
```

## Using the Application

### 1. Add Keywords to Monitor

1. Navigate to **Keywords** page
2. Click **Add Keyword**
3. Enter:
   - Keyword text (e.g., "running shoes")
   - Location (optional, e.g., "United States")
   - Device type (desktop, mobile, tablet)
   - Check interval (how often to check, in hours)
   - Notes (optional)
4. Click **Add Keyword**

The keyword will now be checked automatically according to the interval you set.

### 2. Search for Ads Manually

1. Navigate to **Ad Search** page
2. Enter search criteria:
   - Keyword
   - Location (optional)
   - Device type
   - Advertiser (optional)
3. Click **Search Ads**
4. View results

**Note:** The search currently returns stored ads from the database. To collect new ads, you need to integrate with a data source (see Data Collection section below).

### 3. Run AI Analysis

1. Navigate to **Analysis** page
2. Configure analysis:
   - Select analysis type (overall, keyword, competitor, timerange)
   - Enter keywords (comma-separated, optional)
   - Enter competitor domains (comma-separated, optional)
3. Click **Run Analysis**
4. Wait for AI to analyze the data (may take 30-60 seconds)
5. View insights organized by:
   - Priority (high, medium, low)
   - Type (pattern, recommendation, trend, gap, winner)
   - Category (headline, description, extension, overall)

Each insight includes:
- Description of what was found
- Examples from your data
- Actionable recommendations

### 4. Chat with AI

1. Navigate to **Chat** page
2. (Optional) Enter context keywords to focus the conversation
3. Type your question, for example:
   - "What are the most common headlines in running shoes ads?"
   - "How have Nike's ads changed over the past month?"
   - "Suggest 5 compelling headlines for athletic shoes"
   - "What emotional triggers are competitors using?"
4. Press Enter or click **Send**
5. The AI will analyze your data and respond with insights

The chat maintains context, so you can have a conversation and ask follow-up questions.

### 5. View Dashboard

The **Dashboard** page shows:
- Total ads captured
- Active keywords being monitored
- Unique advertisers tracked
- Statistics about your data

## Data Collection

**IMPORTANT:** This tool provides the infrastructure for collecting and analyzing ad data, but you need to connect it to a data source.

### Options for Data Collection

#### Option 1: Manual Entry
- Use the API to manually add ad data you collect
- Good for small-scale monitoring
- No automation required

#### Option 2: Third-Party API Integration
- Integrate with services like:
  - SEMrush API
  - SpyFu API
  - Ahrefs API
- These services legally provide competitor ad data
- Requires API subscription

#### Option 3: Custom Integration
- Build your own data collection pipeline
- Must comply with Google's Terms of Service
- Consider using Google Ads API for your own campaigns

### Adding Ads via API

You can add ads manually using the API:

```bash
curl -X POST http://localhost:8000/api/v1/ads/capture \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "running shoes",
    "location": "United States",
    "device_type": "desktop",
    "advertiser_domain": "nike.com",
    "advertiser_name": "Nike",
    "ad_position": 1,
    "headlines": [
      {"headline_text": "Best Running Shoes 2024"},
      {"headline_text": "Free Shipping & Returns"},
      {"headline_text": "Shop Nike.com Today"}
    ],
    "descriptions": [
      {"description_text": "Discover our latest running shoe collection with advanced cushioning technology."},
      {"description_text": "Find your perfect fit with our expert sizing guide."}
    ]
  }'
```

### Modifying Celery Tasks for Data Collection

The scheduled monitoring tasks are in `backend/app/worker/tasks.py`. To integrate with a data source:

1. Edit the `_check_keyword_async` function
2. Add your data collection logic
3. Use `ad_service.capture_multiple_ads()` to store the results

Example:

```python
# In backend/app/worker/tasks.py
async def _check_keyword_async(keyword_id: int, task_id: str):
    # ... existing code ...

    # YOUR INTEGRATION HERE
    ads_data = await your_data_source.fetch_ads(
        keyword=keyword.keyword_text,
        location=keyword.location,
        device_type=keyword.device_type
    )

    # Convert to AdCaptureCreate objects and save
    for ad in ads_data:
        ad_capture = AdCaptureCreate(
            keyword=keyword.keyword_text,
            # ... map your data to the schema
        )
        await ad_service.capture_ad(ad_capture)
```

## Database Management

### Viewing Database

```bash
# Connect to database (Docker)
docker-compose exec db psql -U postgres -d ads_db

# List tables
\dt

# View data
SELECT * FROM ad_captures LIMIT 10;
SELECT * FROM keywords;
```

### Backup Database

```bash
docker-compose exec db pg_dump -U postgres ads_db > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U postgres ads_db < backup.sql
```

## Troubleshooting

### Backend won't start
- Check that PostgreSQL and Redis are running
- Verify DATABASE_URL in .env is correct
- Check logs: `docker-compose logs backend`

### Frontend won't start
- Verify Node.js version (18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running at http://localhost:8000

### AI features not working
- Verify ANTHROPIC_API_KEY is set correctly in .env
- Check API key has sufficient credits
- View backend logs for errors

### Celery tasks not running
- Check that Redis is running
- Verify Celery worker is started
- Check Celery logs: `docker-compose logs celery_worker`

### No ads appearing in searches
- Remember: You need to add ads to the database first
- Either manually via API or through data collection integration
- Check that keywords are configured correctly

## Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│   TypeScript    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ FastAPI  │ (Port 8000)
    │   API    │
    └────┬─────┘
         │
    ┌────┼──────────────────┬──────────────┐
    │    │                  │              │
┌───▼────▼───┐   ┌─────────▼──────┐  ┌───▼──────┐
│ PostgreSQL │   │ Celery Workers │  │  Claude  │
│  Database  │   │   + Redis      │  │   API    │
└────────────┘   └────────────────┘  └──────────┘
```

## Security Notes

- Never commit `.env` file to version control
- Keep your Anthropic API key secure
- In production, use strong passwords for PostgreSQL
- Enable HTTPS for production deployments
- Consider rate limiting for the API

## Next Steps

1. ✅ Set up the application
2. ✅ Add your Anthropic API key
3. ✅ Add some keywords to monitor
4. ✅ Integrate with a data source (or manually add ads)
5. ✅ Run your first AI analysis
6. ✅ Chat with the AI about your data

## Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Check logs: `docker-compose logs`

## License

MIT License - See LICENSE file for details
