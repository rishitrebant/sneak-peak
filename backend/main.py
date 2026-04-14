from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db import search_sneakers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search(q: str):
    return search_sneakers(q)

from backend.db import get_price_history

@app.get("/price-history/{id}")
def history(id: int):
    return get_price_history(id)


from scraper.ajio_scraper import scrape_ajio, insert_into_db

@app.get("/run-scraper")
def run_scraper():
    data = scrape_ajio("nike")
    insert_into_db(data)
    return {"status": "done", "inserted": len(data)}