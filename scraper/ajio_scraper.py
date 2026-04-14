from playwright.sync_api import sync_playwright
import psycopg2
import time

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="pass"
    )

def scrape_ajio(query):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # faster + safer load
        page.goto(f"https://www.ajio.com/search/?text={query}", timeout=60000, wait_until="domcontentloaded")

        # wait for products manually
        page.wait_for_timeout(8000)

        items = page.query_selector_all(".item")

        print("Found items:", len(items))  # debug

        for item in items[:5]:
            try:
                name = item.query_selector(".nameCls").inner_text()
                price = item.query_selector(".price").inner_text()

                price = int(''.join(filter(str.isdigit, price)))

                results.append({
                    "name": name,
                    "brand": "Unknown",
                    "price": price,
                    "platform": "Ajio",
                    "url": "https://ajio.com"
                })
            except Exception as e:
                print("Error:", e)
                continue

        browser.close()

    return results

def insert_into_db(data):
    conn = get_connection()
    cur = conn.cursor()

    for item in data:
        # insert or ignore duplicate
        cur.execute("""
            INSERT INTO sneakers (name, brand, price, platform, url, in_stock)
            VALUES (%s, %s, %s, %s, %s, true)
            ON CONFLICT (name, platform) DO NOTHING
        """, (
            item["name"],
            item["brand"],
            item["price"],
            item["platform"],
            item["url"]
        ))

        # get sneaker id
        cur.execute("""
            SELECT id FROM sneakers WHERE name=%s AND platform=%s
        """, (item["name"], item["platform"]))

        sneaker_id = cur.fetchone()[0]

        # insert price history
        cur.execute("""
            INSERT INTO price_history (sneaker_id, price)
            VALUES (%s, %s)
        """, (sneaker_id, item["price"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    data = scrape_ajio("nike")
    insert_into_db(data)
    print("Inserted:", len(data))