from backend.db import get_connection

def detect_and_queue():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        WITH ranked AS (
            SELECT sneaker_id, price, recorded_at,
                   LAG(price) OVER (
                       PARTITION BY sneaker_id 
                       ORDER BY recorded_at ASC
                   ) AS prev_price
            FROM price_history
        )
        SELECT sneaker_id, prev_price, price
        FROM ranked
        WHERE prev_price IS NOT NULL
          AND price < prev_price
    """)

    drops = cur.fetchall()
    print("Drops found:", drops)

    inserted = 0

    for d in drops:
        try:
            sneaker_id, old_price, new_price = d
            drop_pct = ((old_price - new_price) / old_price) * 100

            print(f"Inserting: {sneaker_id}, {old_price} → {new_price}")

            cur.execute("""
                INSERT INTO alert_queue (sneaker_id, old_price, new_price, drop_pct)
                VALUES (%s, %s, %s, %s)
            """, (sneaker_id, old_price, new_price, drop_pct))

            inserted += 1

        except Exception as e:
            print("Insert failed:", e)

    conn.commit()  # 🔥 CRITICAL
    cur.close()
    conn.close()

    print("Inserted alerts:", inserted)

    return inserted