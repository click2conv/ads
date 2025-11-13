from celery import shared_task
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.worker.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.keyword_service import KeywordService
from app.services.ad_service import AdService
from app.services.serpapi_service import SerpAPIService
from app.schemas.ad_data import AdCaptureCreate, AdHeadlineCreate, AdDescriptionCreate, AdExtensionCreate
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.check_all_keywords")
def check_all_keywords():
    """
    Periodic task to check all active keywords that are due for monitoring.
    Runs every hour via Celery Beat.
    """
    asyncio.run(_check_all_keywords_async())


async def _check_all_keywords_async():
    """
    Async implementation of check_all_keywords.
    """
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)

        # Get keywords that need checking
        keywords = await keyword_service.get_keywords_for_monitoring()

        print(f"Found {len(keywords)} keywords to check")

        for keyword in keywords:
            # Schedule individual keyword check
            task = check_keyword.delay(keyword.id)

            # Create monitor task record
            await keyword_service.create_monitor_task(
                keyword_id=keyword.id,
                scheduled_at=datetime.utcnow(),
                task_id=task.id,
            )

        await db.commit()


@celery_app.task(name="app.worker.tasks.check_keyword", bind=True)
def check_keyword(self, keyword_id: int):
    """
    Check a specific keyword and capture ads.
    This is where you would integrate with your ad data source.
    """
    asyncio.run(_check_keyword_async(keyword_id, self.request.id))


async def _check_keyword_async(keyword_id: int, task_id: str):
    """
    Async implementation of keyword checking using SerpAPI.
    """
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)
        ad_service = AdService(db)

        try:
            # Get keyword
            keyword = await keyword_service.get_keyword(keyword_id)

            if not keyword:
                logger.error(f"Keyword {keyword_id} not found")
                return

            logger.info(f"Checking keyword: {keyword.keyword_text}")

            # Check if SerpAPI is configured
            serpapi_key = getattr(settings, 'SERPAPI_KEY', None)
            if not serpapi_key:
                logger.error("SERPAPI_KEY not configured in settings")
                await keyword_service.update_check_status(
                    keyword_id=keyword_id,
                    status="failed",
                    ads_found=0,
                )
                await db.commit()
                return

            # Initialize SerpAPI service
            serpapi = SerpAPIService(serpapi_key)

            # Fetch ads from SerpAPI
            ads_data = serpapi.search_ads(
                keyword=keyword.keyword_text,
                location=keyword.location,
                device=keyword.device_type or "desktop",
            )

            logger.info(f"SerpAPI returned {len(ads_data)} ads for keyword: {keyword.keyword_text}")

            # Convert to our schema and save
            ads_found = 0
            for ad_data in ads_data:
                try:
                    # Convert headlines
                    headlines = [
                        AdHeadlineCreate(**h) for h in ad_data.get("headlines", [])
                    ]

                    # Convert descriptions
                    descriptions = [
                        AdDescriptionCreate(**d) for d in ad_data.get("descriptions", [])
                    ]

                    # Convert extensions
                    extensions = [
                        AdExtensionCreate(**e) for e in ad_data.get("extensions", [])
                    ]

                    # Create ad capture
                    ad_capture = AdCaptureCreate(
                        keyword=ad_data["keyword"],
                        location=ad_data.get("location"),
                        device_type=ad_data.get("device_type"),
                        advertiser_domain=ad_data.get("advertiser_domain"),
                        advertiser_name=ad_data.get("advertiser_name"),
                        display_url=ad_data.get("display_url"),
                        final_url=ad_data.get("final_url"),
                        landing_page_url=ad_data.get("landing_page_url"),
                        ad_position=ad_data.get("ad_position"),
                        is_top_ad=ad_data.get("is_top_ad", True),
                        source=ad_data.get("source", "serpapi"),
                        raw_data=ad_data.get("raw_data"),
                        headlines=headlines,
                        descriptions=descriptions,
                        extensions=extensions,
                    )

                    # Save to database
                    await ad_service.capture_ad(ad_capture)
                    ads_found += 1

                except Exception as e:
                    logger.error(f"Error saving ad: {str(e)}")
                    continue

            # Update keyword status
            await keyword_service.update_check_status(
                keyword_id=keyword_id,
                status="success",
                ads_found=ads_found,
            )

            await db.commit()

            logger.info(f"Successfully checked keyword {keyword.keyword_text}: {ads_found} ads saved")

        except Exception as e:
            logger.error(f"Error checking keyword {keyword_id}: {str(e)}")

            # Update keyword status as failed
            await keyword_service.update_check_status(
                keyword_id=keyword_id,
                status="failed",
                ads_found=0,
            )

            await db.commit()

            raise


