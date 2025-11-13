# SerpAPI Integration Guide

## 🎉 Your Tool Now Has LIVE Data Collection!

Your Google Ads PPC Analysis Tool is now integrated with **SerpAPI** to collect real, live Google Ads data automatically!

## What is SerpAPI?

SerpAPI is a legitimate service that provides Google Search results, including ads, through a simple API. It's:
- ✅ **Legal** - Complies with Google's terms
- ✅ **Reliable** - Professional service with 99.9% uptime
- ✅ **Comprehensive** - Returns ads, shopping results, extensions, and more
- ✅ **Easy** - Simple REST API

## Your API Key

Your SerpAPI key has been configured in `.env`:
```
SERPAPI_KEY=28f9888fa54352b9166b35d38dc7cc56d15106ca9b02d9439452d92c597ba6c4
```

## Quick Test

Test your integration right now:

```bash
cd backend
python scripts/test_serpapi.py
```

This will:
1. Verify your API key works
2. Fetch sample ads for "running shoes"
3. Display the data structure
4. Confirm everything is ready

## How It Works

### Automated Collection

1. **Add Keywords** in the web UI (Keywords page)
2. **System checks hourly** via Celery Beat
3. **SerpAPI fetches live ads** from Google
4. **Data is saved** to your database
5. **AI analyzes** patterns and trends

### What Gets Collected

For each ad, the system captures:
- **Headlines** - All headline variations
- **Descriptions** - Ad description text
- **Display URL** - The URL shown in the ad
- **Landing Page** - The actual destination URL
- **Extensions** - Sitelinks, callouts, structured snippets
- **Position** - Where the ad appears (1, 2, 3, etc.)
- **Advertiser** - Domain and company name
- **Timestamp** - When it was captured
- **Raw data** - Complete SerpAPI response

### Search Options

You can configure per keyword:
- **Location** - Target geographic area (e.g., "United States", "New York", "London")
- **Device** - desktop, mobile, or tablet
- **Interval** - How often to check (1-168 hours)

## Usage

### Option 1: Automated Monitoring (Recommended)

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Open web interface:**
   ```
   http://localhost:3000
   ```

3. **Add keywords:**
   - Go to Keywords page
   - Click "Add Keyword"
   - Enter: "running shoes"
   - Location: "United States"
   - Device: "desktop"
   - Interval: 1 hour
   - Click "Add Keyword"

4. **Wait for first check** (happens within the hour, or immediately on the hour)

5. **View results:**
   - Go to Ad Search page
   - Search for your keyword
   - See live ads!

### Option 2: Manual Search

Trigger an immediate search via API:

```bash
curl -X POST http://localhost:8000/api/v1/ads/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "running shoes",
    "location": "United States",
    "device_type": "desktop"
  }'
```

Or create a manual search endpoint (see below).

## API Reference

### SerpAPI Service

The `SerpAPIService` class handles all interactions:

```python
from app.services.serpapi_service import SerpAPIService

# Initialize
serpapi = SerpAPIService(api_key="your_key")

# Search for ads
ads = serpapi.search_ads(
    keyword="running shoes",
    location="United States",  # Optional
    device="desktop",          # desktop, mobile, tablet
    gl="us"                    # Country code
)

# Returns list of ad dictionaries with:
# - headlines, descriptions, extensions
# - advertiser info, URLs
# - position, timestamp
# - raw SerpAPI data
```

### Data Structure

Each ad returned has this structure:

```python
{
    "keyword": "running shoes",
    "location": "United States",
    "device_type": "desktop",
    "advertiser_domain": "nike.com",
    "advertiser_name": "Nike",
    "display_url": "nike.com/running",
    "final_url": "https://www.nike.com/...",
    "landing_page_url": "https://www.nike.com/...",
    "ad_position": 1,
    "is_top_ad": True,
    "source": "serpapi",
    "raw_data": {...},  # Full SerpAPI response
    "headlines": [
        {"headline_text": "Best Running Shoes", "position": 1},
        {"headline_text": "Free Shipping", "position": 2}
    ],
    "descriptions": [
        {"description_text": "Shop our latest...", "position": 1}
    ],
    "extensions": [
        {
            "extension_type": "sitelink",
            "extension_text": "Men's Running",
            "extension_url": "/mens",
            "position": 1
        }
    ]
}
```

