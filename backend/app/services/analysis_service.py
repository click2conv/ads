from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from anthropic import AsyncAnthropic
import json

from app.models.ad_data import AdCapture, AdHeadline, AdDescription, AdExtension
from app.models.analysis import Analysis, AnalysisInsight
from app.core.config import settings


class AnalysisService:
    """
    AI-powered analysis service using Claude.
    Analyzes ad data to find patterns, trends, and provide insights.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def create_analysis(
        self,
        analysis_type: str,
        keywords: Optional[List[str]] = None,
        competitors: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        device_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Analysis:
        """
        Create and run a new analysis.
        """
        # Create analysis record
        analysis = Analysis(
            analysis_type=analysis_type,
            keywords=keywords,
            competitors=competitors,
            date_from=date_from,
            date_to=date_to,
            device_type=device_type,
            location=location,
            status="processing",
            model_used=settings.CLAUDE_MODEL,
        )

        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        try:
            # Fetch relevant ad data
            ad_data = await self._fetch_ad_data(
                keywords=keywords,
                competitors=competitors,
                date_from=date_from,
                date_to=date_to,
                device_type=device_type,
                location=location,
            )

            # Analyze with Claude
            insights = await self._analyze_with_ai(ad_data, analysis_type)

            # Update analysis with results
            analysis.total_ads_analyzed = len(ad_data)
            analysis.total_headlines_analyzed = sum(len(ad.get("headlines", [])) for ad in ad_data)
            analysis.total_descriptions_analyzed = sum(len(ad.get("descriptions", [])) for ad in ad_data)

            # Create insight records
            for insight_data in insights:
                insight = AnalysisInsight(
                    analysis_id=analysis.id,
                    insight_type=insight_data.get("type", "general"),
                    category=insight_data.get("category", "overall"),
                    title=insight_data.get("title", ""),
                    description=insight_data.get("description", ""),
                    examples=insight_data.get("examples", []),
                    metrics=insight_data.get("metrics", {}),
                    priority=insight_data.get("priority", "medium"),
                    confidence_score=insight_data.get("confidence", 0.5),
                    recommendations=insight_data.get("recommendations", []),
                )
                self.db.add(insight)

            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()

        except Exception as e:
            analysis.status = "failed"
            analysis.summary = f"Analysis failed: {str(e)}"

        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis

    async def _fetch_ad_data(
        self,
        keywords: Optional[List[str]] = None,
        competitors: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        device_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch ad data from database based on filters.
        """
        # Build query
        query = select(AdCapture)

        filters = []

        if keywords:
            filters.append(AdCapture.keyword.in_(keywords))

        if competitors:
            filters.append(AdCapture.advertiser_domain.in_(competitors))

        if date_from:
            filters.append(AdCapture.captured_at >= date_from)

        if date_to:
            filters.append(AdCapture.captured_at <= date_to)

        if device_type:
            filters.append(AdCapture.device_type == device_type)

        if location:
            filters.append(AdCapture.location == location)

        if filters:
            query = query.where(and_(*filters))

        # Execute query
        result = await self.db.execute(query.limit(1000))  # Limit to prevent overload
        ads = result.scalars().all()

        # Format ad data
        ad_data = []
        for ad in ads:
            # Fetch related data
            headlines_result = await self.db.execute(
                select(AdHeadline).where(AdHeadline.ad_capture_id == ad.id)
            )
            headlines = headlines_result.scalars().all()

            descriptions_result = await self.db.execute(
                select(AdDescription).where(AdDescription.ad_capture_id == ad.id)
            )
            descriptions = descriptions_result.scalars().all()

            extensions_result = await self.db.execute(
                select(AdExtension).where(AdExtension.ad_capture_id == ad.id)
            )
            extensions = extensions_result.scalars().all()

            ad_data.append({
                "id": ad.id,
                "keyword": ad.keyword,
                "advertiser": ad.advertiser_name or ad.advertiser_domain,
                "headlines": [h.headline_text for h in headlines],
                "descriptions": [d.description_text for d in descriptions],
                "extensions": [
                    {"type": e.extension_type, "text": e.extension_text}
                    for e in extensions
                ],
                "position": ad.ad_position,
                "captured_at": ad.captured_at.isoformat() if ad.captured_at else None,
            })

        return ad_data

    async def _analyze_with_ai(
        self,
        ad_data: List[Dict[str, Any]],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """
        Use Claude to analyze ad data and generate insights.
        """
        if not ad_data:
            return [{
                "type": "general",
                "category": "overall",
                "title": "No Data Available",
                "description": "No ad data was found matching the specified criteria.",
                "priority": "high",
                "confidence": 1.0,
                "recommendations": ["Add more keywords to monitor", "Expand date range"],
            }]

        # Prepare prompt for Claude
        prompt = self._build_analysis_prompt(ad_data, analysis_type)

        # Call Claude API
        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response
        insights = self._parse_insights(response.content[0].text)

        return insights

    def _build_analysis_prompt(self, ad_data: List[Dict[str, Any]], analysis_type: str) -> str:
        """
        Build a detailed prompt for Claude to analyze the ad data.
        """
        # Summarize the data
        total_ads = len(ad_data)
        all_headlines = []
        all_descriptions = []
        advertisers = set()

        for ad in ad_data:
            all_headlines.extend(ad.get("headlines", []))
            all_descriptions.extend(ad.get("descriptions", []))
            if ad.get("advertiser"):
                advertisers.add(ad["advertiser"])

        # Build prompt
        prompt = f"""You are an expert PPC advertising analyst. Analyze the following Google Ads data and provide actionable insights.

ANALYSIS TYPE: {analysis_type}

DATA SUMMARY:
- Total Ads: {total_ads}
- Total Headlines: {len(all_headlines)}
- Total Descriptions: {len(all_descriptions)}
- Unique Advertisers: {len(advertisers)}

AD DATA:
{json.dumps(ad_data[:50], indent=2)}  # Limit to first 50 ads to avoid token limits

TASK:
Analyze this ad data and provide insights in the following JSON format:

[
  {{
    "type": "pattern|recommendation|trend|gap|winner",
    "category": "headline|description|extension|overall",
    "title": "Brief title of the insight",
    "description": "Detailed description of what you found",
    "examples": ["example 1", "example 2"],
    "metrics": {{"key": "value"}},
    "priority": "high|medium|low",
    "confidence": 0.0-1.0,
    "recommendations": ["actionable recommendation 1", "actionable recommendation 2"]
  }}
]

Focus on:
1. **Patterns**: Common themes, structures, or formulas in successful ads
2. **Trends**: Changes over time, emerging strategies
3. **Winners**: What makes the top-performing ads effective
4. **Gaps**: Opportunities competitors are missing
5. **Recommendations**: Specific, actionable advice for creating better ads

Consider:
- Headline structures (questions, benefits, numbers, urgency)
- Emotional triggers (fear, desire, trust, urgency)
- Calls to action
- Value propositions
- Differentiation strategies
- Use of numbers and statistics
- Brand positioning

Return ONLY valid JSON array of insights, no additional text."""

        return prompt

    def _parse_insights(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse Claude's response into structured insights.
        """
        try:
            # Try to extract JSON from response
            # Claude sometimes adds text before/after JSON
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                insights = json.loads(json_str)
                return insights
            else:
                # Fallback: create a single insight with the full response
                return [{
                    "type": "general",
                    "category": "overall",
                    "title": "Analysis Summary",
                    "description": response_text,
                    "priority": "medium",
                    "confidence": 0.7,
                    "recommendations": [],
                }]

        except json.JSONDecodeError:
            # Fallback: create a single insight with the response
            return [{
                "type": "general",
                "category": "overall",
                "title": "Analysis Summary",
                "description": response_text,
                "priority": "medium",
                "confidence": 0.7,
                "recommendations": [],
            }]

    async def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """
        Get analysis by ID with all insights.
        """
        query = select(Analysis).where(Analysis.id == analysis_id)
        result = await self.db.execute(query)
        analysis = result.scalar_one_or_none()

        if analysis:
            # Load insights
            insights_query = select(AnalysisInsight).where(
                AnalysisInsight.analysis_id == analysis_id
            )
            insights_result = await self.db.execute(insights_query)
            analysis.insights = list(insights_result.scalars().all())

        return analysis
