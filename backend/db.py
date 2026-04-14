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