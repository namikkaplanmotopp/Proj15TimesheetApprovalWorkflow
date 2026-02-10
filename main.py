import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import authentication
from router import user, project, timesheet_entry, timesheet, seed, health
from db import models
from db.database import engine

app = FastAPI(
    title="Timesheet API",
    description="Time tracking system for employees and managers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)  # Health check - no auth required
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(project.router)
app.include_router(timesheet_entry.router)
app.include_router(timesheet.router)
app.include_router(seed.router)

# Create database tables
models.Base.metadata.create_all(engine)

@app.get("/")
def root():
    return {
        "message": "Welcome to Timesheet API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Important: reload=False for debugging with breakpoints
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="debug",
    )
