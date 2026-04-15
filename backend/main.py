from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB functions
from backend.db import search_sneakers, get_price_history

# Scraper
from scraper.ajio_scraper import scrape_ajio, insert_into_db

from backend.price_detector import detect_and_queue

from backend.alert_sender import process_alert_queue

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
@app.get("/run-scraper")
def run_scraper():
    data = scrape_ajio("nike")
    insert_into_db(data)

    from backend.price_detector import detect_and_queue
    drops = detect_and_queue()

    from backend.alert_sender import process_alert_queue
    process_alert_queue()   # 🔥 THIS WAS MISSING

    return {
        "status": "done",
        "inserted": len(data),
        "drops_detected": drops
    }
from backend.alert_sender import _send_email

@app.get("/test-email")
def test_email():
    dummy = {
        "email": "sneakpeak.connect@gmail.com",  
        "name": "Nike Test Sneaker",
        "old_price": 5000,
        "new_price": 3500,
        "drop_pct": 30,
        "platform": "Ajio",
        "url": "https://ajio.com/test"
    }

    _send_email(dummy)
    return {"status": "email sent"}