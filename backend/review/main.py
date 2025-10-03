import sys
import os
import logging

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log environment variables (without exposing secrets)
logger.info("Starting application initialization...")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variables present: SUPABASE_URL={'SUPABASE_URL' in os.environ}, SUPABASE_KEY={'SUPABASE_KEY' in os.environ}, GEMINI_API_KEY={'GEMINI_API_KEY' in os.environ}")

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from uuid import UUID
from services.models import ReviewCreate, Review
from services.services import ReviewService
from services.config import Config

logger.info("Imported all modules successfully")

app = FastAPI(title="Reviews Copilot API")

# Log CORS configuration
logger.info(f"Config.FRONTEND_ORIGIN: {Config.FRONTEND_ORIGIN}")

# Add CORS middleware for cloud deployment
allowed_origins = [Config.FRONTEND_ORIGIN] if Config.FRONTEND_ORIGIN else []
# Add common development origins
allowed_origins.extend([
    "http://localhost:5173",
    "http://localhost:3000",
    "https://reviewscopilot.onrender.com",
    "https://reviews-copilot-frontend.onrender.com"
])

logger.info(f"Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"]
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Initialize services
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        logger.info("Initializing review service...")
        app.state.review_service = ReviewService()
        logger.info("Review service initialized successfully")
        app.state.service_error = None
    except Exception as e:
        logger.error(f"Failed to initialize review service: {str(e)}", exc_info=True)
        # Set a None service so we can check for it in endpoints
        app.state.review_service = None
        app.state.service_error = str(e)
        logger.error("Review service initialization failed, continuing with app startup...")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    service_status = "healthy" if hasattr(app.state, 'review_service') and app.state.review_service is not None else "unhealthy"
    
    details = {}
    if hasattr(app.state, 'service_error'):
        details["service_error"] = app.state.service_error
    
    logger.info(f"Health check response: status=healthy, service={service_status}")
    return {"status": "healthy", "service": service_status, "details": details}

# Middleware to check service availability (but allow docs to work)
@app.middleware("http")
async def check_service_availability(request, call_next):
    # Skip service check for health, docs, and openapi endpoints
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
    if not any(request.url.path.startswith(path) for path in skip_paths):
        logger.info(f"Checking service availability for path: {request.url.path}")
        if not hasattr(app.state, 'review_service') or app.state.review_service is None:
            error_msg = f"Service not available - database connection failed: {getattr(app.state, 'service_error', 'Unknown error')}"
            logger.error(error_msg)
            return JSONResponse(
                status_code=503,
                content={"detail": "Service not available - database connection failed", "service_error": getattr(app.state, 'service_error', 'Unknown error')}
            )
    response = await call_next(request)
    return response

def get_review_service():
    """Helper function to get review service with proper error handling"""
    if not hasattr(app.state, 'review_service') or app.state.review_service is None:
        raise HTTPException(status_code=503, detail="Service not available - database connection failed")
    return app.state.review_service

@app.post("/ingest")
async def ingest_reviews(
    reviews: List[ReviewCreate],
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Ingest reviews with session_id"""
    try:
        review_service = get_review_service()
            
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
    except ValueError as e:
        logger.error(f"Value error in ingest_reviews: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in ingest_reviews: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/reviews")
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
        review_service = get_review_service()
        
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
    except ValueError as e:
        logger.error(f"Value error in list_reviews: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in list_reviews: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/reviews/{review_id}")
async def get_review(
    review_id: int,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Get review by ID"""
    try:
        review_service = get_review_service()
        
        session_id = UUID(x_session_id)
        review = await review_service.get_review(review_id, session_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except ValueError as e:
        logger.error(f"Value error in get_review: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in get_review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/reviews/{review_id}/suggest-reply")
async def suggest_reply(
    review_id: int,
    background_tasks: BackgroundTasks,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Generate AI reply for a review"""
    try:
        review_service = get_review_service()
        
        session_id = UUID(x_session_id)
        review = await review_service.get_review(review_id, session_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Call Gemini API
        reply_data = await review_service.generate_ai_reply(review)
        
        # Save to database in background to avoid blocking the response
        background_tasks.add_task(review_service.save_reply_to_db, review_id, reply_data["reply"])
        
        return reply_data
    except ValueError as e:
        logger.error(f"Value error in suggest_reply: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in suggest_reply: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics")
async def get_analytics(
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Get analytics for reviews"""
    try:
        review_service = get_review_service()
        
        session_id = UUID(x_session_id)
        analytics = await review_service.get_analytics(session_id)
        return analytics
    except ValueError as e:
        logger.error(f"Value error in get_analytics: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/search")
async def search_reviews(
    q: str,
    x_session_id: str = Header(..., alias="X-Session-Id")
):
    """Search reviews using TF-IDF and cosine similarity"""
    try:
        review_service = get_review_service()
        
        session_id = UUID(x_session_id)
        results = await review_service.search_reviews(session_id, q)
        return results
    except ValueError as e:
        logger.error(f"Value error in search_reviews: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in search_reviews: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)