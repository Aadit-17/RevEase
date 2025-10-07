from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from routes import router

# Initialize FastAPI app
app = FastAPI(
    title="RevEase API",
    description="AI-powered customer review analysis and response generation",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        Config.FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"]
)

# Include routers
app.include_router(router.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to RevEase API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
