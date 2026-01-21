from fastapi import FastAPI, Request
import psycopg2
import os
import requests

app = FastAPI()

# Sozlamalar
DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.on_event("startup")
def startup_event():
    conn = get_db_connection()
    cur = conn.cursor()
    # Jadvallar
    cur.execute('''CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, cost_price NUMERIC, sell_price NUMERIC, stock INTEGER DEFAULT 0)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, amo_id INTEGER, product_id INTEGER, status TEXT, amount NUMERIC, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, amount NUMERIC, type TEXT, category TEXT, description TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def home():
    return {"status": "Moliya tizimi onlayn", "message": "Xush kelibsiz!"}

# --- TELEGRAM WEBHOOK ---
@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            msg = ("Salom! Moliya tizimi botiga xush kelibsiz.\n\n"
                   "💰 /kassa - Hozirgi pul holati\n"
                   "📦 /ombor - Tovar qoldiqlari\n"
                   "📉 /rashod - Chiqim kiritish")
            send_telegram_msg(chat_id, msg)
        
        elif text == "/kassa":
            send_telegram_msg(chat_id, "Hisob-kitob qilinmoqda... Hozircha kassa 0 so'm.")

    return {"status": "ok"}

# --- AMOCRM WEBHOOK ---
@app.post("/webhook/amocrm")
async def amocrm_webhook(request: Request):
    # Bu yerga AmoCRM dan ma'lumot kelganda xabar beradi
    # ADMIN_ID ni o'rniga o'zingizni chat_id yuboramiz (Start bosganingizda logsda ko'rinadi)
    return {"status": "qabul qilindi"}
