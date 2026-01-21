from fastapi import FastAPI, Request
import psycopg2
import os

app = FastAPI()

# Bazaga ulanish URL manzili (Buni Render'da sozlaymiz)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Tizim ishga tushganda jadvallarni yaratish
@app.on_event("startup")
def startup_event():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Mahsulotlar jadvali
    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        cost_price NUMERIC DEFAULT 0,
        sell_price NUMERIC DEFAULT 0,
        stock INTEGER DEFAULT 0
    )''')
    
    # 2. Buyurtmalar jadvali
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        amo_id INTEGER UNIQUE,
        product_id INTEGER REFERENCES products(id),
        status TEXT,
        amount NUMERIC,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 3. Kirim-Chiqim (Tranzaksiyalar) jadvali
    cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        amount NUMERIC,
        type TEXT, 
        category TEXT, 
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def home():
    return {"status": "Moliya tizimi onlayn", "message": "Xush kelibsiz!"}

# AmoCRM Webhook qabul qiluvchi qism
@app.post("/webhook/amocrm")
async def amocrm_webhook(request: Request):
    data = await request.form()
    print("AmoCRM ma'lumoti keldi:", data)
    return {"status": "qabul qilindi"}
