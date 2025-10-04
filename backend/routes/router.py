from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from typing import Optional, List
from uuid import UUID
from services import models
from services.service import review_service

router = APIRouter(tags=["reviews"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.post("/ingest")
async def ingest_reviews(
    reviews: List[models.ReviewCreate],
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Ingest reviews with session_id"""
    try:
        session_id = UUID(x_session_id)
        created_reviews = []
        
        for review_data in reviews:
            # Validate session_id matches
            if review_data.session_id != session_id:
                raise HTTPException(status_code=400, detail="Session ID mismatch")
            
            # Redact sensitive information
            review_data.text = redact_sensitive_info(review_data.text)
            
            # Create review
            review = await review_service.create_review(review_data)
            created_reviews.append(review)
        
        return created_reviews
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

@router.get("/reviews")
async def list_reviews(
    location: Optional[str] = None,
    sentiment: Optional[str] = None,
    topic: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """List reviews with filters and pagination"""
    try:
        session_id = UUID(x_session_id)
        reviews = await review_service.list_reviews(
            session_id=session_id,
            location=location,
            sentiment=sentiment,
            topic=topic,
            search_query=q,
            page=page,
            page_size=page_size
        )
        return reviews
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

@router.get("/reviews/{review_id}")
async def get_review(
    review_id: int,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Get review by ID"""
    try:
        session_id = UUID(x_session_id)
        review = await review_service.get_review(review_id, session_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@router.post("/reviews/{review_id}/suggest-reply")
async def suggest_reply(
    review_id: int,
    background_tasks: BackgroundTasks,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Generate AI reply for a review"""
    try:
        session_id = UUID(x_session_id)
        review = await review_service.get_review(review_id, session_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Call Gemini API
        reply_data = await review_service.generate_ai_reply(review)
        
        # Save to database in background to avoid blocking the response
        background_tasks.add_task(review_service.save_reply_to_db, review_id, reply_data["reply"])
        
        return reply_data
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@router.get("/analytics")
async def get_analytics(
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Get analytics for reviews"""
    try:
        session_id = UUID(x_session_id)
        analytics = await review_service.get_analytics(session_id)
        return analytics
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

@router.get("/search")
async def search_reviews(
    q: str,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Search reviews using TF-IDF and cosine similarity"""
    try:
        session_id = UUID(x_session_id)
        results = await review_service.search_reviews(session_id, q)
        return results
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

def redact_sensitive_info(text: str) -> str:
    """Redact sensitive information like emails and phone numbers"""
    import re
    
    # Redact email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
    
    # Redact phone numbers (various formats)
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',
        r'\b\d{3}\.\d{3}\.\d{4}\b',
        r'\b\d{10}\b'
    ]
    
    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE REDACTED]', text)
    
    return text