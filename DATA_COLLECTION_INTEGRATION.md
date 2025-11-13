# Data Collection Integration Guide

## Overview

This tool is designed to store and analyze Google Ads data, but **you need to provide the ad data**. This guide explains how to integrate various data sources.

## ⚠️ Important Legal Notice

**Direct scraping of Google Search results violates Google's Terms of Service.** This tool does NOT include scraping functionality. Instead, it provides infrastructure to collect, store, and analyze ad data from legitimate sources.

## Legitimate Data Sources

### 1. Manual Entry ✅
**Best for:** Small-scale monitoring, specific competitors

Use the API to manually add ads you observe:

```python
import requests

ad_data = {
    "keyword": "running shoes",
    "location": "United States",
    "device_type": "desktop",
    "advertiser_domain": "nike.com",
    "advertiser_name": "Nike",
    "display_url": "nike.com/running",
    "ad_position": 1,
    "headlines": [
        {"headline_text": "Best Running Shoes 2024"},
        {"headline_text": "Free Shipping & Returns"}
    ],
    "descriptions": [
        {"description_text": "Advanced cushioning technology for maximum comfort"}
    ],
    "extensions": [
        {"extension_type": "sitelink", "extension_text": "Shop Men's", "extension_url": "/mens"}
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/ads/capture",
    json=ad_data
)
```

### 2. Third-Party SEO/PPC Tools ✅
**Best for:** Comprehensive competitive analysis

These services legally collect and provide ad data:

#### SEMrush API
- Provides competitor ad data
- Historical ad tracking
- Pricing: Subscription-based
- Docs: https://www.semrush.com/api-documentation/

Example integration:

```python
import requests
from app.services.ad_service import AdService
from app.schemas.ad_data import AdCaptureCreate

async def fetch_from_semrush(keyword: str, db):
    # Call SEMrush API
    response = requests.get(
        "https://api.semrush.com/",
        params={
            "key": "YOUR_SEMRUSH_API_KEY",
            "type": "phrase_ads",
            "phrase": keyword,
            "database": "us"
        }
    )

    ads = response.json()

    # Convert to our format
    ad_service = AdService(db)

    for ad in ads:
        ad_capture = AdCaptureCreate(
            keyword=keyword,
            advertiser_domain=ad.get("domain"),
            headlines=[
                {"headline_text": ad.get("title")}
            ],
            descriptions=[
                {"description_text": ad.get("text")}
            ],
            source="semrush"
        )

        await ad_service.capture_ad(ad_capture)
```

#### SpyFu API
- Competitor ad tracking
- Historical data
- Pricing: Subscription-based
- Docs: https://www.spyfu.com/apis

#### Ahrefs API
- Ad insights
- Competitor analysis
- Pricing: Subscription-based
- Docs: https://ahrefs.com/api

### 3. Google Ads API ✅
**Best for:** Your own campaigns

If you want to analyze YOUR OWN ads:

- Use Google Ads API
- Completely legitimate
- Free for your own data
- Docs: https://developers.google.com/google-ads/api/docs/start

### 4. Browser Extension / Manual Tool 💡
**Best for:** Custom data collection workflow

Create a simple browser extension that:
1. User manually visits Google Ads
2. Extension extracts visible ad data
3. Sends to your API endpoint
4. Stored in database

This keeps a human in the loop and is more defensible legally.

## Integration Examples

### Example 1: CSV Import

Create a CSV with ad data and import it:

```python
# backend/scripts/import_csv.py
import csv
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.ad_service import AdService
from app.schemas.ad_data import AdCaptureCreate

async def import_csv(filename):
    async with AsyncSessionLocal() as db:
        ad_service = AdService(db)

        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                ad_data = AdCaptureCreate(
                    keyword=row['keyword'],
                    advertiser_domain=row['advertiser'],
                    headlines=[
                        {"headline_text": row['headline1']},
                        {"headline_text": row['headline2']},
                    ],
                    descriptions=[
                        {"description_text": row['description']}
                    ],
                    source="csv_import"
                )

                await ad_service.capture_ad(ad_data)

# Run it
asyncio.run(import_csv('ads.csv'))
```

CSV format:
```csv
keyword,advertiser,headline1,headline2,description
running shoes,nike.com,Best Running Shoes,Free Shipping,Shop our latest collection
```

### Example 2: Webhook Integration

If you have a service that collects ads, set up a webhook:

```python
# backend/app/api/webhook.py
from fastapi import APIRouter, Depends
from app.services.ad_service import AdService
from app.schemas.ad_data import AdCaptureCreate

router = APIRouter()

@router.post("/webhook/ads")
async def receive_ad_data(
    ad_data: AdCaptureCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive ad data from external service
    """
    service = AdService(db)
    ad = await service.capture_ad(ad_data)
    return {"status": "success", "ad_id": ad.id}
```

### Example 3: Scheduled API Polling

Poll an external API regularly:

