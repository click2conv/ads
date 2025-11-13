from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc

from app.models.keyword import Keyword, KeywordMonitor
from app.schemas.keyword import KeywordCreate, KeywordUpdate


class KeywordService:
    """
    Service for managing keywords and monitoring schedules.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_keyword(self, keyword_data: KeywordCreate) -> Keyword:
        """
        Create a new keyword to monitor.
        """
        keyword = Keyword(
            keyword_text=keyword_data.keyword_text,
            location=keyword_data.location,
            device_type=keyword_data.device_type,
            check_interval_hours=keyword_data.check_interval_hours,
            notes=keyword_data.notes,
            tags=keyword_data.tags,
            is_active=True,
        )

        self.db.add(keyword)
        await self.db.commit()
        await self.db.refresh(keyword)

        return keyword

    async def get_keyword(self, keyword_id: int) -> Optional[Keyword]:
        """
        Get keyword by ID.
        """
        query = select(Keyword).where(Keyword.id == keyword_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_keywords(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Keyword], int]:
        """
        List keywords with optional filtering.
        """
        query = select(Keyword)

        if active_only:
            query = query.where(Keyword.is_active == True)

        # Count total
        from sqlalchemy import func
        count_query = select(func.count(Keyword.id))
        if active_only:
            count_query = count_query.where(Keyword.is_active == True)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Get keywords
        query = query.order_by(desc(Keyword.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        keywords = list(result.scalars().all())

        return keywords, total

    async def update_keyword(self, keyword_id: int, update_data: KeywordUpdate) -> Optional[Keyword]:
        """
        Update keyword settings.
        """
        keyword = await self.get_keyword(keyword_id)

        if not keyword:
            return None

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(keyword, field, value)

        keyword.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(keyword)

        return keyword

    async def delete_keyword(self, keyword_id: int) -> bool:
        """
        Soft delete keyword (set inactive).
        """
        keyword = await self.get_keyword(keyword_id)

        if not keyword:
            return False

        keyword.is_active = False
        keyword.updated_at = datetime.utcnow()

        await self.db.commit()

        return True

    async def get_keywords_for_monitoring(self) -> List[Keyword]:
        """
        Get active keywords that need to be checked.
        This considers the last check time and check interval.
        """
        from sqlalchemy import or_

        # Get keywords that:
        # 1. Are active
        # 2. Have never been checked OR
        # 3. Last check was more than check_interval_hours ago
        query = select(Keyword).where(
            and_(
                Keyword.is_active == True,
                or_(
                    Keyword.last_checked_at.is_(None),
                    Keyword.last_checked_at < datetime.utcnow() - func.make_interval(hours=Keyword.check_interval_hours)
                )
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_check_status(
        self,
        keyword_id: int,
        status: str,
        ads_found: int = 0
    ) -> Optional[Keyword]:
        """
        Update keyword after a monitoring check.
        """
        keyword = await self.get_keyword(keyword_id)

        if not keyword:
            return None

        keyword.last_checked_at = datetime.utcnow()
        keyword.last_check_status = status
        keyword.total_checks += 1
        keyword.total_ads_found += ads_found

        await self.db.commit()
        await self.db.refresh(keyword)

        return keyword

    async def create_monitor_task(
        self,
        keyword_id: int,
        scheduled_at: datetime,
        task_id: Optional[str] = None
    ) -> KeywordMonitor:
        """
        Create a monitoring task record.
        """
        monitor = KeywordMonitor(
            keyword_id=keyword_id,
            scheduled_at=scheduled_at,
            status="pending",
            task_id=task_id,
        )

        self.db.add(monitor)
        await self.db.commit()
        await self.db.refresh(monitor)

        return monitor

    async def update_monitor_task(
        self,
        monitor_id: int,
        status: str,
        ads_found: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[KeywordMonitor]:
        """
        Update monitoring task status.
        """
        query = select(KeywordMonitor).where(KeywordMonitor.id == monitor_id)
        result = await self.db.execute(query)
        monitor = result.scalar_one_or_none()

        if not monitor:
            return None

        monitor.status = status

        if status == "running" and not monitor.started_at:
            monitor.started_at = datetime.utcnow()

        if status in ["completed", "failed"]:
            monitor.completed_at = datetime.utcnow()

        if ads_found is not None:
            monitor.ads_found = ads_found

        if error_message:
            monitor.error_message = error_message

        await self.db.commit()
        await self.db.refresh(monitor)

        return monitor

    async def get_monitor_history(
        self,
        keyword_id: int,
        limit: int = 50
    ) -> List[KeywordMonitor]:
        """
        Get monitoring history for a keyword.
        """
        query = (
            select(KeywordMonitor)
            .where(KeywordMonitor.keyword_id == keyword_id)
            .order_by(desc(KeywordMonitor.scheduled_at))
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
