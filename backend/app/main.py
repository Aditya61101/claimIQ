from app.setup import app

from app.core.database import engine
from app.core.database import Base
# routes
from app.api.claims import router as claims_router
from app.api.documents import router as documents_router

# reads all models inheriting from base, generates SQL, creates tables if they dont exist
Base.metadata.create_all(bind=engine)

# router registry
app.include_router(claims_router)
app.include_router(documents_router)

@app.get("/health")
def get_health():
    return {"status": "ok"}