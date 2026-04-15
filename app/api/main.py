from fastapi import FastAPI
from app.logging_config import configure_logging
from app.api.routes import router

configure_logging()

app = FastAPI(title="Ask My Docs", version="1.0.0")
app.include_router(router)