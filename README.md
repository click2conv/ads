# Google Ads PPC Analysis Tool

A comprehensive competitive analysis tool for Google Ads PPC campaigns with AI-powered insights.

## Features

- 🔍 **Ad Data Collection** - Capture comprehensive ad data from multiple sources
- 📊 **Historical Tracking** - Never lose data, track changes over time
- ⏰ **Automated Monitoring** - Scheduled checks for keywords
- 🤖 **AI Analysis** - Pattern detection and actionable insights
- 💬 **Interactive Chat** - Ask questions about your data
- 📈 **Visualization** - Charts and trends

## Architecture

- **Backend**: Python FastAPI + PostgreSQL
- **Frontend**: React + TypeScript
- **Scheduler**: Celery + Redis
- **AI**: Anthropic Claude API

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run with Docker Compose:

```bash
docker-compose up -d
```

4. Access the application at `http://localhost:3000`

### Manual Setup (Development)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
ads/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── main.py   # Application entry
│   └── requirements.txt
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ads_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Claude API
ANTHROPIC_API_KEY=your_api_key_here

# App Settings
SECRET_KEY=your_secret_key_here
DEBUG=true
```

## Usage

### Setting Up Keyword Monitoring

1. Navigate to "Keywords" page
2. Add keywords to monitor
3. Configure location and device filters
4. Set monitoring frequency

### Manual Ad Search

1. Go to "Search" page
2. Enter keyword and filters
3. Click "Search Now"
4. View and save results

### AI Analysis

1. Select keywords or date range
2. Click "Analyze"
3. View insights and recommendations

### Chat Interface

1. Open the chat panel
2. Ask questions about your data
3. Get AI-powered insights

## Data Collection

This tool supports multiple data sources:

- Manual entry
- API integrations (SEMrush, SpyFu, etc.)
- Custom data imports

**Note**: Direct scraping of Google Search is not supported as it violates Google's Terms of Service.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

## License

MIT License

## Support

For issues or questions, please open a GitHub issue.
