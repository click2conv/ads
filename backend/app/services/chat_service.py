from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from anthropic import AsyncAnthropic
import json

from app.models.chat import ChatSession, ChatMessage
from app.models.ad_data import AdCapture, AdHeadline, AdDescription
from app.core.config import settings


class ChatService:
    """
    AI-powered chat service for interactive conversations about ad data.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def create_session(
        self,
        session_name: Optional[str] = None,
        context_keywords: Optional[List[str]] = None,
        context_date_from: Optional[datetime] = None,
        context_date_to: Optional[datetime] = None,
    ) -> ChatSession:
        """
        Create a new chat session.
        """
        session = ChatSession(
            session_name=session_name or f"Chat {datetime.utcnow().isoformat()}",
            context_keywords=context_keywords,
            context_date_from=context_date_from,
            context_date_to=context_date_to,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def send_message(
        self,
        session_id: int,
        user_message: str,
        context_keywords: Optional[List[str]] = None,
        context_date_from: Optional[datetime] = None,
        context_date_to: Optional[datetime] = None,
    ) -> ChatMessage:
        """
        Send a message and get AI response.
        """
        # Get or create session
        session = await self._get_session(session_id)

        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Update session context if provided
        if context_keywords:
            session.context_keywords = context_keywords
        if context_date_from:
            session.context_date_from = context_date_from
        if context_date_to:
            session.context_date_to = context_date_to

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_message,
        )
        self.db.add(user_msg)

        # Get conversation history
        history = await self._get_conversation_history(session.id)

        # Fetch relevant ad data based on context
        context_data = await self._fetch_context_data(
            keywords=session.context_keywords,
            date_from=session.context_date_from,
            date_to=session.context_date_to,
        )

        # Generate AI response
        ai_response = await self._generate_response(
            user_message=user_message,
            history=history,
            context_data=context_data,
        )

        # Save AI message
        ai_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response["content"],
            model_used=settings.CLAUDE_MODEL,
            tokens_used=ai_response.get("tokens_used", 0),
            context_data=context_data if context_data else None,
        )
        self.db.add(ai_msg)

        # Update session
        session.total_messages += 2  # User + AI
        session.last_message_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(ai_msg)

        return ai_msg

    async def _get_session(self, session_id: int) -> Optional[ChatSession]:
        """
        Get session by ID.
        """
        query = select(ChatSession).where(ChatSession.id == session_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_conversation_history(self, session_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get recent conversation history.
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = list(result.scalars().all())
        messages.reverse()  # Oldest first

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def _fetch_context_data(
        self,
        keywords: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Fetch relevant ad data for context.
        """
        if not keywords and not date_from and not date_to:
            return {}

        # Build query
        query = select(AdCapture)
        filters = []

        if keywords:
            filters.append(AdCapture.keyword.in_(keywords))

        if date_from:
            filters.append(AdCapture.captured_at >= date_from)

        if date_to:
            filters.append(AdCapture.captured_at <= date_to)

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit)

        result = await self.db.execute(query)
        ads = result.scalars().all()

        # Gather statistics
        all_headlines = []
        all_descriptions = []
        advertisers = set()
        keywords_set = set()

        for ad in ads:
            # Fetch headlines
            headlines_result = await self.db.execute(
                select(AdHeadline).where(AdHeadline.ad_capture_id == ad.id)
            )
            headlines = [h.headline_text for h in headlines_result.scalars().all()]
            all_headlines.extend(headlines)

            # Fetch descriptions
            descriptions_result = await self.db.execute(
                select(AdDescription).where(AdDescription.ad_capture_id == ad.id)
            )
            descriptions = [d.description_text for d in descriptions_result.scalars().all()]
            all_descriptions.extend(descriptions)

            if ad.advertiser_name or ad.advertiser_domain:
                advertisers.add(ad.advertiser_name or ad.advertiser_domain)

            keywords_set.add(ad.keyword)

        return {
            "total_ads": len(ads),
            "total_headlines": len(all_headlines),
            "total_descriptions": len(all_descriptions),
            "unique_advertisers": len(advertisers),
            "keywords": list(keywords_set),
            "sample_headlines": all_headlines[:20],  # First 20
            "sample_descriptions": all_descriptions[:20],
            "advertisers": list(advertisers),
        }

    async def _generate_response(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        context_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate AI response using Claude.
        """
        # Build system prompt
        system_prompt = """You are an expert PPC advertising analyst assistant. You help users understand and analyze Google Ads data.

You have access to a database of captured ad data including headlines, descriptions, ad extensions, and competitor information.

When answering questions:
1. Reference specific data points from the context when available
2. Provide actionable insights and recommendations
3. Use examples from the actual ad data
4. Be concise but thorough
5. If asked for suggestions, provide specific, actionable ad copy

Available context data will be provided with each query."""

        # Build user prompt with context
        user_prompt = f"""USER QUESTION: {user_message}

AVAILABLE DATA CONTEXT:
{json.dumps(context_data, indent=2) if context_data else "No specific data context provided."}

Please answer the user's question based on the available data. If the data is limited, acknowledge this and provide general best practices."""

        # Build messages for Claude
        messages = []

        # Add conversation history
        messages.extend(history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        # Call Claude API
        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2048,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )

        return {
            "content": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        }

    async def get_session_messages(self, session_id: int) -> List[ChatMessage]:
        """
        Get all messages for a session.
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_sessions(self, active_only: bool = True) -> List[ChatSession]:
        """
        List all chat sessions.
        """
        query = select(ChatSession).order_by(ChatSession.created_at.desc())

        if active_only:
            query = query.where(ChatSession.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())
