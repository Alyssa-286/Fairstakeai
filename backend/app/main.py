from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import schemesense, finance360, fairscore, loanguard, clearclause, rag


def create_app() -> FastAPI:
    app = FastAPI(
        title="FairStake AI API",
        description="APIs for SchemeSense, Finance360, FairScore, and LoanGuard modules.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(schemesense.router, prefix="/api/schemesense", tags=["SchemeSense"])
    app.include_router(finance360.router, prefix="/api/finance360", tags=["Finance360"])
    app.include_router(fairscore.router, prefix="/api/fairscore", tags=["FairScore"])
    app.include_router(loanguard.router, prefix="/api/loanguard", tags=["LoanGuard"])
    app.include_router(clearclause.router, prefix="/api/clearclause", tags=["ClearClause"])
    app.include_router(rag.router, tags=["RAG"])

    @app.get("/health", tags=["Utility"])
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    @app.get("/privacy", tags=["Utility"])
    async def privacy_note():
        return {
            "message": "All uploads and SMS data are processed in-memory for demo purposes and not persisted."
        }

    return app


app = create_app()

