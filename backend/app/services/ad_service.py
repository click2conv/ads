from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
import uuid as uuid_lib

from app.models.ad_data import AdCapture, AdHeadline, AdDescription, AdExtension
from app.schemas.ad_data import (
    AdCaptureCreate,
    AdHeadlineCreate,
    AdDescriptionCreate,
    AdExtensionCreate,
)


class AdService:
    """
    Service for managing ad data collection and storage.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def capture_ad(self, ad_data: AdCaptureCreate, search_id: Optional[str] = None) -> AdCapture:
        """
        Capture and store ad data.
        IMPORTANT: Never overwrites existing data - always creates new records.
        """
        # Create ad capture record
        ad_capture = AdCapture(
            keyword=ad_data.keyword,
            location=ad_data.location,
            device_type=ad_data.device_type,
            advertiser_domain=ad_data.advertiser_domain,
            advertiser_name=ad_data.advertiser_name,
            display_url=ad_data.display_url,
            final_url=ad_data.final_url,
            landing_page_url=ad_data.landing_page_url,
            ad_position=ad_data.ad_position,
            is_top_ad=ad_data.is_top_ad,
            source=ad_data.source or "manual",
            search_id=search_id or str(uuid_lib.uuid4()),
            raw_data=ad_data.raw_data,
            estimated_quality_score=ad_data.estimated_quality_score,
        )

        self.db.add(ad_capture)
        await self.db.flush()  # Get the ID

        # Add headlines
        for headline_data in ad_data.headlines:
            headline = AdHeadline(
                ad_capture_id=ad_capture.id,
                headline_text=headline_data.headline_text,
                position=headline_data.position,
                character_count=len(headline_data.headline_text),
            )
            self.db.add(headline)

        # Add descriptions
        for description_data in ad_data.descriptions:
            description = AdDescription(
                ad_capture_id=ad_capture.id,
                description_text=description_data.description_text,
                position=description_data.position,
                character_count=len(description_data.description_text),
            )
            self.db.add(description)

        # Add extensions
        for extension_data in ad_data.extensions:
            extension = AdExtension(
                ad_capture_id=ad_capture.id,
                extension_type=extension_data.extension_type,
                extension_text=extension_data.extension_text,
                extension_url=extension_data.extension_url,
                extension_data=extension_data.extension_data,
                position=extension_data.position,
            )
            self.db.add(extension)

        await self.db.commit()
        await self.db.refresh(ad_capture)

        return ad_capture

    async def capture_multiple_ads(
        self,
        ads_data: List[AdCaptureCreate],
        search_id: Optional[str] = None
    ) -> List[AdCapture]:
        """
        Capture multiple ads from a single search.
        """
        if not search_id:
            search_id = str(uuid_lib.uuid4())

        captured_ads = []
        for ad_data in ads_data:
            ad = await self.capture_ad(ad_data, search_id)
            captured_ads.append(ad)

        return captured_ads

    async def get_ad(self, ad_id: int) -> Optional[AdCapture]:
        """
        Get a single ad by ID with all related data.
        """
        query = select(AdCapture).where(AdCapture.id == ad_id)
        result = await self.db.execute(query)
        ad = result.scalar_one_or_none()

        if ad:
            # Load related data
            await self._load_ad_relations(ad)

        return ad

    async def _load_ad_relations(self, ad: AdCapture):
        """
        Load headlines, descriptions, and extensions for an ad.
        """
        # Load headlines
        headlines_query = select(AdHeadline).where(AdHeadline.ad_capture_id == ad.id)
        headlines_result = await self.db.execute(headlines_query)
        ad.headlines = list(headlines_result.scalars().all())

        # Load descriptions
        descriptions_query = select(AdDescription).where(AdDescription.ad_capture_id == ad.id)
        descriptions_result = await self.db.execute(descriptions_query)
        ad.descriptions = list(descriptions_result.scalars().all())

        # Load extensions
        extensions_query = select(AdExtension).where(AdExtension.ad_capture_id == ad.id)
        extensions_result = await self.db.execute(extensions_query)
        ad.extensions = list(extensions_result.scalars().all())

    async def search_ads(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        device_type: Optional[str] = None,
        advertiser: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AdCapture], int]:
        """
        Search ads with filters. Returns (ads, total_count).
        """
        # Build query
        query = select(AdCapture)
        count_query = select(func.count(AdCapture.id))

        filters = []

        if keyword:
            filters.append(AdCapture.keyword.ilike(f"%{keyword}%"))

        if location:
            filters.append(AdCapture.location == location)

        if device_type:
            filters.append(AdCapture.device_type == device_type)

        if advertiser:
            filters.append(
                or_(
                    AdCapture.advertiser_name.ilike(f"%{advertiser}%"),
                    AdCapture.advertiser_domain.ilike(f"%{advertiser}%"),
                )
            )

        if date_from:
            filters.append(AdCapture.captured_at >= date_from)

        if date_to:
            filters.append(AdCapture.captured_at <= date_to)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Get ads
        query = query.order_by(desc(AdCapture.captured_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        ads = list(result.scalars().all())

        # Load relations for each ad
        for ad in ads:
            await self._load_ad_relations(ad)

        return ads, total

    async def get_advertisers(self, limit: int = 100) -> List[str]:
        """
        Get list of unique advertisers.
        """
        query = (
            select(AdCapture.advertiser_domain)
            .distinct()
            .where(AdCapture.advertiser_domain.isnot(None))
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get_keywords(self, limit: int = 100) -> List[str]:
        """
        Get list of unique keywords.
        """
        query = (
            select(AdCapture.keyword)
            .distinct()
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get_ad_history(
        self,
        advertiser: str,
        keyword: Optional[str] = None,
        limit: int = 50
    ) -> List[AdCapture]:
        """
        Get historical ads for a specific advertiser.
        Useful for tracking how their ads change over time.
        """
        query = select(AdCapture).where(
            or_(
                AdCapture.advertiser_name.ilike(f"%{advertiser}%"),
                AdCapture.advertiser_domain.ilike(f"%{advertiser}%"),
            )
        )

        if keyword:
            query = query.where(AdCapture.keyword.ilike(f"%{keyword}%"))

        query = query.order_by(desc(AdCapture.captured_at)).limit(limit)

        result = await self.db.execute(query)
        ads = list(result.scalars().all())

        for ad in ads:
            await self._load_ad_relations(ad)

        return ads

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics about captured ads.
        """
        # Total ads
        total_ads_query = select(func.count(AdCapture.id))
        total_ads_result = await self.db.execute(total_ads_query)
        total_ads = total_ads_result.scalar()

        # Unique keywords
        unique_keywords_query = select(func.count(func.distinct(AdCapture.keyword)))
        unique_keywords_result = await self.db.execute(unique_keywords_query)
        unique_keywords = unique_keywords_result.scalar()

        # Unique advertisers
        unique_advertisers_query = select(func.count(func.distinct(AdCapture.advertiser_domain)))
        unique_advertisers_result = await self.db.execute(unique_advertisers_query)
        unique_advertisers = unique_advertisers_result.scalar()

        # Date range
        date_range_query = select(
            func.min(AdCapture.captured_at),
            func.max(AdCapture.captured_at)
        )
        date_range_result = await self.db.execute(date_range_query)
        date_range = date_range_result.first()

        return {
            "total_ads": total_ads,
            "unique_keywords": unique_keywords,
            "unique_advertisers": unique_advertisers,
            "oldest_capture": date_range[0].isoformat() if date_range[0] else None,
            "newest_capture": date_range[1].isoformat() if date_range[1] else None,
        }
