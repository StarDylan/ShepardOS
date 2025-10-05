"""
ShepardOS Backend Server
Main entry point for the FastAPI application
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import init_db, get_db
from routers import users, permissions, roles, groups, terminals, currency, gatekeeping, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield

app = FastAPI(
    title="ShepardOS API",
    description="Gatekeeping, Currency, and Identity Verification System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["permissions"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(terminals.router, prefix="/api/terminals", tags=["terminals"])
app.include_router(currency.router, prefix="/api/currency", tags=["currency"])
app.include_router(gatekeeping.router, prefix="/api/gatekeeping", tags=["gatekeeping"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])

@app.get("/")
async def root():
    return {"message": "ShepardOS API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
