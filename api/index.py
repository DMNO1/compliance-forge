"""
ComplianceForge - Vercel Serverless Adapter
Wraps the FastAPI app for Vercel Python runtime
"""
import os
import sys
import logging

logger = logging.getLogger("complianceforge.vercel")

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from main import app
    logger.info("ComplianceForge app imported successfully")
except Exception as e:
    logger.error(f"ComplianceForge app import failed: {e}", exc_info=True)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="ComplianceForge (Error)")

    @app.get("/")
    @app.get("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=503,
            content={
                "error": "App failed to initialize",
                "detail": str(e),
                "hint": "Check Vercel function logs for full traceback"
            }
        )
