import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="pass"
    )

def search_sneakers(query):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, brand, price, platform, url
        FROM sneakers
        WHERE name ILIKE %s
        LIMIT 20
    """, (f"%{query}%",))

    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "brand": r[2],
            "price": r[3],
            "platform": r[4],
            "url": r[5],
        })

    cur.close()
    conn.close()

    return result

def get_price_history(sneaker_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT price, recorded_at
        FROM price_history
        WHERE sneaker_id=%s
        ORDER BY recorded_at
    """, (sneaker_id,))

    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "price": r[0],
            "time": str(r[1])
        })

    cur.close()
    conn.close()

    return result

def get_price_drops_simple():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT sneaker_id, price, recorded_at
        FROM price_history
        ORDER BY sneaker_id, recorded_at DESC
    """)

    rows = cur.fetchall()

    drops = []
    last_seen = {}

    for r in rows:
        sid, price, time = r

        if sid in last_seen:
            prev_price = last_seen[sid]
            if price < prev_price:
                drops.append({
                    "sneaker_id": sid,
                    "old_price": prev_price,
                    "new_price": price
                })

        last_seen[sid] = price

    cur.close()
    conn.close()

    return drops


def insert_alerts(drops):
    conn = get_connection()
    cur = conn.cursor()

    for d in drops:
        drop_pct = ((d["old_price"] - d["new_price"]) / d["old_price"]) * 100

        cur.execute("""
            INSERT INTO alert_queue (sneaker_id, old_price, new_price, drop_pct)
            VALUES (%s, %s, %s, %s)
        """, (
            d["sneaker_id"],
            d["old_price"],
            d["new_price"],
            drop_pct
        ))

    conn.commit()
    cur.close()
    conn.close()