## SerpAPI Pricing

Your account details: https://serpapi.com/manage-api-key

**Free Tier:**
- 100 searches/month
- Good for testing

**Paid Plans:**
- Starter: $50/month - 5,000 searches
- Pro: $150/month - 30,000 searches
- Business: $450/month - 100,000 searches

**Cost Per Keyword:**
- 1 keyword checked hourly = 720 searches/month
- With free tier: Can monitor ~7-10 keywords (considering some months have more hours)
- With Starter plan: Can monitor ~175 keywords
- With Pro plan: Can monitor ~1,000 keywords

**Tips to Conserve Searches:**
- Use longer intervals (check every 3-6 hours instead of hourly)
- Focus on most important keywords
- Pause keywords you don't need temporarily
- Use location/device filters to be specific

## Location Options

SerpAPI supports locations like:
- **Countries**: "United States", "United Kingdom", "Canada"
- **Cities**: "New York,New York,United States"
- **States**: "California,United States"

Or use location codes from: https://serpapi.com/locations

## Device Types

- **desktop** - Standard desktop results (default)
- **mobile** - Mobile phone results
- **tablet** - Tablet results

## Troubleshooting

### No ads found
- **Normal**: Some keywords don't have ads
- **Try**: More commercial keywords like "buy running shoes", "insurance", "lawyer"
- **Check**: Location matters - ads vary by region

### API errors
```python
# Check your remaining credits
from app.services.serpapi_service import SerpAPIService
serpapi = SerpAPIService("your_key")
serpapi.test_connection()  # Returns True if working
```

### Rate limits
- Free tier: 100/month
- Upgrade if needed: https://serpapi.com/pricing

### "No API key" errors
- Verify `.env` file has: `SERPAPI_KEY=your_actual_key`
- Restart Docker containers: `docker-compose restart`

## Advanced Usage

### Custom Search Parameters

Modify `backend/app/services/serpapi_service.py` to add more parameters:

```python
params = {
    "q": keyword,
    "api_key": self.api_key,
    "engine": "google",
    "gl": gl,  # Country
    "hl": "en",  # Language
    "device": device,
    "num": 10,  # Number of results
    "location": location,
}
```

See all options: https://serpapi.com/search-api

### Shopping Ads

The integration already captures shopping ads! They're included in the results automatically.

### Multiple Locations

Create separate keywords for each location:
```python
# Keyword 1: "running shoes" - Location: "New York"
# Keyword 2: "running shoes" - Location: "Los Angeles"
# Keyword 3: "running shoes" - Location: "London"
```

### Historical Tracking

The system never deletes data, so you can:
- Track how ads change over time
- See when competitors entered/exited
- Analyze seasonal trends
- Compare different time periods

## What's Next

Now that you have live data:

1. **Monitor Competitors**
   - Add their brand keywords
   - Track their ad copy changes
   - Identify their strategies

2. **Analyze Patterns**
   - Use the Analysis page
   - AI will find winning formulas
   - Get recommendations

3. **Chat with AI**
   - Ask questions about your data
   - Get headline suggestions
   - Understand trends

4. **Export & Report**
   - View historical data
   - Track changes
   - Share insights

## Example Workflow

```bash
# 1. Add keyword via API
curl -X POST http://localhost:8000/api/v1/keywords/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_text": "running shoes",
    "location": "United States",
    "device_type": "desktop",
    "check_interval_hours": 1
  }'

# 2. Wait for hourly check, or trigger manually
# (Celery Beat will run it automatically)

# 3. View collected ads
curl http://localhost:8000/api/v1/ads/?keyword=running+shoes

# 4. Run AI analysis
curl -X POST http://localhost:8000/api/v1/analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "keyword",
    "keywords": ["running shoes"]
  }'

# 5. Chat with AI
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the most common headlines?",
    "context_keywords": ["running shoes"]
  }'
```

## Support

- **SerpAPI Docs**: https://serpapi.com/search-api
- **SerpAPI Support**: https://serpapi.com/contact
- **Your Dashboard**: https://serpapi.com/manage-api-key

---

**You're all set! Your tool now collects real Google Ads data automatically!** 🎉

Start the application and watch the ads roll in:
```bash
docker-compose up -d
```

Then visit: http://localhost:3000