```python
# backend/app/worker/tasks.py

@celery_app.task
def fetch_from_external_api():
    """
    Fetch ads from external API (SEMrush, SpyFu, etc.)
    """
    asyncio.run(_fetch_from_external_api_async())

async def _fetch_from_external_api_async():
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)
        ad_service = AdService(db)

        # Get active keywords
        keywords = await keyword_service.list_keywords(active_only=True)

        for keyword in keywords[0]:  # keywords is tuple (list, count)
            # Call your external API
            ads = await call_external_api(keyword.keyword_text)

            # Store ads
            for ad in ads:
                ad_capture = AdCaptureCreate(
                    keyword=keyword.keyword_text,
                    location=keyword.location,
                    device_type=keyword.device_type,
                    advertiser_domain=ad['domain'],
                    headlines=[
                        {"headline_text": h} for h in ad['headlines']
                    ],
                    descriptions=[
                        {"description_text": d} for d in ad['descriptions']
                    ],
                    source="external_api"
                )

                await ad_service.capture_ad(ad_capture)

async def call_external_api(keyword: str):
    """Replace with your actual API call"""
    # Example: SEMrush, SpyFu, etc.
    pass
```

## Modifying Celery Tasks

To integrate with automated monitoring, edit `backend/app/worker/tasks.py`:

```python
async def _check_keyword_async(keyword_id: int, task_id: str):
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)
        ad_service = AdService(db)

        try:
            keyword = await keyword_service.get_keyword(keyword_id)

            if not keyword:
                return

            # 🔥 YOUR INTEGRATION HERE 🔥
            # Option 1: Call external API
            ads_data = await fetch_ads_from_semrush(
                keyword=keyword.keyword_text,
                location=keyword.location,
                device=keyword.device_type
            )

            # Option 2: Read from file/database
            # ads_data = await read_ads_from_source()

            # Option 3: Call webhook/queue
            # ads_data = await get_ads_from_queue()

            # Store the ads
            ads_found = 0
            for ad_data in ads_data:
                ad_capture = AdCaptureCreate(**ad_data)
                await ad_service.capture_ad(ad_capture)
                ads_found += 1

            # Update status
            await keyword_service.update_check_status(
                keyword_id=keyword_id,
                status="success",
                ads_found=ads_found,
            )

            await db.commit()

        except Exception as e:
            await keyword_service.update_check_status(
                keyword_id=keyword_id,
                status="failed",
                ads_found=0,
            )
            await db.commit()
            raise
```

## Testing Your Integration

1. **Add Test Data**

```bash
# Add a keyword
curl -X POST http://localhost:8000/api/v1/keywords/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_text": "test keyword",
    "device_type": "desktop",
    "check_interval_hours": 1
  }'
```

2. **Trigger Manual Check**

Modify `backend/app/worker/tasks.py` to test your integration:

```python
# Add a test task
@celery_app.task
def test_integration():
    asyncio.run(_test_integration_async())

async def _test_integration_async():
    async with AsyncSessionLocal() as db:
        # Your integration code here
        print("Testing integration...")
```

Run it:
```bash
# From backend directory
python -c "from app.worker.tasks import test_integration; test_integration.delay()"
```

3. **Verify Data**

```bash
curl http://localhost:8000/api/v1/ads/?keyword=test+keyword
```

## Best Practices

### 1. Rate Limiting
```python
import time
from datetime import datetime, timedelta

last_call = {}

async def rate_limited_api_call(api_name: str, min_interval: int = 60):
    """
    Ensure minimum time between API calls
    """
    if api_name in last_call:
        elapsed = (datetime.now() - last_call[api_name]).seconds
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)

    last_call[api_name] = datetime.now()
```

### 2. Error Handling
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_retry(url):
    """Retry failed requests"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

### 3. Data Validation
```python
def validate_ad_data(ad_data: dict) -> bool:
    """
    Validate ad data before storing
    """
    required_fields = ['keyword', 'headlines']

    for field in required_fields:
        if field not in ad_data or not ad_data[field]:
            return False

    return True
```

### 4. Deduplication
```python
async def is_duplicate_ad(db, advertiser: str, headline: str, keyword: str):
    """
    Check if this ad already exists
    """
    query = select(AdCapture).where(
        and_(
            AdCapture.advertiser_domain == advertiser,
            AdCapture.keyword == keyword
        )
    )

    result = await db.execute(query)
    existing_ads = result.scalars().all()

    for ad in existing_ads:
        if any(h.headline_text == headline for h in ad.headlines):
            return True

    return False
```

## Recommended Approach

For most users, we recommend:

1. **Start with manual entry** - Get familiar with the system
2. **Subscribe to a third-party API** - SEMrush or SpyFu for professional use
3. **Integrate via the examples above** - Modify Celery tasks or create import scripts
4. **Use the AI features** - Get value from the analysis and chat

## Questions?

- Ensure your data collection method complies with terms of service
- Consider consulting with legal counsel for commercial use
- Focus on your own campaigns when possible (Google Ads API)
- Use legitimate third-party services for competitor analysis

Remember: This tool is designed to help you analyze and gain insights from ad data, not to scrape or violate terms of service.
