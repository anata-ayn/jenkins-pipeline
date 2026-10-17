import os
import time

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        connect_timeout=5,
    )


def init_db(retries=10, delay=2):
    for attempt in range(1, retries + 1):
        try:
            conn = get_conn()
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            conn.close()
            print("Database siap.")
            return
        except psycopg2.OperationalError as exc:
            print(f"Database belum siap ({attempt}/{retries}): {exc}")
            time.sleep(delay)
    raise RuntimeError("Tidak bisa terhubung ke database")


@app.route("/")
def hello():
    return "Halo dari Flask + Docker + Jenkins!"


@app.route("/health")
def health():
    try:
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
        conn.close()
        return jsonify(status="ok", database=version)
    except Exception as exc:
        return jsonify(status="error", detail=str(exc)), 500


@app.route("/notes", methods=["GET"])
def list_notes():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, message, created_at FROM notes ORDER BY id DESC")
        rows = cur.fetchall()
    conn.close()
    return jsonify(
        [{"id": r[0], "message": r[1], "created_at": r[2].isoformat()} for r in rows]
    )


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="field 'message' wajib diisi"), 400
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO notes (message) VALUES (%s) RETURNING id", (message,))
        new_id = cur.fetchone()[0]
    conn.close()
    return jsonify(id=new_id, message=message), 201


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
