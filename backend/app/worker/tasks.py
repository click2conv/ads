from celery import shared_task
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.worker.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.keyword_service import KeywordService
from app.services.ad_service import AdService


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
    Async implementation of keyword checking.
    """
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)
        ad_service = AdService(db)

        try:
            # Get keyword
            keyword = await keyword_service.get_keyword(keyword_id)

            if not keyword:
                print(f"Keyword {keyword_id} not found")
                return

            print(f"Checking keyword: {keyword.keyword_text}")

            # TODO: Integrate with your ad data source here
            # For now, this is a placeholder that demonstrates the structure

            # Example: Call your ad collection API/service
            # ads_data = await fetch_ads_from_source(
            #     keyword=keyword.keyword_text,
            #     location=keyword.location,
            #     device_type=keyword.device_type
            # )

            # Placeholder: Simulate ad collection
            ads_found = 0

            # For demonstration, we'll just update the status
            # In production, you would:
            # 1. Fetch ads from your data source (API, manual entry system, etc.)
            # 2. Save them using ad_service.capture_multiple_ads()
            # 3. Update keyword check status

            # Update keyword status
            await keyword_service.update_check_status(
                keyword_id=keyword_id,
                status="success",
                ads_found=ads_found,
            )

            await db.commit()

            print(f"Successfully checked keyword {keyword.keyword_text}: {ads_found} ads found")

        except Exception as e:
            print(f"Error checking keyword {keyword_id}: {str(e)}")

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
    Async implementation of manual search.
    """
    async with AsyncSessionLocal() as db:
        ad_service = AdService(db)

        try:
            # TODO: Integrate with your ad data source
            # For now, this is a placeholder

            # Example:
            # ads_data = await fetch_ads_from_source(
            #     keyword=keyword,
            #     location=location,
            #     device_type=device_type
            # )
            #
            # captured_ads = await ad_service.capture_multiple_ads(ads_data)

            print(f"Manual search for: {keyword} (location: {location}, device: {device_type})")

            # Placeholder return
            return {
                "keyword": keyword,
                "location": location,
                "device_type": device_type,
                "ads_found": 0,
                "message": "Search completed (integration with ad source required)"
            }

        except Exception as e:
            print(f"Error in manual search: {str(e)}")
            raise
