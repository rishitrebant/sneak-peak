from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB functions
from backend.db import search_sneakers, get_price_history

# Scraper
from scraper.ajio_scraper import scrape_ajio, insert_into_db

from backend.price_detector import detect_and_queue

app = FastAPI()

# CORS (frontend connect ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# SEARCH API
# -------------------------
@app.get("/search")
def search(q: str):
    return search_sneakers(q)

# -------------------------
# PRICE HISTORY API
# -------------------------
@app.get("/price-history/{id}")
def history(id: int):
    return get_price_history(id)

# -------------------------
# RUN SCRAPER API (IMPORTANT)
# -------------------------
@app.get("/run-scraper")
def run_scraper():
    try:
        data = scrape_ajio("nike")
        insert_into_db(data)

        drops = detect_and_queue()

        return {
            "status": "done",
            "inserted": len(data),
            "drops_detected": drops
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}