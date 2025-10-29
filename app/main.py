from fastapi import FastAPI
from .routes import country
from .config.Config import init_db

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(country.router)