@celery_app.task(name="app.worker.tasks.manual_search")
def manual_search(keyword: str, location: str = None, device_type: str = "desktop"):
    """
    Perform a manual ad search.
    This can be triggered from the API when a user wants to search immediately.
    """
    return asyncio.run(_manual_search_async(keyword, location, device_type))


async def _manual_search_async(keyword: str, location: str, device_type: str):
    """
    Async implementation of manual search using SerpAPI.
    """
    async with AsyncSessionLocal() as db:
        ad_service = AdService(db)

        try:
            # Check if SerpAPI is configured
            serpapi_key = getattr(settings, 'SERPAPI_KEY', None)
            if not serpapi_key:
                logger.error("SERPAPI_KEY not configured in settings")
                return {
                    "keyword": keyword,
                    "location": location,
                    "device_type": device_type,
                    "ads_found": 0,
                    "message": "SerpAPI key not configured"
                }

            logger.info(f"Manual search for: {keyword} (location: {location}, device: {device_type})")

            # Initialize SerpAPI service
            serpapi = SerpAPIService(serpapi_key)

            # Fetch ads from SerpAPI
            ads_data = serpapi.search_ads(
                keyword=keyword,
                location=location,
                device=device_type or "desktop",
            )

            logger.info(f"SerpAPI returned {len(ads_data)} ads")

            # Convert to our schema and save
            ads_found = 0
            for ad_data in ads_data:
                try:
                    # Convert headlines
                    headlines = [
                        AdHeadlineCreate(**h) for h in ad_data.get("headlines", [])
                    ]

                    # Convert descriptions
                    descriptions = [
                        AdDescriptionCreate(**d) for d in ad_data.get("descriptions", [])
                    ]

                    # Convert extensions
                    extensions = [
                        AdExtensionCreate(**e) for e in ad_data.get("extensions", [])
                    ]

                    # Create ad capture
                    ad_capture = AdCaptureCreate(
                        keyword=ad_data["keyword"],
                        location=ad_data.get("location"),
                        device_type=ad_data.get("device_type"),
                        advertiser_domain=ad_data.get("advertiser_domain"),
                        advertiser_name=ad_data.get("advertiser_name"),
                        display_url=ad_data.get("display_url"),
                        final_url=ad_data.get("final_url"),
                        landing_page_url=ad_data.get("landing_page_url"),
                        ad_position=ad_data.get("ad_position"),
                        is_top_ad=ad_data.get("is_top_ad", True),
                        source=ad_data.get("source", "serpapi"),
                        raw_data=ad_data.get("raw_data"),
                        headlines=headlines,
                        descriptions=descriptions,
                        extensions=extensions,
                    )

                    # Save to database
                    await ad_service.capture_ad(ad_capture)
                    ads_found += 1

                except Exception as e:
                    logger.error(f"Error saving ad: {str(e)}")
                    continue

            await db.commit()

            logger.info(f"Manual search completed: {ads_found} ads saved")

            return {
                "keyword": keyword,
                "location": location,
                "device_type": device_type,
                "ads_found": ads_found,
                "message": f"Successfully collected {ads_found} ads from SerpAPI"
            }

        except Exception as e:
            logger.error(f"Error in manual search: {str(e)}")
            raise
