# Google Ads PPC Analysis Tool

A comprehensive competitive analysis tool for Google Ads PPC campaigns with AI-powered insights and **LIVE data collection via SerpAPI**.

## ✨ Now with LIVE Data Collection!

This tool is **fully integrated with SerpAPI** to automatically collect real Google Ads data:
- ✅ **Automated hourly checks** for your keywords
- ✅ **Real Google Ads** including headlines, descriptions, extensions
- ✅ **Shopping ads** support
- ✅ **Multiple locations & devices**
- ✅ **Already configured** - just add your keywords!

## Features

- 🔍 **Live Ad Collection** - Real Google Ads data via SerpAPI integration
- 📊 **Historical Tracking** - Never lose data, track changes over time
- ⏰ **Automated Monitoring** - Hourly scheduled checks for keywords
- 🤖 **AI Analysis** - Pattern detection and actionable insights powered by Claude
- 💬 **Interactive Chat** - Ask questions about your data with AI assistant
- 📈 **Visualization** - Charts and trends
- 🎯 **Competitor Tracking** - Monitor competitor ad strategies

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

1. **Clone the repository**

2. **Configure your API keys**

   The `.env` file is already configured with your SerpAPI key!
   ```bash
   # .env file (already set up)
   SERPAPI_KEY=28f9888fa54352b9166b35d38dc7cc56d15106ca9b02d9439452d92c597ba6c4
   ANTHROPIC_API_KEY=your_anthropic_key_here  # Add your Claude API key
   ```

3. **Test your SerpAPI connection** (optional but recommended)
   ```bash
   cd backend
   python scripts/test_serpapi.py
   ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Access the web interface**
   ```
   http://localhost:3000
   ```

6. **Add keywords to monitor**
   - Go to Keywords page
   - Click "Add Keyword"
   - Enter keyword, location, device
   - Ads will be collected automatically every hour!

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

## SerpAPI Integration

This tool uses **SerpAPI** to collect real Google Ads data. Your API key is already configured!

### What Gets Collected

Every hour, for each keyword you add:
- Ad headlines (all variations)
- Ad descriptions
- Display URLs and landing pages
- Ad extensions (sitelinks, callouts, etc.)
- Advertiser information
- Ad position and placement
- Shopping ads
- Complete raw data for analysis

### Usage Guide

**See [SERPAPI_SETUP.md](SERPAPI_SETUP.md) for complete documentation**, including:
- How to test your connection
- Location and device options
- SerpAPI pricing and limits
- Troubleshooting tips
- Advanced configuration

### Quick Example

```python
# Keywords added in the UI are automatically monitored
# Example: "running shoes" in "United States" on "desktop"
# System checks hourly and saves all ads to database
```

### Cost Management

- **Free Tier**: 100 searches/month (~3-5 keywords checked hourly)
- **Starter ($50/mo)**: 5,000 searches (~175 keywords)
- **Pro ($150/mo)**: 30,000 searches (~1,000 keywords)

Tips: Use longer intervals (3-6 hours) to monitor more keywords with fewer searches.

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

# SerpAPI (already configured!)
SERPAPI_KEY=your_serpapi_key

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
