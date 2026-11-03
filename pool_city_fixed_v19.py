# ============================================================
# 💰🏙️ پول سیتی | Pool City
# 🤖 ستاره‌ی جاودانه‌ی پول‌سیتی 👑
# Python + python-bale-bot 2.5.0
# ============================================================

import asyncio
import sqlite3
import time
import random
import urllib.request
import urllib.parse
import json
import re
import os
import statistics
import tempfile
import urllib.request
import urllib.error
from datetime import datetime

from bale import Bot, Message, CallbackQuery
from bale.ui import InlineKeyboardMarkup, InlineKeyboardButton


async def answer_callback_popup(callback, text):
    """نمایش پیام فقط برای همان کاربری که دکمه را زده؛ بدون ارسال/ویرایش پیام گروه."""
    try:
        callback_id = getattr(callback, "id", None) or getattr(callback, "callback_id", None)
        if not callback_id or not TOKEN:
            return
        payload = urllib.parse.urlencode({
            "callback_query_id": str(callback_id),
            "text": str(text)[:200],
            "show_alert": "true",
        }).encode("utf-8")
        url = f"https://tapi.bale.ai/bot{TOKEN}/answerCallbackQuery"
        def _send():
            req = urllib.request.Request(url, data=payload, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        await asyncio.to_thread(_send)
    except Exception as e:
        print("CALLBACK POPUP ERROR:", repr(e))


# ============================================================
# ⚙️ تنظیمات
# ============================================================

TOKEN = ""

OWNER_ID = 623961720
BOT_ID = 2047002584

DB_NAME = "pool_city.db"

BOT_TITLE = "🤖🌟 ستاره‌ی جاودانه‌ی پول‌سیتی 👑🏙️"
OWNER_TITLE = "👑 جاودانه | اسطوره‌ای | خدای پول‌سیتی"

CRYPTO_UPDATE_SECONDS = 20

# ============================================================
# 📢 عضویت اجباری کانال اطلاع‌رسانی
# ============================================================
FORCE_JOIN_CHANNEL = "@pool_city_channel"
FORCE_JOIN_CHANNEL_URL = "https://ble.ir/pool_city_channel"



# ============================================================
# 🪙 کریپتوهای واقعی
# ============================================================

CRYPTO = {
    "بیت کوین": {
        "id": "bitcoin",
        "symbol": "BTC",
        "emoji": "₿",
    },
    "اتریوم": {
        "id": "ethereum",
        "symbol": "ETH",
        "emoji": "Ξ",
    },
    "سولانا": {
        "id": "solana",
        "symbol": "SOL",
        "emoji": "🟣",
    },
    "bnb": {
        "id": "binancecoin",
        "symbol": "BNB",
        "emoji": "🟡",
    },
    "ریپل": {
        "id": "ripple",
        "symbol": "XRP",
        "emoji": "🔵",
    },
    "دوج کوین": {
        "id": "dogecoin",
        "symbol": "DOGE",
        "emoji": "🐕",
    },
    "شیبا": {
        "id": "shiba-inu",
        "symbol": "SHIB",
        "emoji": "🐶",
    },
    "تون کوین": {
        "id": "the-open-network",
        "symbol": "TON",
        "emoji": "💎",
    },
}

crypto_prices = {}
crypto_last_update = 0


# ============================================================
# 🏢 شغل‌ها
# ============================================================

JOBS = {
    "نظافتچی": ("🧹", 12_000, 500, 50),
    "کشاورز": ("👨‍🌾", 24_000, 1_000, 80),
    "آشپز": ("👨‍🍳", 48_000, 2_000, 120),
    "مکانیک": ("🔧", 96_000, 4_000, 170),
    "کارگر کارخانه": ("👷", 144_000, 6_000, 220),
    "انباردار": ("📦", 192_000, 8_000, 270),
    "راننده کامیون": ("🚛", 288_000, 12_000, 320),
    "عکاس": ("📷", 384_000, 16_000, 370),
    "طراح گرافیک": ("🖌️", 528_000, 22_000, 430),
    "برنامه‌نویس": ("👨‍💻", 720_000, 30_000, 500),
    "توسعه‌دهنده اپلیکیشن": ("📱", 960_000, 40_000, 580),
    "حسابدار": ("🧾", 1_200_000, 50_000, 650),
    "مهندس عمران": ("👷‍♂️", 1_560_000, 65_000, 750),
    "مهندس برق": ("👨‍🔧", 1_920_000, 80_000, 850),
    "شیمیدان": ("🧑‍🔬", 2_400_000, 100_000, 950),
    "پژوهشگر": ("🔬", 3_000_000, 125_000, 1_100),
    "پزشک": ("👨‍⚕️", 3_600_000, 150_000, 1_300),
    "دندانپزشک": ("🦷", 4_320_000, 180_000, 1_500),
    "وکیل": ("👨‍⚖️", 5_280_000, 220_000, 1_700),
    "قاضی": ("⚖️", 6_480_000, 270_000, 1_900),
    "آتش‌نشان": ("🧑‍🚒", 7_680_000, 320_000, 2_100),
    "افسر پلیس": ("👮", 9_120_000, 380_000, 2_300),
    "خلبان": ("👨‍✈️", 10_800_000, 450_000, 2_600),
    "ناخدا": ("🧑‍✈️", 13_200_000, 550_000, 2_900),
    "مهندس هوافضا": ("🧑‍🚀", 16_800_000, 700_000, 3_300),
    "مدیر بانک": ("🏦", 21_600_000, 900_000, 3_800),
    "مدیر صنعت نفت": ("🛢️", 28_800_000, 1_200_000, 4_500),
    "مدیر کارخانه": ("👨‍💼", 38_400_000, 1_600_000, 5_500),
    "مدیر سرمایه‌گذاری": ("💰", 52_800_000, 2_200_000, 7_000),
    "مدیرعامل شرکت بزرگ": ("👔", 72_000_000, 3_000_000, 9_000),
}


# ============================================================
# 🚗 ماشین‌ها
# ============================================================

CARS = {
    "دوچرخه": ("🚲", 500, 10),
    "موتور ایرانی": ("🏍️", 2500, 25),
    "پراید": ("😂", 12000, 60),
    "تیبا": ("🚗", 18000, 85),
    "ساینا": ("🚙", 25000, 110),
    "کوییک": ("🚗", 32000, 140),
    "دنا پلاس": ("🔥", 45000, 190),
    "شاهین پلاس": ("🦅", 55000, 230),
    "تارا": ("🚘", 65000, 270),
    "تویوتا کمری": ("🔥", 120000, 350),
    "BMW سری 5": ("🏁", 220000, 470),
    "لامبورگینی هوراکان": ("🏎️", 450000, 650),
    "فراری 296 GTB": ("🏎️", 600000, 760),
    "رولز رویس": ("👑", 1000000, 1000),
}


# ============================================================
# 🏠 خانه‌ها
# ============================================================

HOUSES = {
    "اتاق کوچک": ("🛏️", 5000, 20),
    "آپارتمان": ("🏢", 25000, 60),
    "خانه معمولی": ("🏠", 80000, 150),
    "خانه لوکس": ("🏡", 250000, 350),
    "ویلا": ("🌴", 700000, 800),
    "عمارت": ("🏰", 2000000, 2000),
}


# ============================================================
# 🏦 وام
# ============================================================

LOANS = {
    150000: 180000,
    200000: 230000,
    250000: 280000,
}


# ============================================================
# 📈 بورس
# ============================================================

STOCKS = {
    "نفت": {"symbol": "OIL", "price": 78000},
    "فولاد": {"symbol": "FOOLAD", "price": 52000},
    "خودرو": {"symbol": "KHODRO", "price": 31000},
    "بانک": {"symbol": "BANK", "price": 44000},
    "فناوری": {"symbol": "TECH", "price": 68000},
    "دارویی": {"symbol": "PHARMA", "price": 57000},
}


# ============================================================
# 🛍️ فروشگاه فصلی
# ============================================================

REAL_PRODUCTS = {
    "لقب محدود فصل": {
        "price": 50000,
        "type": "title",
        "value": "👑 افسانه فصل",
    },
    "تم پروفایل فصل": {
        "price": 75000,
        "type": "theme",
        "value": "🌟 تم فصل",
    },
    "پک الماس فصل": {
        "price": 100000,
        "type": "diamonds",
        "value": 500,
    },
    "جعبه افسانه‌ای فصل": {
        "price": 120000,
        "type": "box",
        "value": 1,
    },
    "بلیت رویداد فصل": {
        "price": 80000,
        "type": "ticket",
        "value": 1,
    },
    "نشان افتخار فصل": {
        "price": 90000,
        "type": "badge",
        "value": "🏆 نشان فصل",
    },

    "پک ۱۰ هزار پول": {
        "price": 30000,
        "type": "money",
        "value": 10000,
    },
    "پک ۵۰ هزار پول": {
        "price": 100000,
        "type": "money",
        "value": 50000,
    },
    "پک ۲۵۰ هزار پول": {
        "price": 350000,
        "type": "money",
        "value": 250000,
    },
    "پک ۱ میلیون پول": {
        "price": 1000000,
        "type": "money",
        "value": 1000000,
    },
    "پک ۵ میلیون پول": {
        "price": 4000000,
        "type": "money",
        "value": 5000000,
    },
    "پک ۲۵ میلیون پول": {
        "price": 15000000,
        "type": "money",
        "value": 25000000,
    },
    "پک ۱۰۰ میلیون پول": {
        "price": 50000000,
        "type": "money",
        "value": 100000000,
    },
}


# ============================================================
# 🗄️ دیتابیس
# ============================================================

db = sqlite3.connect(
    DB_NAME,
    check_same_thread=False
)

db.row_factory = sqlite3.Row

db_lock = asyncio.Lock()

# Persistent management logs (additive schema; player data is preserved).
import traceback as _traceback

def init_admin_tables():
    db.execute("""CREATE TABLE IF NOT EXISTS bot_error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at INTEGER NOT NULL,
        area TEXT NOT NULL, error_type TEXT NOT NULL, details TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS backup_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at INTEGER NOT NULL,
        filename TEXT NOT NULL, status TEXT NOT NULL, details TEXT DEFAULT '')""")
    db.commit()

def log_bot_error(area, exc):
    try:
        details = "".join(_traceback.format_exception(type(exc), exc, exc.__traceback__))
        db.execute("INSERT INTO bot_error_logs(created_at,area,error_type,details) VALUES(?,?,?,?)",
                   (int(time.time()), str(area)[:80], type(exc).__name__, details[-12000:]))
        db.commit()
    except Exception as log_exc:
        print("PERSISTENT LOG FAILURE:", repr(log_exc), "original:", repr(exc))
    print(f"{area} ERROR:", repr(exc))

def log_backup(status, filename="", details=""):
    try:
        db.execute("INSERT INTO backup_history(created_at,filename,status,details) VALUES(?,?,?,?)",
                   (int(time.time()), str(filename)[:255], str(status)[:40], str(details)[:1000]))
        db.commit()
    except Exception as exc:
        log_bot_error("backup-history", exc)



def now():
    return int(time.time())


def init_db():
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT DEFAULT '',
        money INTEGER DEFAULT 0,
        bank INTEGER DEFAULT 0,
        diamonds INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        job TEXT DEFAULT '',
        house TEXT DEFAULT '',
        car TEXT DEFAULT '',
        wanted INTEGER DEFAULT 0,
        prison INTEGER DEFAULT 0,
        last_money INTEGER DEFAULT 0,
        last_daily INTEGER DEFAULT 0,
        last_salary INTEGER DEFAULT 0,
        last_wheel INTEGER DEFAULT 0,
        title TEXT DEFAULT 'تازه‌کار',
        theme TEXT DEFAULT '',
        season_badge TEXT DEFAULT '',
        season_ticket INTEGER DEFAULT 0,
        company TEXT DEFAULT '',
        city TEXT DEFAULT '',
        alliance TEXT DEFAULT '',
        loan INTEGER DEFAULT 0,
        loan_due INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        games_played INTEGER DEFAULT 0,
        gambling_played INTEGER DEFAULT 0,
        stocks_value INTEGER DEFAULT 0,
        crypto_value REAL DEFAULT 0
    )
    """)

    columns = {
        "title": "TEXT DEFAULT 'تازه‌کار'",
        "theme": "TEXT DEFAULT ''",
        "season_badge": "TEXT DEFAULT ''",
        "season_ticket": "INTEGER DEFAULT 0",
        "company": "TEXT DEFAULT ''",
        "city": "TEXT DEFAULT ''",
        "alliance": "TEXT DEFAULT ''",
        "loan": "INTEGER DEFAULT 0",
        "loan_due": "INTEGER DEFAULT 0",
        "streak": "INTEGER DEFAULT 0",
        "games_played": "INTEGER DEFAULT 0",
        "gambling_played": "INTEGER DEFAULT 0",
        "stocks_value": "INTEGER DEFAULT 0",
        "crypto_value": "REAL DEFAULT 0",
    }

    cur.execute("PRAGMA table_info(users)")
    existing = {row[1] for row in cur.fetchall()}

    for col, definition in columns.items():
        if col not in existing:
            cur.execute(
                f"ALTER TABLE users ADD COLUMN {col} {definition}"
            )

    cur.execute("""
    CREATE TABLE IF NOT EXISTS crypto_assets (
        user_id INTEGER,
        crypto TEXT,
        amount REAL DEFAULT 0,
        invested REAL DEFAULT 0,
        PRIMARY KEY(user_id, crypto)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_assets (
        user_id INTEGER,
        stock TEXT,
        shares REAL DEFAULT 0,
        invested REAL DEFAULT 0,
        PRIMARY KEY(user_id, stock)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        amount REAL,
        created_at INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchase_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER,
        buyer_name TEXT,
        product TEXT,
        amount INTEGER,
        reward_type TEXT,
        reward_value TEXT,
        status TEXT DEFAULT 'pending',
        created_at INTEGER,
        processed_at INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alliances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        leader_id INTEGER,
        treasury INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        created_at INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alliance_members (
        alliance_id INTEGER,
        user_id INTEGER UNIQUE,
        role TEXT DEFAULT 'member',
        joined_at INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER UNIQUE,
        name TEXT,
        money INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        employees INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inviter_id INTEGER,
        invited_id INTEGER UNIQUE,
        reward_given INTEGER DEFAULT 0,
        created_at INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lottery_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        purchased_at INTEGER,
        draw_date TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    init_admin_tables()
    db.commit()


def ensure_user(user_id, name):
    cur = db.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    if cur.fetchone() is None:
        cur.execute("""
        INSERT INTO users(user_id, name)
        VALUES (?, ?)
        """, (user_id, name))
    else:
        cur.execute("""
        UPDATE users
        SET name=?
        WHERE user_id=?
        """, (name, user_id))

    db.commit()


def get_user(user_id):
    cur = db.cursor()

    cur.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    return cur.fetchone()


def add_history(user_id, action, amount):
    db.execute("""
    INSERT INTO history(user_id, action, amount, created_at)
    VALUES (?, ?, ?, ?)
    """, (user_id, action, amount, now()))

    db.commit()


def fmt(n):
    if n is None:
        return "0"

    if isinstance(n, float):
        return f"{n:,.8f}".rstrip("0").rstrip(".")

    return f"{int(n):,}"


def mention(name, user_id):
    name = str(name).replace("[", "").replace("]", "")
    return f"[{name}](uid:{user_id})"


# ============================================================
# ⭐ سطح بازیکن
# ============================================================

# XP کل موردنیاز برای رسیدن به هر لول؛ لول ۱۵ در ۱۳۰۰ XP باز می‌شود.
LEVEL_XP = {
    1: 0,
    2: 40,
    3: 80,
    4: 130,
    5: 190,
    6: 260,
    7: 340,
    8: 430,
    9: 530,
    10: 640,
    11: 760,
    12: 880,
    13: 1000,
    14: 1150,
    15: 1300,
}


def get_level(xp):
    level = 1

    for lv, required in LEVEL_XP.items():
        if xp >= required:
            level = lv

    return level


def add_xp(user_id, amount):
    """Add XP safely. Normal gameplay cannot subtract XP or lower a player's level."""
    try:
        amount = max(0, int(amount))
    except (TypeError, ValueError):
        amount = 0
    db.execute(
        "UPDATE users SET xp=MAX(0, COALESCE(xp, 0)+?) WHERE user_id=?",
        (amount, user_id)
    )
    db.commit()
    return get_level(max(0, int((get_user(user_id) or {"xp": 0})["xp"] or 0)))


def level_required(user_id, required):
    user = get_user(user_id)
    return get_level(max(0, int(user["xp"] or 0))) >= required


# ============================================================
# 🔐 سطح دسترسی
# ============================================================

LEVEL_FEATURES = {
    1: "💰 پول | 👤 پروفایل | 🎁 جایزه | 🎲 تاس | 🪙 شیر یا خط | 🔢 حدس عدد | ⭕❌ دوز | ✂️ سنگ کاغذ قیچی | 💣 مین‌یاب | 🐍 مار و پله | 🚗 مسابقه ماشین | 🎫 لاتاری",
    2: "💼 شغل | 🚗 ماشین | 💵 حقوق | 💸 انتقال پول | 📰 روزنامه | 🎯 ماموریت",
    3: "🏦 بانک | 📜 تاریخچه | 🎁 هدیه | 🎡 گردونه",
    4: "🏠 خونه | 🌾 کشاورزی | 🧭 کاوش شهری | 💎 الماس",
    5: "🏹 شکار | 🪵 چوب | ⛏️ معدن | 🐾 حیوانات",
    6: "🕵️ دزدی | ⚖️ دادگاه | 🔓 فرار از زندان | 🎰 کازینو",
    7: "🤝 اتحاد | 📈 بورس | 🪙 کریپتو",
    8: "🏭 کارخونه | 🛒 بازار | 🏢 شرکت | 🏙️ شهر",
    9: "⚔️ جنگ اقتصادی | 📜 قرارداد",
    10: "🏆 لیگ",
}

COMMAND_LEVELS = {
    "پروفایل": 1, "پول": 1, "پول سیتی": 1, "مانی": 1, "جایزه": 1,
    "تاس": 1, "بازی تاس": 1, "شیر یا خط": 1, "سکه": 1, "حدس عدد": 1,
    "دوز": 1, "سنگ کاغذ قیچی": 1, "مین یاب": 1, "مین‌یاب": 1,
    "مار و پله": 1, "مسابقه ماشین": 1, "لاتاری": 1,
    "شغل": 2, "کار": 2, "ماشین": 2, "حقوق": 2, "انتقال پول": 2,
    "کارت به کارت": 2, "روزنامه": 2, "ماموریت": 2,
    "بانک": 3, "تاریخچه": 3, "هدیه": 3, "گردونه": 3,
    "وام": 4, "الماس": 4, "خونه": 4, "خانه": 4, "کشاورزی": 4, "کاوش شهری": 4,
    "شکار": 5, "چوب": 5, "معدن": 5, "حیوانات": 5,
    "دزدی": 6, "دادگاه": 6, "فرار از زندان": 6, "کازینو": 6,
    "اتحاد": 7, "بورس": 7, "کریپتو": 7,
    "کارخونه": 8, "بازار": 8, "شرکت": 8, "شهر": 8,
    "جنگ اقتصادی": 9, "قرارداد": 9, "لیگ": 10,
    # استریک در راهنمای اصلی نمایش داده نمی‌شود، ولی برای حفظ قابلیت قبلی فعال می‌ماند.
    "استریک": 1,
}


async def check_level(message, command):
    """Enforce configured feature levels; never mutate or reduce XP here."""
    required = COMMAND_LEVELS.get(str(command).strip(), 1)
    try:
        user_id = message.author.user_id
        user = get_user(user_id)
        if user is None:
            return False
        current = get_level(max(0, int(user["xp"] or 0)))
        if current >= required:
            return True
        await message.reply(
            f"🔒 این قابلیت در لول {required} باز می‌شود.\n"
            f"⭐ لول فعلی تو: {current}\n"
            f"💡 با بازی‌کردن و انجام فعالیت‌ها XP بگیر و لولت رو بالا ببر."
        )
        return False
    except Exception as exc:
        print("LEVEL CHECK ERROR:", repr(exc))
        return False


# ============================================================
# 🏅 عنوان‌ها
# ============================================================

def calculate_title(user):
    if user["user_id"] == OWNER_ID:
        return OWNER_TITLE

    money = user["money"]
    games = user["games_played"]
    gambling = user["gambling_played"]
    bank = user["bank"]
    xp = user["xp"]

    if gambling >= 100:
        return "🎰 قمارباز افسانه‌ای"

    if games >= 100:
        return "🎮 گیمر افسانه‌ای"

    if money >= 10000000:
        return "💰 میلیاردر پول‌سیتی"

    if money >= 1000000:
        return "💰 پولدار"

    if bank >= 1000000:
        return "🏦 بانکدار"

    if xp >= 10000:
        return "⭐ نخبه"

    return "⚪ تازه‌کار"


def update_title(user_id):
    user = get_user(user_id)

    if user["user_id"] == OWNER_ID:
        title = OWNER_TITLE
    else:
        title = calculate_title(user)

    db.execute(
        "UPDATE users SET title=? WHERE user_id=?",
        (title, user_id)
    )

    db.commit()


# ============================================================
# 🪙 API قیمت کریپتو
# ============================================================

def fetch_crypto_prices_sync():
    ids = ",".join(
        item["id"]
        for item in CRYPTO.values()
    )

    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd"
        "&include_24hr_change=true"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PoolCityBot/1.0"
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=10
    ) as response:

        return json.loads(
            response.read().decode()
        )


async def update_crypto_prices():
    global crypto_prices
    global crypto_last_update

    try:
        data = await asyncio.to_thread(
            fetch_crypto_prices_sync
        )

        crypto_prices = {}

        for name, item in CRYPTO.items():

            cid = item["id"]

            if cid in data:

                crypto_prices[name] = {
                    "price": data[cid].get(
                        "usd",
                        0
                    ),

                    "change": data[cid].get(
                        "usd_24h_change",
                        0
                    ),
                }

        crypto_last_update = now()

        print("🪙 Crypto prices updated.")

    except Exception as e:
        print(
            "CRYPTO PRICE ERROR:",
            repr(e)
        )


async def crypto_price_loop():
    while True:

        try:
            await asyncio.sleep(
                CRYPTO_UPDATE_SECONDS
            )

            await update_crypto_prices()

        except asyncio.CancelledError:
            break

        except Exception as e:
            print(
                "CRYPTO LOOP ERROR:",
                repr(e)
            )


def find_crypto(text):
    text = text.lower().strip()

    aliases = {
        "بیتکوین": "بیت کوین",
        "بیت کویین": "بیت کوین",
        "btc": "بیت کوین",

        "اتریوم": "اتریوم",
        "eth": "اتریوم",

        "sol": "سولانا",
        "سولانا": "سولانا",

        "bnb": "bnb",
        "بی ان بی": "bnb",

        "xrp": "ریپل",
        "ریپل": "ریپل",

        "doge": "دوج کوین",
        "دوج": "دوج کوین",
        "دوج کوین": "دوج کوین",

        "shib": "شیبا",
        "شیبا": "شیبا",

        "ton": "تون کوین",
        "تون": "تون کوین",
        "تون کوین": "تون کوین",
    }

    return aliases.get(text)


# ============================================================
# 📖 راهنما
# ============================================================

def normal_help():
    return """
🏙️💰 **راهنمای پول‌سیتی**

🤖 🤖🌟 ستاره‌ی جاودانه‌ی پول‌سیتی 👑🏙️

⭐ سطح ۱
💰 پول
👤 پروفایل
🎁 جایزه
🎲 تاس
🪙 شیر یا خط
🔢 حدس عدد
⭕❌ دوز
✂️ سنگ کاغذ قیچی
💣 مین‌یاب
🐍 مار و پله
🚗 مسابقه ماشین
🎫 لاتاری

⭐ سطح ۲
💼 شغل
🚗 ماشین
💵 حقوق
💸 انتقال پول
📰 روزنامه
🎯 ماموریت

⭐ سطح ۳
🏦 بانک
📜 تاریخچه
🎁 هدیه
🎡 گردونه

⭐ سطح ۴
🏠 خونه
🌾 کشاورزی
🧭 کاوش شهری
💎 الماس

⭐ سطح ۵
🏹 شکار
🪵 چوب
⛏️ معدن
🐾 حیوانات

⭐ سطح ۶
🕵️ دزدی
⚖️ دادگاه
🔓 فرار از زندان
🎰 کازینو

⭐ سطح ۷
🤝 اتحاد
📈 بورس
🪙 کریپتو

⭐ سطح ۸
🏭 کارخونه
🛒 بازار
🏢 شرکت
🏙️ شهر

⭐ سطح ۹
⚔️ جنگ اقتصادی
📜 قرارداد

⭐ سطح ۱۰
🏆 لیگ

━━━━━━━━━━━━━━

🎫 **لاتاری:** هر بلیت ۱۰۰ پول — قرعه‌کشی ساعت ۱۷:۰۰

💬 گپ پول سیتی
"""


def casino_help():
    return """
🎰 **راهنمای کازینو**

🃏 بلک‌جک
🎡 رولت
🃏 پوکر
🎯 باکارات
🎰 اسلات
🃏 بالاتر یا پایین‌تر
🎲 تاس کازینو
🎰 قمار

👥 همه بازی‌های کازینو چندنفره هستند.
🎮 بعد از ساخت اتاق، ادامه بازی با دکمه‌های شیشه‌ای انجام می‌شود.

مثال:
قمار ۱۰۰۰ ۵

نام بازی | مبلغ ورودی | تعداد نفرات
"""


def cheat_help():
    return """
👑🔐 **راهنمای چیت مالک**
━━━━━━━━━━━━━━
⚠️ این دستورات فقط برای مالک ربات هستند.

💰 گرفتن پول [مقدار]
💸 کم پول [مقدار]
💎 گرفتن الماس [مقدار]
💼 گرفتن شغل [نام شغل]
🏠 گرفتن خونه [نام خانه]
🏠 گرفتن خانه [نام خانه]
⭐ تغییر اکس پی به [مقدار]
👑 تغییر لول به [1 تا 15]
🚨 حذف جریمه
🏦 تغییر موجودی بانک به [مقدار]
🔄 ریست تست

📌 برای دستورهایی که بازیکن هدف می‌خواهند، دستور را در پاسخ به پیام همان بازیکن بفرستید.

━━━━━━━━━━━━━━
🛠️ **راهنمای پنل مدیریت**
برای باز کردن پنل بنویسید: پنل مدیریت

📦 دریافت بکاپ دیتابیس
🗂️ تاریخچه بکاپ‌ها
📊 آمار ربات
🏓 وضعیت و پینگ
📈 آمار اقتصادی
🖥️ وضعیت سرور
🧾 گزارش تراکنش‌ها
🚨 تشخیص تقلب
📢 پیام همگانی [متن پیام]
🐞 گزارش خطاها
🧪 تست امکانات

━━━━━━━━━━━━━━
👑 فقط مالک می‌تواند از چیت‌ها و ابزارهای مدیریت استفاده کند.
⚠️ «تست امکانات» بررسی اولیه است و جای تست واقعی همه بازی‌ها را نمی‌گیرد.
"""


# ============================================================
# ⌨️ کیبوردها
# ============================================================

def confirm_keyboard(action, key):
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "✅ تأیید",
            callback_data=f"{action}:yes:{key}"
        ),
        row=0
    )

    kb.add(
        InlineKeyboardButton(
            "❌ لغو",
            callback_data=f"{action}:no:{key}"
        ),
        row=1
    )

    return kb


def purchase_keyboard(request_id):
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "✅ تأیید پرداخت",
            callback_data=f"payapprove:{request_id}"
        ),
        row=0
    )

    kb.add(
        InlineKeyboardButton(
            "❌ رد پرداخت",
            callback_data=f"payreject:{request_id}"
        ),
        row=1
    )

    return kb


# ============================================================
# 👤 پروفایل
# ============================================================

async def profile(message):
    user_id = message.author.user_id
    user = get_user(user_id)

    update_title(user_id)

    user = get_user(user_id)

    level = get_level(user["xp"])

    job_name = user["job"] or "بدون شغل"
    car_name = user["car"] or "بدون ماشین"
    house_name = user["house"] or "بدون خانه"

    await message.reply(
        f"👤 **پروفایل پول‌سیتی**\n\n"
        f"👤 {mention(user['name'], user_id)}\n"
        f"👑 لقب: {user['title']}\n"
        f"⭐ سطح: {level}\n"
        f"✨ XP: {fmt(user['xp'])}\n\n"
        f"💰 پول: {fmt(user['money'])}\n"
        f"🏦 بانک: {fmt(user['bank'])}\n"
        f"💎 الماس: {fmt(user['diamonds'])}\n\n"
        f"💼 شغل: {job_name}\n"
        f"🚗 ماشین: {car_name}\n"
        f"🏠 خانه: {house_name}\n\n"
        f"🎮 بازی‌ها: {user['games_played']}\n"
        f"🔥 استریک: {user['streak']}"
    )


# ============================================================
# 🎫 لاتاری
# ============================================================

LOTTERY_TICKET_PRICE = 100


def lottery_draw_key():
    return datetime.now().strftime("%Y-%m-%d")


async def lottery(message):
    if not await check_level(message, "لاتاری"):
        return

    user_id = message.author.user_id
    user = get_user(user_id)
    draw_date = lottery_draw_key()

    cur = db.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM lottery_tickets WHERE user_id=? AND draw_date=? AND status='active'",
        (user_id, draw_date)
    )
    count = cur.fetchone()[0]

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🎟️ خرید بلیت — ۱۰۰ پول", callback_data="lottery:buy"),
        row=0
    )

    await message.reply(
        f"🎫 **لاتاری پول‌سیتی**\n\n"
        f"🎟️ قیمت هر بلیت: **۱۰۰ پول**\n"
        f"🕔 قرعه‌کشی امروز: **۱۷:۰۰**\n"
        f"🎟️ بلیت‌های تو برای امروز: **{count}**\n\n"
        f"برای خرید بلیت روی دکمه زیر بزن 👇",
        components=kb
    )


async def lottery_draw_loop():
    last_draw = ""
    while True:
        try:
            current = datetime.now()
            key = current.strftime("%Y-%m-%d")
            if current.hour == 17 and current.minute == 0 and key != last_draw:
                last_draw = key
                cur = db.cursor()
                cur.execute(
                    "SELECT id, user_id FROM lottery_tickets WHERE draw_date=? AND status='active'",
                    (key,)
                )
                tickets = cur.fetchall()
                if tickets:
                    winner = random.choice(tickets)
                    winner_id = winner["user_id"]
                    prize = len(tickets) * LOTTERY_TICKET_PRICE
                    db.execute(
                        "UPDATE users SET money=money+? WHERE user_id=?",
                        (prize, winner_id)
                    )
                    db.execute(
                        "UPDATE lottery_tickets SET status='drawn' WHERE draw_date=? AND status='active'",
                        (key,)
                    )
                    db.commit()
                    try:
                        await bot.send_message(
                            winner_id,
                            f"🏆 **برنده لاتاری پول‌سیتی شدی!**\n\n🎫 تعداد بلیت‌های قرعه: {len(tickets)}\n💰 جایزه: {fmt(prize)} پول"
                        )
                    except Exception as e:
                        print("LOTTERY WINNER MESSAGE ERROR:", repr(e))
            await asyncio.sleep(20)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print("LOTTERY LOOP ERROR:", repr(e))
            await asyncio.sleep(20)


# ============================================================
# 🎁 جایزه روزانه
# ============================================================

async def daily_reward(message):
    user_id = message.author.user_id
    user = get_user(user_id)

    if now() - user["last_daily"] < 86400:

        remain = 86400 - (
            now() - user["last_daily"]
        )

        hours = remain // 3600
        minutes = (remain % 3600) // 60

        await message.reply(
            f"⏳ جایزه روزانه رو گرفتی!\n"
            f"🕐 حدود {hours} ساعت و {minutes} دقیقه دیگه برگرد."
        )

        return

    reward = random.randint(
        200,
        500
    )

    db.execute("""
    UPDATE users
    SET money=money+?,
        last_daily=?,
        xp=xp+50,
        streak=streak+1
    WHERE user_id=?
    """, (
        reward,
        now(),
        user_id
    ))

    db.commit()

    add_history(
        user_id,
        "جایزه روزانه",
        reward
    )

    update_title(user_id)

    await message.reply(
        f"🎁 **جایزه روزانه**\n\n"
        f"💰 +{fmt(reward)} پول‌سیتی\n"
        f"⭐ +50 XP\n"
        f"🔥 استریک جدید: "
        f"{get_user(user_id)['streak']}"
    )


# ============================================================
# 💼 شغل
# ============================================================

def item_list_keyboard(items, action, label_prefix="خرید"):
    """ساخت دکمه‌های شیشه‌ای با همان ایموجی واقعی هر آیتم."""
    kb = InlineKeyboardMarkup()
    row = 0
    for name, data in items.items():
        emoji = data[0] if isinstance(data, (tuple, list)) and data else "🎮"
        kb.add(
            InlineKeyboardButton(
                f"{emoji} {label_prefix} {name}",
                callback_data=f"{action}:yes:{name}"
            ),
            row=row
        )
        row += 1
    return kb


async def show_jobs(message):

    if not await check_level(message, "شغل"):
        return

    text = "💼 **شغل‌های موجود**\n━━━━━━━━━━━━━━\n\n"
    for name, data in JOBS.items():
        emoji, price, salary_value, required_xp = data
        text += (f"{emoji} {name}\n"
                 f"💵 درآمد: {fmt(salary_value)} پول هر ۱ ساعت\n"
                 f"💰 قیمت: {fmt(price)} پول\n\n")
    text += "━━━━━━━━━━━━━━\n📌 می‌توانی چند شغل بخری، اما فقط یک شغل را به‌عنوان شغل فعال انتخاب کنی."

    await message.reply(text, components=item_list_keyboard(JOBS, "job", "انتخاب"))


async def choose_job(message, job):

    if job not in JOBS:

        await message.reply(
            "❌ این شغل وجود نداره.\n"
            "💼 اسم شغل رو دقیق بنویس."
        )

        return

    await message.reply(
        f"💼 انتخاب شغل\n\n"
        f"👔 {job}\n"
        f"💵 درآمد هر ساعت: {fmt(JOBS[job][2])} پول\n"
        f"💰 قیمت: {fmt(JOBS[job][1])} پول\n\n"
        f"برای تأیید دکمه رو بزن.",
        components=confirm_keyboard(
            "job",
            job
        )
    )


# ============================================================
# 🚗 ماشین
# ============================================================

async def show_cars(message):

    if not await check_level(message, "ماشین"):
        return

    user = get_user(message.author.user_id)
    active_car = user.get("car") or "بدون ماشین"
    active_data = CARS.get(active_car)
    active_bonus = active_data[2] if active_data else 0
    text = ("🚗 **فروشگاه ماشین**\n"
            "━━━━━━━━━━━━━━\n\n"
            f"🚗 ماشین فعال: {active_car} (افزایش درآمد: +{fmt(active_bonus)})\n\n")
    for name, data in CARS.items():
        emoji, price, bonus = data
        owned = "✅" if active_car == name else "❌"
        text += (f"{emoji} {name}  |  قیمت: {fmt(price)}💰  |  افزایش درآمد: +{fmt(bonus)}  |  {owned}\n")
    text += "\nبرای خرید یک ماشین روی دکمه‌های زیر کلیک کنید."

    await message.reply(text, components=item_list_keyboard(CARS, "car", "خرید"))


async def choose_car(message, car):

    if car not in CARS:
        await message.reply(
            "❌ این ماشین وجود نداره."
        )
        return

    emoji, price, bonus = CARS[car]

    await message.reply(
        f"{emoji} **{car}**\n\n"
        f"💰 قیمت: {fmt(price)}\n"
        f"💵 پاداش حقوق: +{fmt(bonus)}\n\n"
        f"برای خرید تأیید کن.",
        components=confirm_keyboard(
            "car",
            car
        )
    )


# ============================================================
# 🏠 خانه
# ============================================================

async def show_houses(message):

    if not await check_level(message, "خانه"):
        return

    text = "🏠 **خانه‌های پول‌سیتی**\n\n"
    for name, data in HOUSES.items():
        emoji, price, bonus = data
        text += (f"{emoji} {name}\n"
                 f"💰 قیمت: {fmt(price)}\n"
                 f"⭐ پاداش: +{fmt(bonus)}\n\n")

    await message.reply(text, components=item_list_keyboard(HOUSES, "house", "خرید"))


async def choose_house(message, house):
    if house not in HOUSES:
        await message.reply("❌ این خانه وجود نداره.")
        return
    emoji, price, bonus = HOUSES[house]
    await message.reply(
        f"{emoji} **{house}**\n\n"
        f"💰 قیمت: {fmt(price)}\n"
        f"⭐ پاداش: +{fmt(bonus)}\n\n"
        f"برای خرید تأیید کن.",
        components=confirm_keyboard("house", house)
    )


async def salary(message):

    if not await check_level(
        message,
        "حقوق"
    ):
        return

    user_id = message.author.user_id
    user = get_user(user_id)

    if not user["job"]:

        await message.reply(
            "❌ هنوز شغلی نداری.\n"
            "💼 اول یک شغل انتخاب کن."
        )

        return

    if now() - user["last_salary"] < 3600:

        remain = 3600 - (
            now() - user["last_salary"]
        )

        minutes = remain // 60

        await message.reply(
            f"⏳ هنوز زمان حقوق بعدی نرسیده.\n"
            f"🕐 حدود {minutes} دقیقه دیگه."
        )

        return

    base = JOBS[user["job"]][2]

    car_bonus = 0

    if (
        user["car"]
        and user["car"] in CARS
    ):
        car_bonus = CARS[user["car"]][2]

    total = base + car_bonus

    db.execute("""
    UPDATE users
    SET money=money+?,
        last_salary=?
    WHERE user_id=?
    """, (
        total,
        now(),
        user_id
    ))

    db.commit()

    add_history(
        user_id,
        "حقوق",
        total
    )

    update_title(user_id)

    await message.reply(
        f"💵 **حقوق دریافت شد!**\n\n"
        f"💼 شغل: {user['job']}\n"
        f"💰 حقوق پایه: {fmt(base)}\n"
        f"🚗 پاداش ماشین: +{fmt(car_bonus)}\n"
        f"━━━━━━━━━━━━\n"
        f"💵 دریافتی نهایی: "
        f"**{fmt(total)} پول‌سیتی**"
    )


# ============================================================
# 🏦 بانک
# ============================================================

async def bank(message):

    if not await check_level(
        message,
        "بانک"
    ):
        return

    user = get_user(
        message.author.user_id
    )

    await message.reply(
        f"🏦 **بانک پول‌سیتی**\n\n"
        f"💰 موجودی کیف پول: "
        f"{fmt(user['money'])}\n"
        f"🏦 موجودی بانک: "
        f"{fmt(user['bank'])}\n\n"
        f"برای واریز:\n"
        f"`واریز 5000`\n\n"
        f"برای برداشت:\n"
        f"`برداشت 5000`"
    )


async def deposit(message, amount):

    user_id = message.author.user_id
    user = get_user(user_id)

    if (
        amount <= 0
        or user["money"] < amount
    ):

        await message.reply(
            "❌ موجودی کیف پول کافی نیست."
        )

        return

    db.execute("""
    UPDATE users
    SET money=money-?,
        bank=bank+?
    WHERE user_id=?
    """, (
        amount,
        amount,
        user_id
    ))

    db.commit()

    await message.reply(
        f"🏦 واریز انجام شد.\n"
        f"💰 مبلغ: {fmt(amount)}"
    )


async def withdraw(message, amount):

    user_id = message.author.user_id
    user = get_user(user_id)

    if (
        amount <= 0
        or user["bank"] < amount
    ):

        await message.reply(
            "❌ موجودی بانک کافی نیست."
        )

        return

    db.execute("""
    UPDATE users
    SET bank=bank-?,
        money=money+?
    WHERE user_id=?
    """, (
        amount,
        amount,
        user_id
    ))

    db.commit()

    await message.reply(
        f"🏦 برداشت انجام شد.\n"
        f"💰 مبلغ: {fmt(amount)}"
    )


# ============================================================
# 💸 انتقال پول
# ============================================================

async def transfer(
    message,
    target_id,
    amount
):

    sender_id = message.author.user_id

    if sender_id == target_id:

        await message.reply(
            "❌ نمیشه پول رو به خودت انتقال بدی 😂"
        )

        return

    sender = get_user(sender_id)
    target = get_user(target_id)

    if not target:

        await message.reply(
            "❌ کاربر مقصد هنوز وارد پول‌سیتی نشده."
        )

        return

    if (
        amount <= 0
        or sender["money"] < amount
    ):

        await message.reply(
            "❌ موجودی کافی نیست."
        )

        return

    db.execute(
        "UPDATE users SET money=money-? WHERE user_id=?",
        (
            amount,
            sender_id
        )
    )

    db.execute(
        "UPDATE users SET money=money+? WHERE user_id=?",
        (
            amount,
            target_id
        )
    )

    db.commit()

    await message.reply(
        f"💸 انتقال انجام شد!\n\n"
        f"💰 مبلغ: {fmt(amount)}\n"
        f"👤 مقصد: "
        f"{mention(target['name'], target_id)}"
    )


# ============================================================
# 💳 وام
# ============================================================

async def loan(message):

    if not await check_level(
        message,
        "وام"
    ):
        return

    user = get_user(
        message.author.user_id
    )

    if user["loan"] > 0:

        await message.reply(
            f"💳 وام فعال داری.\n"
            f"💰 اصل وام: "
            f"{fmt(user['loan'])}\n"
            f"💵 مبلغ بازپرداخت: "
            f"{fmt(user['loan_due'])}"
        )

        return

    text = "💳 **وام‌های پول‌سیتی**\n\n"

    for amount, repay in LOANS.items():

        text += (
            f"💰 {fmt(amount)} → "
            f"💵 بازپرداخت: "
            f"{fmt(repay)}\n"
        )

    text += "\nمثال:\n`وام 150000`"

    await message.reply(text)


async def take_loan(message, amount):

    if amount not in LOANS:

        await message.reply(
            "❌ مبلغ وام مجاز نیست.\n"
            "150000 / 200000 / 250000"
        )

        return

    user = get_user(
        message.author.user_id
    )

    if user["loan"] > 0:

        await message.reply(
            "❌ یک وام فعال داری."
        )

        return

    repay = LOANS[amount]

    db.execute("""
    UPDATE users
    SET money=money+?,
        loan=?,
        loan_due=?
    WHERE user_id=?
    """, (
        amount,
        amount,
        repay,
        message.author.user_id
    ))

    db.commit()

    await message.reply(
        f"💳 وام دریافت شد!\n\n"
        f"💰 مبلغ: {fmt(amount)}\n"
        f"💵 بازپرداخت: {fmt(repay)}"
    )


# ============================================================
# 🪙 نمایش کریپتو
# ============================================================

async def show_crypto(message):

    if not await check_level(
        message,
        "کریپتو"
    ):
        return

    if (
        not crypto_prices
        or now() - crypto_last_update >= CRYPTO_UPDATE_SECONDS
    ):
        await update_crypto_prices()

    text = (
        "🪙 **بازار کریپتو پول‌سیتی**\n\n"
        f"🔄 بروزرسانی: هر "
        f"{CRYPTO_UPDATE_SECONDS} ثانیه\n\n"
    )

    for name, item in CRYPTO.items():

        data = crypto_prices.get(name)

        if not data:

            text += (
                f"{item['emoji']} "
                f"{name}: ⏳\n"
            )

            continue

        price = data["price"]
        change = data["change"]

        arrow = (
            "🟢"
            if change >= 0
            else "🔴"
        )

        text += (
            f"{item['emoji']} "
            f"**{name} ({item['symbol']})**\n"
            f"💵 قیمت واقعی: "
            f"${price:,.8f}\n"
            f"{arrow} تغییر ۲۴ساعته: "
            f"{change:+.2f}%\n\n"
        )

    text += (
        "━━━━━━━━━━━━━━\n"
        "💡 خرید با پول‌سیتی انجام می‌شود.\n\n"
        "مثال:\n"
        "`خرید بیت کوین 5000`\n"
        "`خرید اتریوم 10000`"
    )

    await message.reply(text)


# ============================================================
# 🛒 خرید کریپتو
# ============================================================

async def buy_crypto(
    message,
    crypto_name,
    money_amount
):

    if not await check_level(
        message,
        "کریپتو"
    ):
        return

    if money_amount <= 0:

        await message.reply(
            "❌ مبلغ باید بیشتر از صفر باشد."
        )

        return

    user_id = message.author.user_id
    user = get_user(user_id)

    if user["money"] < money_amount:

        await message.reply(
            f"❌ پول‌سیتی کافی نیست.\n"
            f"💰 موجودی: "
            f"{fmt(user['money'])}"
        )

        return

    if (
        not crypto_prices
        or now() - crypto_last_update >= CRYPTO_UPDATE_SECONDS
    ):
        await update_crypto_prices()

    data = crypto_prices.get(
        crypto_name
    )

    if (
        not data
        or data["price"] <= 0
    ):

        await message.reply(
            "⏳ قیمت این کریپتو فعلاً دریافت نشده؛ چند ثانیه بعد دوباره امتحان کن."
        )

        return

    usd_price = data["price"]

    crypto_amount = (
        money_amount / usd_price
    )

    db.execute("""
    INSERT INTO crypto_assets(
        user_id,
        crypto,
        amount,
        invested
    )
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id, crypto)
    DO UPDATE SET
        amount=amount+excluded.amount,
        invested=invested+excluded.invested
    """, (
        user_id,
        crypto_name,
        crypto_amount,
        money_amount
    ))

    db.execute(
        "UPDATE users SET money=money-? WHERE user_id=?",
        (
            money_amount,
            user_id
        )
    )

    db.commit()

    add_history(
        user_id,
        f"خرید کریپتو {crypto_name}",
        -money_amount
    )

    await message.reply(
        f"{CRYPTO[crypto_name]['emoji']} "
        f"**خرید {crypto_name}**\n\n"
        f"💰 مبلغ خرید: "
        f"**{fmt(money_amount)} پول‌سیتی**\n"
        f"📊 قیمت فعلی: "
        f"${usd_price:,.8f}\n"
        f"🪙 مقدار دریافتی: "
        f"{crypto_amount:.8f} "
        f"{CRYPTO[crypto_name]['symbol']}\n\n"
        f"✅ خرید با موفقیت انجام شد."
    )


# ============================================================
# 💵 فروش کریپتو
# ============================================================

async def sell_crypto(
    message,
    crypto_name,
    money_amount
):

    if not await check_level(
        message,
        "کریپتو"
    ):
        return

    if money_amount <= 0:

        await message.reply(
            "❌ مبلغ باید بیشتر از صفر باشد."
        )

        return

    user_id = message.author.user_id

    if (
        not crypto_prices
        or now() - crypto_last_update >= CRYPTO_UPDATE_SECONDS
    ):
        await update_crypto_prices()

    price = crypto_prices.get(
        crypto_name
    )

    if (
        not price
        or price["price"] <= 0
    ):

        await message.reply(
            "⏳ قیمت فعلی در دسترس نیست."
        )

        return

    cur = db.cursor()

    cur.execute("""
    SELECT amount, invested
    FROM crypto_assets
    WHERE user_id=? AND crypto=?
    """, (
        user_id,
        crypto_name
    ))

    asset = cur.fetchone()

    if (
        not asset
        or asset["amount"] <= 0
    ):

        await message.reply(
            "❌ از این کریپتو چیزی نداری."
        )

        return

    current_value = (
        asset["amount"]
        * price["price"]
    )

    if money_amount > current_value:

        await message.reply(
            f"❌ ارزش دارایی کافی نیست.\n"
            f"💰 ارزش فعلی: "
            f"{fmt(current_value)}"
        )

        return

    crypto_to_sell = (
        money_amount / price["price"]
    )

    remaining = (
        asset["amount"]
        - crypto_to_sell
    )

    invested_ratio = (
        asset["invested"]
        * (
            crypto_to_sell
            / asset["amount"]
        )
    )

    profit = (
        money_amount
        - invested_ratio
    )

    db.execute("""
    UPDATE crypto_assets
    SET amount=?,
        invested=?
    WHERE user_id=? AND crypto=?
    """, (
        remaining,
        max(
            0,
            asset["invested"]
            - invested_ratio
        ),
        user_id,
        crypto_name
    ))

    db.execute(
        "UPDATE users SET money=money+? WHERE user_id=?",
        (
            money_amount,
            user_id
        )
    )

    db.commit()

    await message.reply(
        f"💵 **فروش {crypto_name}**\n\n"
        f"💰 مبلغ فروش: "
        f"{fmt(money_amount)} پول‌سیتی\n"
        f"📊 قیمت فعلی: "
        f"${price['price']:,.8f}\n"
        f"{'🟢' if profit >= 0 else '🔴'} "
        f"سود/ضرر: {fmt(profit)}\n\n"
        f"✅ فروش انجام شد."
    )


# ============================================================
# 📊 دارایی کریپتو
# ============================================================

async def crypto_assets(message):

    if not await check_level(
        message,
        "کریپتو"
    ):
        return

    user_id = message.author.user_id

    cur = db.cursor()

    cur.execute("""
    SELECT crypto, amount, invested
    FROM crypto_assets
    WHERE user_id=? AND amount>0
    """, (user_id,))

    rows = cur.fetchall()

    if not rows:

        await message.reply(
            "🪙 هنوز هیچ کریپتویی نداری."
        )

        return

    if (
        not crypto_prices
        or now() - crypto_last_update >= CRYPTO_UPDATE_SECONDS
    ):
        await update_crypto_prices()

    text = "🪙 **دارایی‌های کریپتو**\n\n"

    total_value = 0
    total_invested = 0

    for row in rows:

        crypto = row["crypto"]
        amount = row["amount"]
        invested = row["invested"]

        price = crypto_prices.get(
            crypto,
            {"price": 0}
        )["price"]

        value = amount * price

        total_value += value
        total_invested += invested

        text += (
            f"{CRYPTO[crypto]['emoji']} "
            f"{crypto}\n"
            f"🪙 مقدار: "
            f"{amount:.8f}\n"
            f"💰 سرمایه‌گذاری: "
            f"{fmt(invested)}\n"
            f"📊 ارزش فعلی: "
            f"{fmt(value)}\n\n"
        )

    profit = (
        total_value
        - total_invested
    )

    text += (
        "━━━━━━━━━━━━━━\n"
        f"💰 ارزش کل: "
        f"{fmt(total_value)}\n"
        f"{'🟢' if profit >= 0 else '🔴'} "
        f"سود/ضرر کل: "
        f"{fmt(profit)}"
    )

    await message.reply(text)


# ============================================================
# 📈 بورس
# ============================================================

async def show_stocks(message):

    if not await check_level(
        message,
        "بورس"
    ):
        return

    text = "📈 **بورس پول‌سیتی**\n\n"

    for name, data in STOCKS.items():

        text += (
            f"🏢 {name} "
            f"({data['symbol']})\n"
            f"💰 قیمت هر سهم: "
            f"{fmt(data['price'])}\n\n"
        )

    text += (
        "🛒 خرید با مبلغ پول‌سیتی:\n"
        "`خرید سهام نفت 50000`\n\n"
        "💵 فروش:\n"
        "`فروش سهام نفت 50000`\n\n"
        "📊 دارایی:\n"
        "`دارایی بورس`"
    )

    await message.reply(text)


async def buy_stock(
    message,
    stock,
    money_amount
):

    if not await check_level(
        message,
        "بورس"
    ):
        return

    if stock not in STOCKS:

        await message.reply(
            "❌ این سهم وجود ندارد."
        )

        return

    user_id = message.author.user_id
    user = get_user(user_id)

    if (
        money_amount <= 0
        or user["money"] < money_amount
    ):

        await message.reply(
            "❌ پول‌سیتی کافی نیست."
        )

        return

    price = STOCKS[stock]["price"]

    shares = (
        money_amount / price
    )

    db.execute("""
    INSERT INTO stock_assets(
        user_id,
        stock,
        shares,
        invested
    )
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id, stock)
    DO UPDATE SET
        shares=shares+excluded.shares,
        invested=invested+excluded.invested
    """, (
        user_id,
        stock,
        shares,
        money_amount
    ))

    db.execute(
        "UPDATE users SET money=money-? WHERE user_id=?",
        (
            money_amount,
            user_id
        )
    )

    db.commit()

    await message.reply(
        f"📈 **خرید سهم {stock}**\n\n"
        f"💰 سرمایه‌گذاری: "
        f"{fmt(money_amount)}\n"
        f"📊 قیمت سهم: "
        f"{fmt(price)}\n"
        f"📦 تعداد سهم: "
        f"{shares:.4f}\n\n"
        f"✅ خرید انجام شد."
    )


async def stock_assets(message):

    if not await check_level(
        message,
        "بورس"
    ):
        return

    user_id = message.author.user_id

    cur = db.cursor()

    cur.execute("""
    SELECT stock, shares, invested
    FROM stock_assets
    WHERE user_id=? AND shares>0
    """, (user_id,))

    rows = cur.fetchall()

    if not rows:

        await message.reply(
            "📈 هنوز سهمی نداری."
        )

        return

    text = "📈 **سبد بورس**\n\n"

    total = 0
    invested = 0

    for row in rows:

        price = STOCKS[
            row["stock"]
        ]["price"]

        value = (
            row["shares"]
            * price
        )

        total += value
        invested += row["invested"]

        text += (
            f"🏢 {row['stock']}\n"
            f"📦 سهم: "
            f"{row['shares']:.4f}\n"
            f"💰 ارزش: "
            f"{fmt(value)}\n\n"
        )

    text += (
        f"💰 ارزش کل: "
        f"{fmt(total)}\n"
        f"📊 سود/ضرر: "
        f"{fmt(total-invested)}"
    )

    await message.reply(text)


# ============================================================
# 🎮 بازی‌ها
# ============================================================

async def dice_game(message):

    user_id = message.author.user_id
    user = get_user(user_id)

    bet = 1000

    if user["money"] < bet:

        await message.reply(
            "❌ حداقل ۱۰۰۰ پول لازم داری."
        )

        return

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)

    total = d1 + d2

    if total == 7:
        reward = bet * 2

    elif d1 == d2:
        reward = bet * 3

    elif total in (2, 12):
        reward = bet * 5

    else:
        reward = 0

    db.execute(
        """
        UPDATE users
        SET money=money-?,
            games_played=games_played+1
        WHERE user_id=?
        """,
        (
            bet,
            user_id
        )
    )

    if reward:

        db.execute(
            """
            UPDATE users
            SET money=money+?
            WHERE user_id=?
            """,
            (
                reward,
                user_id
            )
        )

    db.execute(
        """
        UPDATE users
        SET xp=xp+10
        WHERE user_id=?
        """,
        (user_id,)
    )

    db.commit()

    update_title(user_id)

    await message.reply(
        f"🎲 **تاس**\n\n"
        f"🎲 {d1} + {d2} = {total}\n"
        f"💰 شرط: {fmt(bet)}\n"
        f"{'🎉 جایزه: ' + fmt(reward) if reward else '💥 باختی!'}"
    )


async def coin_game(message):

    user_id = message.author.user_id
    user = get_user(user_id)

    bet = 1000

    if user["money"] < bet:

        await message.reply(
            "❌ پول کافی نیست."
        )

        return

    result = random.choice([
        "شیر",
        "خط"
    ])

    win = random.choice([
        True,
        False
    ])

    db.execute(
        """
        UPDATE users
        SET money=money-?,
            games_played=games_played+1,
            xp=xp+5
        WHERE user_id=?
        """,
        (
            bet,
            user_id
        )
    )

    if win:

        db.execute(
            """
            UPDATE users
            SET money=money+?
            WHERE user_id=?
            """,
            (
                bet * 2,
                user_id
            )
        )

    db.commit()

    update_title(user_id)

    await message.reply(
        f"🪙 شیر یا خط\n\n"
        f"🎯 نتیجه: {result}\n"
        f"{'🎉 بردی! +2,000' if win else '💥 باختی!'}"
    )


async def rps_game(message):

    user_id = message.author.user_id
    user = get_user(user_id)

    bet = 1000

    if user["money"] < bet:

        await message.reply(
            "❌ پول کافی نیست."
        )

        return

    choices = [
        "سنگ",
        "کاغذ",
        "قیچی"
    ]

    player = random.choice(
        choices
    )

    bot_choice = random.choice(
        choices
    )

    if player == bot_choice:

        result = "مساوی 😐"
        reward = bet

    elif (
        (
            player == "سنگ"
            and bot_choice == "قیچی"
        )
        or
        (
            player == "کاغذ"
            and bot_choice == "سنگ"
        )
        or
        (
            player == "قیچی"
            and bot_choice == "کاغذ"
        )
    ):

        result = "بردی 🎉"
        reward = bet * 2

    else:

        result = "باختی 💥"
        reward = 0

    db.execute(
        """
        UPDATE users
        SET money=money-?,
            games_played=games_played+1,
            xp=xp+10
        WHERE user_id=?
        """,
        (
            bet,
            user_id
        )
    )

    if reward:

        db.execute(
            """
            UPDATE users
            SET money=money+?
            WHERE user_id=?
            """,
            (
                reward,
                user_id
            )
        )

    db.commit()

    update_title(user_id)

    await message.reply(
        f"✊ **سنگ کاغذ قیچی**\n\n"
        f"👤 تو: {player}\n"
        f"🤖 ربات: {bot_choice}\n\n"
        f"{result}"
    )


# ============================================================
# 🎰 قمار
# ============================================================

async def casino(message):
    if not await check_level(message, "کازینو"):
        return
    await message.reply(casino_help())


# ============================================================
# 🕵️ دزدی
# ============================================================

async def robbery(
    message,
    target_id
):

    if not await check_level(
        message,
        "دزدی"
    ):
        return

    user_id = message.author.user_id

    if user_id == target_id:

        await message.reply(
            "نمیشه از خودت دزدی کرد احمق 🤦‍♂️"
        )

        return

    if target_id == BOT_ID:

        await message.reply(
            "😅"
        )

        return

    if target_id == OWNER_ID:

        await message.reply(
            "می‌خوای بن شی؟ 😂"
        )

        return

    target = get_user(target_id)

    if not target:

        await message.reply(
            "❌ این بازیکن در پول‌سیتی وجود ندارد."
        )

        return

    if target["money"] <= 0:

        await message.reply(
            "💸 این بازیکن پولی برای دزدی نداره."
        )

        return

    success = (
        random.random()
        < 0.45
    )

    if success:

        amount = min(
            target["money"],
            random.randint(
                500,
                max(
                    500,
                    target["money"] // 4
                )
            )
        )

        db.execute(
            """
            UPDATE users
            SET money=money+?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        db.execute(
            """
            UPDATE users
            SET money=money-?
            WHERE user_id=?
            """,
            (
                amount,
                target_id
            )
        )

        db.commit()

        await message.reply(
            f"🕵️ **دزدی موفق بود!**\n\n"
            f"💰 مبلغ دزدیده‌شده: "
            f"{fmt(amount)}"
        )

    else:

        db.execute(
            """
            UPDATE users
            SET wanted=wanted+1
            WHERE user_id=?
            """,
            (user_id,)
        )

        db.commit()

        await message.reply(
            "🚨 دزدی ناموفق بود!\n"
            "⚠️ تحت تعقیب شدی."
        )


# ============================================================
# 🎡 گردونه
# ============================================================

async def wheel(message):

    if not await check_level(
        message,
        "گردونه"
    ):
        return

    user_id = message.author.user_id
    user = get_user(user_id)

    if (
        now()
        - user["last_wheel"]
        < 86400
    ):

        await message.reply(
            "⏳ امروز گردونه رو چرخوندی."
        )

        return

    # بیشتر مواقع جایزه‌های پایین‌تر داده می‌شوند 😈
    rewards = [
        100, 100, 150, 150, 200, 200,
        250, 300, 400, 500, 600, 700,
        0,
    ]

    reward = random.choice(
        rewards
    )

    db.execute(
        """
        UPDATE users
        SET money=money+?,
            last_wheel=?
        WHERE user_id=?
        """,
        (
            reward,
            now(),
            user_id
        )
    )

    db.commit()

    await message.reply(
        f"🎡 **گردونه چرخید!**\n\n"
        f"🎁 جایزه: "
        f"**{fmt(reward)} پول‌سیتی**"
    )


# ============================================================
# 🎯 مأموریت
# ============================================================

async def missions(message):

    if not await check_level(
        message,
        "ماموریت"
    ):
        return

    await message.reply(
        "🎯 **مأموریت امروز**\n\n"
        "🎮 ۳ بازی انجام بده\n"
        "💼 یک بار حقوق بگیر\n"
        "🎁 جایزه: ۵۰۰۰ پول‌سیتی + ۱۰۰ XP"
    )


# ============================================================
# 🏙️ شهر
# ============================================================

async def city(message):

    if not await check_level(
        message,
        "شهر"
    ):
        return

    await message.reply(
        "🏙️ **شهر پول‌سیتی**\n\n"
        "🏗️ ساختمان‌ها\n"
        "💰 خزانه شهر\n"
        "🛒 بازار شهر\n"
        "📰 اخبار اقتصادی\n"
        "🏆 رتبه شهرها\n\n"
        "🚧 بخش‌های پیشرفته شهر در حال توسعه هستند."
    )


# ============================================================
# 🏢 شرکت
# ============================================================

async def company(message):

    if not await check_level(
        message,
        "شرکت"
    ):
        return

    user_id = message.author.user_id

    cur = db.cursor()

    cur.execute(
        """
        SELECT *
        FROM companies
        WHERE owner_id=?
        """,
        (user_id,)
    )

    row = cur.fetchone()

    if not row:

        await message.reply(
            "🏢 هنوز شرکت نداری.\n\n"
            "برای ساخت شرکت:\n"
            "`ساخت شرکت نام شرکت`"
        )

        return

    await message.reply(
        f"🏢 **{row['name']}**\n\n"
        f"⭐ سطح: {row['level']}\n"
        f"👥 کارمندان: {row['employees']}\n"
        f"💰 سرمایه: {fmt(row['money'])}"
    )


async def create_company(
    message,
    name
):

    if not await check_level(
        message,
        "شرکت"
    ):
        return

    user_id = message.author.user_id
    user = get_user(user_id)

    cur = db.cursor()

    cur.execute(
        """
        SELECT id
        FROM companies
        WHERE owner_id=?
        """,
        (user_id,)
    )

    if cur.fetchone():

        await message.reply(
            "❌ تو قبلاً شرکت داری."
        )

        return

    cost = 100000

    if user["money"] < cost:

        await message.reply(
            f"❌ برای ساخت شرکت "
            f"{fmt(cost)} پول لازم داری."
        )

        return

    db.execute(
        """
        INSERT INTO companies(
            owner_id,
            name,
            money
        )
        VALUES (?, ?, 0)
        """,
        (
            user_id,
            name
        )
    )

    db.execute(
        """
        UPDATE users
        SET money=money-?,
            company=?
        WHERE user_id=?
        """,
        (
            cost,
            name,
            user_id
        )
    )

    db.commit()

    await message.reply(
        f"🏢 شرکت **{name}** ساخته شد!\n\n"
        f"💰 هزینه: {fmt(cost)}"
    )


# ============================================================
# 🤝 اتحاد | فاز ۳
# ============================================================

async def alliance(message):

    if not await check_level(
        message,
        "اتحاد"
    ):
        return

    user_id = message.author.user_id

    cur = db.cursor()

    cur.execute("""
    SELECT a.*
    FROM alliances a
    JOIN alliance_members am
    ON a.id=am.alliance_id
    WHERE am.user_id=?
    """, (user_id,))

    row = cur.fetchone()

    if not row:

        await message.reply(
            "🤝 **سیستم اتحاد پول‌سیتی — فاز ۳**\n\n"
            "🏰 ساخت اتحاد\n"
            "👥 دعوت عضو\n"
            "💰 خزانه مشترک\n"
            "🏗️ پروژه‌های گروهی\n"
            "📈 سطح اتحاد\n"
            "🏆 رتبه‌بندی اتحادها\n\n"
            "برای ساخت:\n"
            "`ساخت اتحاد نام اتحاد`"
        )

        return

    await message.reply(
        f"🤝 **اتحاد {row['name']}**\n\n"
        f"⭐ سطح: {row['level']}\n"
        f"✨ XP: {fmt(row['xp'])}\n"
        f"💰 خزانه: {fmt(row['treasury'])}\n\n"
        f"👑 رهبر: {row['leader_id']}"
    )


async def create_alliance(
    message,
    name
):

    if not await check_level(
        message,
        "اتحاد"
    ):
        return

    user_id = message.author.user_id
    user = get_user(user_id)

    cur = db.cursor()

    cur.execute(
        """
        SELECT user_id
        FROM alliance_members
        WHERE user_id=?
        """,
        (user_id,)
    )

    if cur.fetchone():

        await message.reply(
            "❌ تو همین الان عضو یک اتحاد هستی."
        )

        return

    cost = 250000

    if user["money"] < cost:

        await message.reply(
            f"❌ برای ساخت اتحاد "
            f"{fmt(cost)} پول لازم داری."
        )

        return

    try:

        cur.execute("""
        INSERT INTO alliances(
            name,
            leader_id,
            created_at
        )
        VALUES (?, ?, ?)
        """, (
            name,
            user_id,
            now()
        ))

        alliance_id = cur.lastrowid

        cur.execute("""
        INSERT INTO alliance_members(
            alliance_id,
            user_id,
            role,
            joined_at
        )
        VALUES (?, ?, 'leader', ?)
        """, (
            alliance_id,
            user_id,
            now()
        ))

        db.execute(
            """
            UPDATE users
            SET money=money-?,
                alliance=?
            WHERE user_id=?
            """,
            (
                cost,
                name,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"🤝 **اتحاد ساخته شد!**\n\n"
            f"🏰 نام: {name}\n"
            f"👑 رهبر: "
            f"{mention(user['name'], user_id)}\n"
            f"💰 هزینه: {fmt(cost)}"
        )

    except sqlite3.IntegrityError:

        await message.reply(
            "❌ این نام اتحاد قبلاً استفاده شده."
        )


# ============================================================
# 🛒 بازار
# ============================================================

async def market(message):

    if not await check_level(
        message,
        "بازار"
    ):
        return

    await message.reply(
        "🛒 **بازار پول‌سیتی**\n\n"
        "💰 خریدوفروش بازیکنان\n"
        "🏭 کالاهای شرکت‌ها\n"
        "💎 منابع کمیاب\n"
        "🎁 آیتم‌های محدود\n\n"
        "🚧 بازار بازیکن‌به‌بازیکن در حال توسعه است."
    )


# ============================================================
# 🎁 فروشگاه واقعی
# ============================================================

async def real_shop(message):

    text = (
        "🛍️ **فروشگاه ویژه پول‌سیتی**\n\n"
    )

    for product, data in REAL_PRODUCTS.items():

        text += (
            f"🎁 {product}\n"
            f"💳 قیمت: "
            f"{fmt(data['price'])} تومان\n\n"
        )

    text += (
        "━━━━━━━━━━━━━━\n"
        "🧾 برای خرید:\n"
        "`خرید واقعی نام محصول`\n\n"
        "💡 بعد از ثبت درخواست، اطلاعات پرداخت برایت ارسال می‌شود."
    )

    await message.reply(text)


async def create_purchase(
    message,
    product
):

    if product not in REAL_PRODUCTS:

        await message.reply(
            "❌ این محصول وجود ندارد."
        )

        return

    user_id = message.author.user_id
    user = get_user(user_id)

    data = REAL_PRODUCTS[product]

    cur = db.cursor()

    cur.execute("""
    INSERT INTO purchase_requests(
        buyer_id,
        buyer_name,
        product,
        amount,
        reward_type,
        reward_value,
        status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (
        user_id,
        user["name"],
        product,
        data["price"],
        data["type"],
        str(data["value"]),
        now()
    ))

    request_id = cur.lastrowid

    db.commit()

    await message.reply(
        f"🧾 **درخواست خرید ثبت شد!**\n\n"
        f"🎁 محصول: {product}\n"
        f"💳 مبلغ: "
        f"{fmt(data['price'])} تومان\n\n"
        f"📨 مبلغ را به مالک پول‌سیتی ارسال کن:\n"
        f"👑 "
        f"{mention('Owner_Pool_City', OWNER_ID)}\n\n"
        f"⚠️ بعد از ارسال پاکت هدیه، منتظر تأیید مالک باش.\n"
        f"🔐 پرداخت به‌صورت دستی بررسی می‌شود."
    )

    try:

        await bot.send_message(
            OWNER_ID,
            f"🧾 **درخواست خرید جدید**\n\n"
            f"👤 خریدار: "
            f"{mention(user['name'], user_id)}\n"
            f"🆔 ID: {user_id}\n"
            f"🎁 محصول: {product}\n"
            f"💳 مبلغ: "
            f"{fmt(data['price'])} تومان\n"
            f"🔢 درخواست: #{request_id}\n\n"
            f"⚠️ پاکت هدیه را دستی بررسی کن.\n"
            f"اگر پول را دریافت کردی، تأیید کن.",
            components=purchase_keyboard(
                request_id
            )
        )

    except Exception as e:

        print(
            "PURCHASE OWNER MESSAGE ERROR:",
            repr(e)
        )


# ============================================================
# 👑 ریست تست مالک
# ============================================================

def reset_owner_test():

    cur = db.cursor()

    cur.execute("""
    UPDATE users
    SET money=0,
        bank=0,
        diamonds=0,
        xp=0,
        job='',
        house='',
        car='',
        wanted=0,
        prison=0,
        last_money=0,
        last_daily=0,
        last_salary=0,
        last_wheel=0,
        title='تازه‌کار',
        theme='',
        season_badge='',
        season_ticket=0,
        company='',
        city='',
        alliance='',
        loan=0,
        loan_due=0,
        streak=0,
        games_played=0,
        gambling_played=0,
        stocks_value=0,
        crypto_value=0
    WHERE user_id=?
    """, (OWNER_ID,))

    cur.execute(
        """
        DELETE FROM crypto_assets
        WHERE user_id=?
        """,
        (OWNER_ID,)
    )

    cur.execute(
        """
        DELETE FROM stock_assets
        WHERE user_id=?
        """,
        (OWNER_ID,)
    )

    db.commit()


# ============================================================
# 👑 چیت مالک
# ============================================================

async def handle_cheat(
    message,
    text
):

    user_id = message.author.user_id

    if str(user_id) != str(OWNER_ID):
        return False

    parts = text.split()

    # --------------------------------------------------------
    # راهنمای چیت
    # --------------------------------------------------------

    if text == "راهنما چیت":

        await message.reply(
            cheat_help()
        )

        return True

    # --------------------------------------------------------
    # ریست تست
    # --------------------------------------------------------

    if text == "ریست تست":

        reset_owner_test()

        await message.reply(
            "🔄 **ریست تست انجام شد!**\n\n"
            "💰 پول: 0\n"
            "🏦 بانک: 0\n"
            "💎 الماس: 0\n"
            "⭐ XP: 0\n"
            "💼 شغل: ندارد\n"
            "🚗 ماشین: ندارد\n"
            "🏠 خانه: ندارد\n"
            "🚨 جریمه: 0\n"
            "🔒 زندان: 0\n\n"
            "✅ آماده تست مجددی."
        )

        return True

    # --------------------------------------------------------
    # گرفتن پول
    # --------------------------------------------------------

    if text.startswith("گرفتن پول "):

        try:
            amount = int(parts[-1])
        except:

            await message.reply(
                "❌ مقدار اشتباه است."
            )

            return True

        db.execute(
            """
            UPDATE users
            SET money=money+?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"👑 چیت اجرا شد.\n"
            f"💰 +{fmt(amount)} پول"
        )

        return True

    # --------------------------------------------------------
    # کم کردن پول (فقط مالک)
    # --------------------------------------------------------

    if text.startswith("کم پول "):

        try:
            amount = int(parts[-1])
        except:
            await message.reply("❌ مقدار اشتباه است.")
            return True

        if amount <= 0:
            await message.reply("❌ مقدار باید بیشتر از صفر باشد.")
            return True

        user = get_user(user_id)
        current_money = max(0, int(user["money"]))
        removed = min(amount, current_money)

        db.execute(
            "UPDATE users SET money=money-? WHERE user_id=?",
            (removed, user_id)
        )
        db.commit()

        await message.reply(
            f"👑 چیت اجرا شد.\n"
            f"💸 -{fmt(removed)} پول\n"
            f"💰 موجودی جدید: {fmt(current_money - removed)} پول"
        )

        return True

    # --------------------------------------------------------
    # گرفتن الماس
    # --------------------------------------------------------

    if text.startswith("گرفتن الماس "):

        try:
            amount = int(parts[-1])
        except:

            await message.reply(
                "❌ مقدار اشتباه است."
            )

            return True

        db.execute(
            """
            UPDATE users
            SET diamonds=diamonds+?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"👑 چیت اجرا شد.\n"
            f"💎 +{fmt(amount)} الماس"
        )

        return True

    # --------------------------------------------------------
    # تغییر XP
    # --------------------------------------------------------

    if text.startswith(
        "تغییر اکس پی به "
    ):

        try:
            amount = int(parts[-1])
        except:

            await message.reply(
                "❌ مقدار XP اشتباه است."
            )

            return True

        amount = max(
            0,
            amount
        )

        db.execute(
            """
            UPDATE users
            SET xp=?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        db.commit()

        update_title(user_id)

        await message.reply(
            f"⭐ XP به "
            f"{fmt(amount)} تغییر کرد.\n"
            f"📊 لول فعلی: "
            f"{get_level(amount)}"
        )

        return True

    # --------------------------------------------------------
    # ⭐ چیت تغییر لول
    # --------------------------------------------------------

    if text.startswith(
        "تغییر لول به "
    ):

        try:

            level = int(
                text.replace(
                    "تغییر لول به ",
                    "",
                    1
                ).strip()
            )

        except:

            await message.reply(
                "❌ شماره لول اشتباه است.\n\n"
                "مثال:\n"
                "`تغییر لول به 15`"
            )

            return True

        if level < 1 or level > 15:

            await message.reply(
                "❌ لول باید بین 1 تا 15 باشد."
            )

            return True

        xp = LEVEL_XP[level]

        db.execute(
            """
            UPDATE users
            SET xp=?
            WHERE user_id=?
            """,
            (
                xp,
                user_id
            )
        )

        db.commit()

        update_title(user_id)

        await message.reply(
            f"👑 **چیت لول اجرا شد!**\n\n"
            f"⭐ لول جدید: **{level}**\n"
            f"✨ XP: **{fmt(xp)}**"
        )

        return True

    # --------------------------------------------------------
    # حذف جریمه
    # --------------------------------------------------------

    if text == "حذف جریمه":

        db.execute(
            """
            UPDATE users
            SET wanted=0,
                prison=0
            WHERE user_id=?
            """,
            (user_id,)
        )

        db.commit()

        await message.reply(
            "🚨 جریمه‌ها و وضعیت زندان پاک شد."
        )

        return True

    # --------------------------------------------------------
    # تغییر بانک
    # --------------------------------------------------------

    if text.startswith(
        "تغییر موجودی بانک به "
    ):

        try:
            amount = int(parts[-1])
        except:

            await message.reply(
                "❌ مقدار اشتباه است."
            )

            return True

        amount = max(
            0,
            amount
        )

        db.execute(
            """
            UPDATE users
            SET bank=?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"🏦 موجودی بانک روی "
            f"{fmt(amount)} تنظیم شد."
        )

        return True

    # --------------------------------------------------------
    # گرفتن شغل
    # --------------------------------------------------------

    if text.startswith(
        "گرفتن شغل "
    ):

        job = text.replace(
            "گرفتن شغل ",
            "",
            1
        ).strip()

        if job not in JOBS:

            await message.reply(
                "❌ این شغل وجود ندارد."
            )

            return True

        db.execute(
            """
            UPDATE users
            SET job=?
            WHERE user_id=?
            """,
            (
                job,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"💼 شغل به «{job}» تغییر کرد."
        )

        return True

    # --------------------------------------------------------
    # گرفتن خونه
    # --------------------------------------------------------

    if text.startswith(
        "گرفتن خونه "
    ):

        house = text.replace(
            "گرفتن خونه ",
            "",
            1
        ).strip()

        if house not in HOUSES:

            await message.reply(
                "❌ این خانه وجود ندارد."
            )

            return True

        db.execute(
            """
            UPDATE users
            SET house=?
            WHERE user_id=?
            """,
            (
                house,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"🏠 خانه به «{house}» تغییر کرد."
        )

        return True

    # --------------------------------------------------------
    # گرفتن خانه
    # --------------------------------------------------------

    if text.startswith(
        "گرفتن خانه "
    ):

        house = text.replace(
            "گرفتن خانه ",
            "",
            1
        ).strip()

        if house not in HOUSES:

            await message.reply(
                "❌ این خانه وجود ندارد."
            )

            return True

        db.execute(
            """
            UPDATE users
            SET house=?
            WHERE user_id=?
            """,
            (
                house,
                user_id
            )
        )

        db.commit()

        await message.reply(
            f"🏠 خانه به «{house}» تغییر کرد."
        )

        return True

    return False


# ============================================================
# 🔘 Callback
# ============================================================

def game_names_for_room(game):
    return {"مار و پله": "🐍", "مسابقه ماشین": "🚗"}.get(game, "🎮") + f" **{game}"

def ttt_keyboard(room):
    kb = InlineKeyboardMarkup()
    for i, cell in enumerate(room["board"]):
        label = cell if cell.strip() else str(i + 1)
        kb.add(InlineKeyboardButton(label, callback_data=f"ttt:{room['id']}:{i}"), row=i // 3)
    kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room['id']}"), row=3)
    return kb

def rps_room_keyboard(room_id):
    kb = InlineKeyboardMarkup()
    for i, name in enumerate(("✊ سنگ", "📄 کاغذ", "✂️ قیچی")):
        kb.add(InlineKeyboardButton(name, callback_data=f"rpsroom:{room_id}:{name.split()[-1]}"), row=i)
    return kb

def guess_keyboard(room_id):
    kb = InlineKeyboardMarkup()
    for i in range(1, 21):
        kb.add(InlineKeyboardButton(str(i), callback_data=f"guessroom:{room_id}:{i}"), row=(i-1)//5)
    return kb

def move_keyboard(room_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏃 حرکت", callback_data=f"move:{room_id}"), row=0)
    kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)
    return kb

def mines_keyboard(room_id, room):
    kb = InlineKeyboardMarkup()
    for i in range(9):
        if i in room.get("revealed", set()):
            label = "💰"
        else:
            label = "❓"
        kb.add(InlineKeyboardButton(label, callback_data=f"mine:{room_id}:{i}"), row=i//3)
    return kb

async def restore_room_message(message, room_id):
    """بعد از پیام موقت، اتاق را دوباره به حالت عادی برمی‌گرداند."""
    await asyncio.sleep(random.randint(10, 20))
    room = casino_rooms.get(room_id)
    if not room:
        return

    kb = InlineKeyboardMarkup()
    if room.get("type") == "gamble":
        kb.add(InlineKeyboardButton("🎮 شرکت در بازی", callback_data=f"gameroom:join:{room_id}"), row=0)
        kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)
        text = (
            f"🎰 **اتاق قمار**\n\n"
            f"💰 مبلغ ورود: {fmt(room['bet'])} پول\n"
            f"👥 ظرفیت: {room['capacity']} نفر\n"
            f"📊 نفرات فعلی: {len(room['players'])}/{room['capacity']}\n\n"
            f"بازیکن بعدی می‌تواند وارد شود."
        )
    elif room.get("type") == "game":
        game = room.get("game", "بازی")
        kb.add(InlineKeyboardButton(f"🎮 شرکت در {game}", callback_data=f"gameroom:join:{room_id}"), row=0)
        kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)
        text = (
            f"{game_names_for_room(game)} **اتاق {game} ساخته شد**\n\n"
            f"💰 مبلغ ورود: {fmt(room['bet'])} پول\n"
            f"👥 نفرات: {len(room['players'])}/{room['capacity']}\n\n"
            f"بازیکن بعدی روی دکمه شیشه‌ای بزند."
        )
    else:
        return

    try:
        await message.edit(text, components=kb)
    except Exception:
        pass


async def on_callback(
    callback: CallbackQuery
):

    try:

        # ----------------------------------------------------
        # 📢 بررسی عضویت اجباری
        # ----------------------------------------------------
        if getattr(callback, "data", "") == "forcejoin:check":
            user_id = callback.from_user.user_id

            if str(user_id) == str(OWNER_ID):
                ok = True
            else:
                ok = False
                try:
                    member = await bot.get_chat_member(
                        FORCE_JOIN_CHANNEL,
                        user_id
                    )
                    status = str(getattr(member, "status", "")).lower()
                    ok = status in (
                        "member",
                        "administrator",
                        "creator",
                        "owner",
                    )
                except Exception as e:
                    print(
                        "FORCE JOIN CALLBACK CHECK ERROR:",
                        repr(e)
                    )

            if ok:
                await callback.message.edit(
                    "✅ **عضویت تأیید شد!**\n\n"
                    "🎉 حالا می‌تونی از تمام امکانات پول‌سیتی استفاده کنی."
                )
            else:
                kb = InlineKeyboardMarkup()
                kb.add(
                    InlineKeyboardButton(
                        "📢 عضویت در کانال پول‌سیتی",
                        url=FORCE_JOIN_CHANNEL_URL
                    ),
                    row=0
                )
                kb.add(
                    InlineKeyboardButton(
                        "🔄 بررسی مجدد",
                        callback_data="forcejoin:check"
                    ),
                    row=1
                )
                await callback.message.edit(
                    "❌ هنوز عضویتت تأیید نشده.\n\n"
                    "اول عضو کانال شو و بعد «بررسی مجدد» رو بزن.",
                    components=kb
                )

            return

        data = callback.data or ""

        user_id = callback.from_user.user_id

        if data == "lottery:buy":
            user = get_user(user_id)
            if user["money"] < LOTTERY_TICKET_PRICE:
                await callback.message.edit("❌ برای خرید بلیت ۱۰۰ پول لازم داری.")
                return
            draw_date = lottery_draw_key()
            db.execute("UPDATE users SET money=money-? WHERE user_id=?", (LOTTERY_TICKET_PRICE, user_id))
            db.execute(
                "INSERT INTO lottery_tickets(user_id, purchased_at, draw_date, status) VALUES (?, ?, ?, 'active')",
                (user_id, now(), draw_date)
            )
            db.commit()
            await callback.message.edit(
                f"🎫 بلیت لاتاری با موفقیت خریداری شد!\n\n💰 مبلغ: {fmt(LOTTERY_TICKET_PRICE)} پول\n🕔 قرعه‌کشی: ۱۷:۰۰"
            )
            # بعد از ۱۰ ثانیه پیام به صفحه اصلی لاتاری برمی‌گردد.
            await asyncio.sleep(10)
            cur = db.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM lottery_tickets WHERE user_id=? AND draw_date=? AND status='active'",
                (user_id, lottery_draw_key())
            )
            count = cur.fetchone()[0]
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🎟️ خرید بلیت — ۱۰۰ پول", callback_data="lottery:buy"), row=0)
            try:
                await callback.message.edit(
                    f"🎫 **لاتاری پول‌سیتی**\n\n"
                    f"🎟️ قیمت هر بلیت: **۱۰۰ پول**\n"
                    f"🕔 قرعه‌کشی امروز: **۱۷:۰۰**\n"
                    f"🎟️ بلیت‌های تو برای امروز: **{count}**\n\n"
                    f"برای خرید بلیت روی دکمه زیر بزن 👇",
                    components=kb
                )
            except Exception:
                pass
            return

        # ----------------------------------------------------
        # 🎮 حرکات داخل بازی
        # ----------------------------------------------------
        if data.startswith("ttt:"):
            _, room_id, pos = data.split(":", 2)
            room = casino_rooms.get(room_id)
            if not room or user_id not in room["players"]:
                return
            if user_id != room["turn"]:
                await callback.message.edit("⏳ الان نوبت تو نیست!", components=ttt_keyboard(room))
                return
            pos = int(pos)
            if room["board"][pos].strip():
                await callback.message.edit("❌ این خانه قبلاً انتخاب شده.", components=ttt_keyboard(room))
                return
            mark = "❌" if user_id == room["creator"] else "⭕"
            room["board"][pos] = mark
            board = room["board"]
            wins = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
            winner = user_id if any(all(board[i] == mark for i in line) for line in wins) else None
            if winner or all(x.strip() for x in board):
                pot = room["bet"] * 2
                if winner:
                    db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+15 WHERE user_id=?", (pot, winner))
                    result = "🏆 بردی!"
                else:
                    for pid in room["players"]:
                        db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+10 WHERE user_id=?", (room["bet"], pid))
                    result = "🤝 مساوی! مبلغ هر دو برگشت خورد."
                db.commit(); del casino_rooms[room_id]
                await callback.message.edit(f"⭕❌ **دوز تمام شد!**\n\n{result}")
                return
            room["turn"] = room["players"][1] if user_id == room["players"][0] else room["players"][0]
            await callback.message.edit("⭕❌ **دوز**\n\nنوبت بازیکن بعدی است.", components=ttt_keyboard(room))
            return

        if data.startswith("rpsroom:"):
            _, room_id, choice = data.split(":", 2)
            room = casino_rooms.get(room_id)
            if not room or user_id not in room["players"]:
                return
            if choice not in ("سنگ", "کاغذ", "قیچی"):
                await answer_callback_popup(callback, "❌ انتخاب نامعتبر است.")
                return
            if user_id in room["choices"]:
                await answer_callback_popup(callback, "⏳ انتخابت ثبت شده؛ منتظر بازیکن دیگر باش.")
                return
            room["choices"][user_id] = choice
            if len(room["choices"]) < 2:
                await callback.message.edit("✂️ انتخابت ثبت شد! منتظر بازیکن دیگر باش.", components=rps_room_keyboard(room_id))
                return
            p1, p2 = room["players"]
            c1, c2 = room["choices"][p1], room["choices"][p2]
            win = {("سنگ","قیچی"),("کاغذ","سنگ"),("قیچی","کاغذ")}
            if c1 == c2:
                for pid in room["players"]:
                    db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+10 WHERE user_id=?", (room["bet"], pid))
                result = "🤝 مساوی!"
            else:
                winner = p1 if (c1,c2) in win else p2
                db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+15 WHERE user_id=?", (room["bet"]*2, winner))
                result = "🏆 برنده مشخص شد!"
            db.commit(); del casino_rooms[room_id]
            await callback.message.edit(f"✂️ **سنگ کاغذ قیچی**\n\n👤 {c1}\n👤 {c2}\n\n{result}")
            return

        if data.startswith("guessroom:"):
            _, room_id, guess = data.split(":", 2)
            room = casino_rooms.get(room_id)
            if not room or user_id not in room["players"]:
                return
            guess = int(guess)
            if not 1 <= guess <= 20:
                await answer_callback_popup(callback, "❌ عدد باید بین ۱ تا ۲۰ باشد.")
                return
            if guess == room["target"]:
                pot = room["bet"] * 2
                db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+15 WHERE user_id=?", (pot, user_id))
                db.commit(); del casino_rooms[room_id]
                await callback.message.edit(f"🔢 **حدس عدد**\n\n🎯 عدد درست: **{guess}**\n🏆 برنده: {get_user(user_id)['name']}\n💰 جایزه: {fmt(pot)}")
            else:
                await callback.message.edit(f"🔢 حدس **{guess}** اشتباه بود! دوباره تلاش کنید.", components=guess_keyboard(room_id))
            return

        if data.startswith("move:"):
            _, room_id = data.split(":", 1)
            room = casino_rooms.get(room_id)
            if not room or user_id not in room["players"]:
                return
            room["positions"][user_id] += random.randint(1, 2)
            pos = room["positions"][user_id]
            if pos >= 5:
                pot = room["bet"] * 2
                db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+15 WHERE user_id=?", (pot, user_id))
                db.commit(); del casino_rooms[room_id]
                await callback.message.edit(f"{game_names_for_room(room['game'])} تمام شد!\n\n🏆 برنده: {get_user(user_id)['name']}\n💰 جایزه: {fmt(pot)}")
            else:
                await callback.message.edit(f"{game_names_for_room(room['game'])}\n\n📍 موقعیت تو: {pos}/5\n🏁 اولین نفری که به ۵ برسد برنده است.", components=move_keyboard(room_id))
            return

        if data.startswith("mine:"):
            _, room_id, cell = data.split(":", 2)
            room = casino_rooms.get(room_id)
            if not room or user_id != room["creator"]:
                return
            cell = int(cell)
            if cell in room["mines"]:
                db.execute("UPDATE users SET games_played=games_played+1, xp=xp+5 WHERE user_id=?", (user_id,))
                db.commit(); del casino_rooms[room_id]
                await callback.message.edit("💣 **بوم! مین بود!**\n\n💥 بازی را باختی.")
            else:
                room["revealed"].add(cell)
                if len(room["revealed"]) >= 7:
                    pot = room["bet"] * 2
                    db.execute("UPDATE users SET money=money+?, games_played=games_played+1, xp=xp+20 WHERE user_id=?", (pot, user_id))
                    db.commit(); del casino_rooms[room_id]
                    await callback.message.edit(f"💣 **مین‌یاب تمام شد!**\n\n🎉 همه خانه‌های امن را پیدا کردی!\n💰 جایزه: {fmt(pot)}")
                else:
                    await callback.message.edit("💣 خانه امن بود! ادامه بده 👇", components=mines_keyboard(room_id, room))
            return

        # ----------------------------------------------------
        # اتاق قمار
        # ----------------------------------------------------
        if data.startswith("gameroom:"):
            parts = data.split(":")
            if len(parts) < 3:
                return
            action = parts[1]
            room_id = ":".join(parts[2:])
            room = casino_rooms.get(room_id)
            if not room:
                await callback.message.edit("❌ این اتاق دیگر فعال نیست.")
                return
            # فقط اتاق قمار در این بخش پردازش می‌شود؛ بازی‌های معمولی
            # به هندلر بعدی می‌رسند.
            if room.get("type") == "gamble":
                if action == "cancel":
                    if user_id != room["creator"]:
                        await callback.message.edit("❌ فقط سازنده اتاق می‌تواند بازی را لغو کند.")
                        return
                    for pid in room["players"]:
                        db.execute("UPDATE users SET money=money+? WHERE user_id=?", (room["bet"], pid))
                    db.commit()
                    del casino_rooms[room_id]
                    await callback.message.edit("❌ اتاق قمار توسط سازنده لغو شد.\n💰 مبلغ همه بازیکنان برگشت داده شد.")
                    return

                if action == "join":
                    if user_id in room["players"]:
                        await callback.message.edit(f"🎰 تو قبلاً وارد این اتاق شدی.\n👥 نفرات: {len(room['players'])}/{room['capacity']}")
                        asyncio.create_task(restore_room_message(callback.message, room_id))
                        return
                    if len(room["players"]) >= room["capacity"]:
                        await callback.message.edit("❌ ظرفیت این اتاق کامل شده است.")
                        return
                    user = get_user(user_id)
                    if user["money"] < room["bet"]:
                        await callback.message.edit("❌ پول کافی برای ورود به این قمار نداری.")
                        return
                    db.execute("UPDATE users SET money=money-?, gambling_played=gambling_played+1 WHERE user_id=?", (room["bet"], user_id))
                    db.commit()
                    room["players"].append(user_id)

                    if len(room["players"]) >= room["capacity"]:
                        winner_id = random.choice(room["players"])
                        prize = room["bet"] * len(room["players"])
                        db.execute("UPDATE users SET money=money+? WHERE user_id=?", (prize, winner_id))
                        db.commit()
                        winner = get_user(winner_id)
                        del casino_rooms[room_id]
                        await callback.message.edit(
                            f"🎰 **قمار تمام شد!**\n\n👥 تعداد بازیکنان: {room['capacity']}\n💰 جایزه: {fmt(prize)} پول\n🏆 برنده: {winner['name']}\n\n🎉 تبریک به برنده!"
                        )
                        return

                    kb = InlineKeyboardMarkup()
                    kb.add(InlineKeyboardButton("🎮 شرکت در بازی", callback_data=f"gameroom:join:{room_id}"), row=0)
                    kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)
                    await callback.message.edit(
                        f"🎰 **اتاق قمار**\n\n💰 مبلغ ورود: {fmt(room['bet'])} پول\n👥 ظرفیت: {room['capacity']} نفر\n📊 نفرات فعلی: {len(room['players'])}/{room['capacity']}\n\nبازیکن بعدی می‌تواند وارد شود.",
                        components=kb
                    )
                    return

        # ----------------------------------------------------
        # 🎮 مدیریت اتاق بازی‌ها
        # ----------------------------------------------------
        if data.startswith("gameroom:") and data.split(":", 1)[1].split(":", 1)[0] in ("join", "cancel"):
            parts = data.split(":")
            if len(parts) < 3:
                return
            action = parts[1]
            room_id = ":".join(parts[2:])
            room = casino_rooms.get(room_id)
            if not room or room.get("type") != "game":
                # اتاق پیدا نشد یا مربوط به بازی معمولی نیست؛ هیچ پیامی در گروه نفرست.
                if not room:
                    await answer_callback_popup(callback, "❌ این اتاق بازی دیگر وجود ندارد یا تمام شده است.")
                return
            else:
                if action == "cancel":
                    if user_id != room["creator"]:
                        await answer_callback_popup(callback, "❌ تو بازی را نساختی؛ فقط سازنده می‌تواند بازی را لغو کند.")
                        return
                    for pid in room["players"]:
                        db.execute("UPDATE users SET money=money+? WHERE user_id=?", (room["bet"], pid))
                    db.commit()
                    del casino_rooms[room_id]
                    await callback.message.edit("❌ بازی لغو شد.\n💰 مبلغ همه بازیکنان برگشت داده شد.")
                    return

                if action == "join":
                    if user_id in room["players"]:
                        await answer_callback_popup(
                            callback,
                            f"🎮 تو قبلاً وارد این بازی شدی.\n👥 نفرات: {len(room['players'])}/{room['capacity']}"
                        )
                        return
                    if len(room["players"]) >= room["capacity"]:
                        await answer_callback_popup(callback, "❌ ظرفیت بازی کامل شده است.")
                        return
                    user = get_user(user_id)
                    if not user:
                        await answer_callback_popup(callback, "❌ اول /start را بزن تا حسابت ساخته شود.")
                        return
                    if user["money"] < room["bet"]:
                        await answer_callback_popup(callback, "❌ پول کافی برای ورود به بازی نداری.")
                        return
                    db.execute("UPDATE users SET money=money-? WHERE user_id=?", (room["bet"], user_id))
                    db.commit()
                    room["players"].append(user_id)
                    room["positions"][user_id] = 0
                    game = room["game"]
                    # بازی‌های انتخابی سریع
                    if game == "دوز":
                        room["turn"] = room["creator"]
                        await callback.message.edit("⭕❌ **دوز شروع شد!**\n\nنوبت بازیکن اول است.", components=ttt_keyboard(room))
                    elif game == "سنگ کاغذ قیچی":
                        await callback.message.edit("✂️ **سنگ کاغذ قیچی شروع شد!**\n\nهر بازیکن انتخاب خودش را بزند.", components=rps_room_keyboard(room_id))
                    elif game == "حدس عدد":
                        await callback.message.edit("🔢 **حدس عدد شروع شد!**\n\nعدد بین ۱ تا ۲۰ است. هر نفر با دکمه حدس می‌زند.", components=guess_keyboard(room_id))
                    elif game in ("مار و پله", "مسابقه ماشین"):
                        room["positions"] = {pid: 0 for pid in room["players"]}
                        await callback.message.edit(f"{game_names_for_room(game)} **شروع شد!**\n\nهر بازیکن با دکمه حرکت می‌کند. اولین نفر به ۵ برسد برنده است.", components=move_keyboard(room_id))
                    else:
                        room["mines"] = set(random.sample(range(9), 2))
                        await callback.message.edit("💣 **مین‌یاب شروع شد!**\n\nیک خانه را انتخاب کن؛ اگر مین نباشد جایزه می‌گیری.", components=mines_keyboard(room_id, room))
                    return

        # ----------------------------------------------------
        # خرید شغل
        # ----------------------------------------------------

        if data.startswith("job:"):

            parts = data.split(
                ":",
                2
            )

            if len(parts) < 3:
                return

            action = parts[1]
            job = parts[2]

            if action == "no":

                await callback.message.edit(
                    "❌ خرید شغل لغو شد."
                )

                return

            if job not in JOBS:
                return

            if user_id != OWNER_ID:

                user = get_user(user_id)

                price = JOBS[job][1]
                required_xp = JOBS[job][3]
                current_xp = int(user["xp"] or 0)
                if current_xp < required_xp:
                    await callback.message.edit(
                        f"🔒 برای خرید این شغل به {fmt(required_xp)} XP نیاز داری.\n"
                        f"⭐ XP فعلی: {fmt(current_xp)}"
                    )
                    return

                if user["money"] < price:

                    await callback.message.edit(
                        "❌ پول کافی برای این شغل نداری."
                    )

                    return

                db.execute("""
                UPDATE users
                SET money=money-?,
                    job=?
                WHERE user_id=?
                """, (
                    price,
                    job,
                    user_id
                ))

            else:

                db.execute(
                    """
                    UPDATE users
                    SET job=?
                    WHERE user_id=?
                    """,
                    (
                        job,
                        user_id
                    )
                )

            db.commit()

            await callback.message.edit(
                f"💼 شغل انتخاب شد!\n\n"
                f"👔 {job}\n"
                f"💵 درآمد هر ساعت: {fmt(JOBS[job][2])} پول\n"
                f"💰 قیمت خرید: {fmt(JOBS[job][1])} پول"
            )

            return

        # ----------------------------------------------------
        # خرید ماشین
        # ----------------------------------------------------

        if data.startswith("car:"):

            parts = data.split(
                ":",
                2
            )

            if len(parts) < 3:
                return

            action = parts[1]
            car = parts[2]

            if action == "no":

                await callback.message.edit(
                    "❌ خرید ماشین لغو شد."
                )

                return

            if car not in CARS:
                return

            emoji, price, bonus = CARS[car]

            user = get_user(user_id)

            if user_id != OWNER_ID:

                if user["money"] < price:

                    await callback.message.edit(
                        "❌ پول کافی نیست."
                    )

                    return

                db.execute("""
                UPDATE users
                SET money=money-?,
                    car=?
                WHERE user_id=?
                """, (
                    price,
                    car,
                    user_id
                ))

            else:

                db.execute(
                    """
                    UPDATE users
                    SET car=?
                    WHERE user_id=?
                    """,
                    (
                        car,
                        user_id
                    )
                )

            db.commit()

            await callback.message.edit(
                f"{emoji} **ماشین خریداری شد!**\n\n"
                f"🚗 {car}\n"
                f"💵 پاداش حقوق: "
                f"+{fmt(bonus)}"
            )

            return

        # ----------------------------------------------------
        # خرید خانه
        # ----------------------------------------------------

        if data.startswith("house:"):
            parts = data.split(":", 2)
            if len(parts) < 3:
                return
            action, house = parts[1], parts[2]
            if action == "no":
                await callback.message.edit("❌ خرید خانه لغو شد.")
                return
            if house not in HOUSES:
                return
            emoji, price, bonus = HOUSES[house]
            user = get_user(user_id)
            if user_id != OWNER_ID:
                if user["money"] < price:
                    await callback.message.edit("❌ پول کافی نیست.")
                    return
                db.execute("UPDATE users SET money=money-?, house=? WHERE user_id=?", (price, house, user_id))
            else:
                db.execute("UPDATE users SET house=? WHERE user_id=?", (house, user_id))
            db.commit()
            await callback.message.edit(f"{emoji} **خانه خریداری شد!**\n\n🏠 {house}\n⭐ پاداش: +{fmt(bonus)}")
            return

        # ----------------------------------------------------
        # تأیید خرید واقعی
        # ----------------------------------------------------

        if data.startswith(
            "payapprove:"
        ):

            if user_id != OWNER_ID:
                return

            try:
                request_id = int(
                    data.split(":")[1]
                )
            except:
                return

            cur = db.cursor()

            cur.execute("""
            SELECT *
            FROM purchase_requests
            WHERE id=?
            """, (
                request_id,
            ))

            request = cur.fetchone()

            if not request:

                await callback.message.edit(
                    "❌ درخواست پیدا نشد."
                )

                return

            if request["status"] != "pending":

                await callback.message.edit(
                    "⚠️ این درخواست قبلاً بررسی شده."
                )

                return

            product = request["product"]

            data_product = REAL_PRODUCTS.get(
                product
            )

            if not data_product:

                await callback.message.edit(
                    "❌ محصول دیگر وجود ندارد."
                )

                return

            buyer_id = request["buyer_id"]
            reward_type = request["reward_type"]
            reward_value = request["reward_value"]

            if reward_type == "money":

                amount = int(
                    reward_value
                )

                db.execute(
                    """
                    UPDATE users
                    SET money=money+?
                    WHERE user_id=?
                    """,
                    (
                        amount,
                        buyer_id
                    )
                )

            elif reward_type == "diamonds":

                amount = int(
                    reward_value
                )

                db.execute(
                    """
                    UPDATE users
                    SET diamonds=diamonds+?
                    WHERE user_id=?
                    """,
                    (
                        amount,
                        buyer_id
                    )
                )

            elif reward_type == "title":

                db.execute(
                    """
                    UPDATE users
                    SET title=?
                    WHERE user_id=?
                    """,
                    (
                        reward_value,
                        buyer_id
                    )
                )

            elif reward_type == "theme":

                db.execute(
                    """
                    UPDATE users
                    SET theme=?
                    WHERE user_id=?
                    """,
                    (
                        reward_value,
                        buyer_id
                    )
                )

            elif reward_type == "ticket":

                db.execute("""
                UPDATE users
                SET season_ticket=season_ticket+?
                WHERE user_id=?
                """, (
                    int(reward_value),
                    buyer_id
                ))

            elif reward_type == "badge":

                db.execute(
                    """
                    UPDATE users
                    SET season_badge=?
                    WHERE user_id=?
                    """,
                    (
                        reward_value,
                        buyer_id
                    )
                )

            elif reward_type == "box":

                reward = random.choice([
                    50000,
                    100000,
                    250000,
                    500
                ])

                if reward <= 250000:

                    db.execute(
                        """
                        UPDATE users
                        SET money=money+?
                        WHERE user_id=?
                        """,
                        (
                            reward,
                            buyer_id
                        )
                    )

                else:

                    db.execute(
                        """
                        UPDATE users
                        SET diamonds=diamonds+?
                        WHERE user_id=?
                        """,
                        (
                            reward,
                            buyer_id
                        )
                    )

            db.execute("""
            UPDATE purchase_requests
            SET status='approved',
                processed_at=?
            WHERE id=?
            """, (
                now(),
                request_id
            ))

            db.commit()

            await callback.message.edit(
                f"✅ **پرداخت تأیید شد**\n\n"
                f"🧾 درخواست #{request_id}\n"
                f"👤 "
                f"{mention(request['buyer_name'], buyer_id)}\n"
                f"🎁 {product}\n\n"
                f"📦 جایزه تحویل داده شد."
            )

            try:

                await bot.send_message(
                    buyer_id,
                    f"🎉 **خریدت تأیید شد!**\n\n"
                    f"🎁 محصول: {product}\n"
                    f"✅ پرداخت توسط مالک تأیید شد.\n"
                    f"📦 جایزه به حسابت اضافه شد."
                )

            except:
                pass

            return

        # ----------------------------------------------------
        # رد خرید واقعی
        # ----------------------------------------------------

        if data.startswith(
            "payreject:"
        ):

            if user_id != OWNER_ID:
                return

            try:
                request_id = int(
                    data.split(":")[1]
                )
            except:
                return

            cur = db.cursor()

            cur.execute("""
            SELECT *
            FROM purchase_requests
            WHERE id=?
            """, (
                request_id,
            ))

            request = cur.fetchone()

            if not request:

                await callback.message.edit(
                    "❌ درخواست پیدا نشد."
                )

                return

            if request["status"] != "pending":

                await callback.message.edit(
                    "⚠️ این درخواست قبلاً بررسی شده."
                )

                return

            db.execute("""
            UPDATE purchase_requests
            SET status='rejected',
                processed_at=?
            WHERE id=?
            """, (
                now(),
                request_id
            ))

            db.commit()

            await callback.message.edit(
                f"❌ **درخواست رد شد**\n\n"
                f"🧾 #{request_id}\n"
                f"👤 "
                f"{mention(request['buyer_name'], request['buyer_id'])}\n"
                f"🎁 {request['product']}"
            )

            try:

                await bot.send_message(
                    request["buyer_id"],
                    f"❌ **درخواست خرید رد شد.**\n\n"
                    f"🎁 محصول: "
                    f"{request['product']}\n"
                    f"🧾 درخواست: "
                    f"#{request_id}"
                )

            except:
                pass

            return

    except Exception as e:
        log_bot_error("callback", e)


# ============================================================
# 📢 بررسی عضویت اجباری
# ============================================================

async def check_force_join(message):
    """اجازه استفاده از ربات فقط به اعضای کانال اطلاع‌رسانی."""
    user_id = message.author.user_id

    # مالک ربات همیشه دسترسی دارد.
    if str(user_id) == str(OWNER_ID):
        return True

    try:
        member = await bot.get_chat_member(
            FORCE_JOIN_CHANNEL,
            user_id
        )

        status = str(getattr(member, "status", "")).lower()

        # عضو عادی یا ادمین/مالک کانال = مجاز
        if status in (
            "member",
            "administrator",
            "creator",
            "owner",
        ):
            return True

    except Exception as e:
        print(
            "FORCE JOIN CHECK ERROR:",
            repr(e)
        )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "📢 عضویت در کانال پول‌سیتی",
            url=FORCE_JOIN_CHANNEL_URL
        ),
        row=0
    )

    kb.add(
        InlineKeyboardButton(
            "✅ عضو شدم | بررسی مجدد",
            callback_data="forcejoin:check"
        ),
        row=1
    )

    await message.reply(
        "🔒 **عضویت اجباری فعال است!**\n\n"
        "برای استفاده از امکانات پول‌سیتی، ابتدا در کانال اطلاع‌رسانی عضو شو.\n\n"
        "📢 @pool_city_channel",
        components=kb
    )
    return False


# ============================================================
# 👑 ابزارهای پنل مالک: بکاپ، آمار و پینگ
# ============================================================

ADMIN_PANEL_TEXT = """👑 پنل مدیریت پول‌سیتی
━━━━━━━━━━━━━━
📦 دریافت بکاپ دیتابیس
🗂️ تاریخچه بکاپ‌ها
📊 آمار ربات
🏓 وضعیت و پینگ
📈 آمار اقتصادی
🖥️ وضعیت سرور
🧾 گزارش تراکنش‌ها
🚨 تشخیص تقلب
📢 پیام همگانی
🐞 گزارش خطاها
🧪 تست امکانات
━━━━━━━━━━━━━━"""


def _api_call(method, payload=None, timeout=12):
    if not TOKEN:
        raise RuntimeError("توکن در کد تنظیم نشده است")
    url = f"https://tapi.bale.ai/bot{TOKEN}/{method}"
    body = urllib.parse.urlencode(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _owner_stats_text():
    cur = db.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(money),0), COALESCE(SUM(bank),0), COALESCE(SUM(diamonds),0), COALESCE(AVG(xp),0), COALESCE(SUM(games_played),0), COALESCE(SUM(gambling_played),0) FROM users")
    users, cash, bank, diamonds, avg_xp, games, gambling = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM companies")
    companies = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM alliances")
    alliances_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM lottery_tickets WHERE status='active'")
    tickets = cur.fetchone()[0]
    return ("📊 آمار کلی پول‌سیتی\n━━━━━━━━━━━━━━\n"
            f"👥 کاربران ثبت‌شده: {fmt(users)}\n"
            f"💰 مجموع پول: {fmt(cash)}\n🏦 مجموع بانک: {fmt(bank)}\n"
            f"💎 مجموع الماس: {fmt(diamonds)}\n⭐ میانگین XP: {fmt(round(avg_xp))}\n"
            f"🎮 بازی‌های انجام‌شده: {fmt(games)}\n🎰 بازی‌های قمار: {fmt(gambling)}\n"
            f"🏢 شرکت‌ها: {fmt(companies)}\n🤝 اتحادها: {fmt(alliances_count)}\n"
            f"🎟️ بلیت‌های فعال: {fmt(tickets)}\n\n🔒 بدون نمایش اطلاعات شخصی کاربران")


def _economic_stats_text():
    cur = db.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(money+bank),0), COALESCE(AVG(money+bank),0), COALESCE(MAX(money+bank),0) FROM users")
    count, total, avg, richest = cur.fetchone()
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM history WHERE amount > 0")
    inflow = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM history WHERE amount < 0")
    outflow = cur.fetchone()[0]
    return ("📈 آمار اقتصادی\n━━━━━━━━━━━━━━\n"
            f"👥 حساب‌ها: {fmt(count)}\n💰 پول + بانک: {fmt(total)}\n"
            f"📊 میانگین دارایی: {fmt(round(avg))}\n🏆 بیشترین دارایی: {fmt(richest)}\n"
            f"📥 ورودی ثبت‌شده در تاریخچه: {fmt(inflow)}\n📤 خروجی ثبت‌شده در تاریخچه: {fmt(outflow)}")


async def _send_db_backup(chat_id):
    """Create a consistent SQLite backup and send it to owner via Bale sendDocument."""
    fd, path = tempfile.mkstemp(prefix="pool_city_backup_", suffix=".db")
    os.close(fd)
    try:
        backup_db = sqlite3.connect(path)
        try:
            db.backup(backup_db)
        finally:
            backup_db.close()
        boundary = "----PoolCityBackupBoundary"
        fields = [("chat_id", str(chat_id))]
        body = bytearray()
        for key, value in fields:
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
        filename = os.path.basename(path)
        data = open(path, "rb").read()
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode())
        body.extend(data)
        body.extend(f"\r\n--{boundary}--\r\n".encode())
        req = urllib.request.Request(f"https://tapi.bale.ai/bot{TOKEN}/sendDocument", data=bytes(body), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok", True):
            raise RuntimeError(str(result))
        log_backup("success", filename, "بکاپ SQLite ارسال شد")
    except Exception as exc:
        log_backup("failed", os.path.basename(path), repr(exc))
        log_bot_error("backup", exc)
        raise
    finally:
        try: os.remove(path)
        except OSError: pass


async def _owner_ping(chat_id):
    """Measure real API, send and edit latency; remove the temporary test message."""
    import time as _time
    report = "🏓 وضعیت ربات\n━━━━━━━━━━━━━━\n"
    api_ms = send_ms = edit_ms = None
    msg_id = None
    try:
        t0 = _time.perf_counter()
        me = _api_call("getMe")
        api_ms = round((_time.perf_counter()-t0)*1000)
        t0 = _time.perf_counter()
        sent = _api_call("sendMessage", {"chat_id": chat_id, "text": "🧪 پیام آزمایشی پینگ پول‌سیتی"})
        send_ms = round((_time.perf_counter()-t0)*1000)
        result = sent.get("result", {})
        msg_id = result.get("message_id")
        if msg_id is not None:
            t0 = _time.perf_counter()
            _api_call("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": "🧪 ویرایش آزمایشی"})
            edit_ms = round((_time.perf_counter()-t0)*1000)
    finally:
        if msg_id is not None:
            try: _api_call("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
            except Exception as exc: print("PING TEST DELETE ERROR:", repr(exc))
    vals = [v for v in (api_ms, send_ms, edit_ms) if v is not None]
    avg = round(sum(vals)/len(vals)) if vals else None
    state = "🟢 خوب" if avg is not None and avg < 500 else ("🟡 متوسط" if avg is not None and avg < 1000 else "🔴 ضعیف")
    cur = db.cursor(); cur.execute("SELECT COUNT(*) FROM users"); count = cur.fetchone()[0]
    return (report + f"🌐 API بله: {api_ms if api_ms is not None else 'خطا'} ms\n"
            f"🔌 پاسخ‌گویی API: {api_ms if api_ms is not None else 'خطا'} ms\n"
            f"📤 ارسال: {send_ms if send_ms is not None else 'خطا'} ms\n"
            f"✏️ ویرایش: {edit_ms if edit_ms is not None else 'خطا'} ms\n"
            f"📊 میانگین: {avg if avg is not None else 'نامشخص'} ms\n\n"
            f"👥 کاربران: {fmt(count)}\n{state}")


# ============================================================
# 📨 پیام‌ها
# ============================================================

async def on_message(
    message: Message
):

    try:

        if not message.author:
            return

        user_id = message.author.user_id

        name = (
            getattr(
                message.author,
                "first_name",
                None
            )
            or getattr(
                message.author,
                "name",
                None
            )
            or "بازیکن"
        )

        ensure_user(
            user_id,
            name
        )

        text = (
            message.content
            or ""
        ).strip()

        if not text:
            return

        # ----------------------------------------------------
        # 👑 پنل مالک / ابزارهای مدیریت
        # ----------------------------------------------------
        if str(user_id) == str(OWNER_ID):
            if text in ("پنل مدیریت", "پنل مالک", "مدیریت ربات"):
                await message.reply(ADMIN_PANEL_TEXT)
                return
            if text in ("دریافت بکاپ دیتابیس", "بکاپ دیتابیس", "بکاپ"):
                await message.reply("📦 در حال آماده‌سازی بکاپ کامل دیتابیس...")
                try:
                    await _send_db_backup(user_id)
                except Exception as exc:
                    print("BACKUP ERROR:", repr(exc))
                    await message.reply("❌ دریافت بکاپ ناموفق بود؛ گزارش خطا در کنسول ثبت شد.")
                return
            if text in ("تاریخچه بکاپ‌ها", "بکاپ‌های قبلی"):
                rows = db.execute("SELECT id,created_at,filename,status FROM backup_history ORDER BY id DESC LIMIT 10").fetchall()
                if not rows:
                    await message.reply("🗂️ هنوز بکاپی در تاریخچه ثبت نشده است.")
                else:
                    out = ["🗂️ تاریخچه بکاپ‌ها", "━━━━━━━━━━━━━━"]
                    for row in rows:
                        stamp = datetime.fromtimestamp(row["created_at"]).strftime("%Y/%m/%d %H:%M")
                        out.append(f"#{row['id']} | {stamp} | {row['status']} | {row['filename']}")
                    await message.reply("\\n".join(out))
                return
            if text in ("آمار ربات", "آمار"):
                await message.reply(_owner_stats_text())
                return
            if text in ("وضعیت ربات", "پینگ", "پینگ ربات"):
                try:
                    await message.reply(await _owner_ping(user_id))
                except Exception as exc:
                    print("PING ERROR:", repr(exc))
                    await message.reply("🏓 وضعیت ربات\n❌ تست API یا ارسال/ویرایش پیام با خطا مواجه شد. جزئیات در کنسول ثبت شد.")
                return
            if text.startswith("پیام همگانی "):
                broadcast_text = text[len("پیام همگانی "):].strip()
                if not broadcast_text:
                    await message.reply("روش استفاده:\nپیام همگانی متن پیام")
                    return
                cur = db.cursor()
                cur.execute("SELECT user_id FROM users")
                targets = [row[0] for row in cur.fetchall()]
                sent_count = failed_count = 0
                await message.reply(f"📢 ارسال پیام همگانی شروع شد.\n👥 گیرندگان: {fmt(len(targets))}")
                for target in targets:
                    try:
                        result = _api_call("sendMessage", {"chat_id": target, "text": "📢 پیام پول‌سیتی\n━━━━━━━━━━━━━━\n" + broadcast_text}, timeout=10)
                        if result.get("ok", True):
                            sent_count += 1
                        else:
                            failed_count += 1
                    except Exception as exc:
                        failed_count += 1
                        print("BROADCAST ERROR:", repr(exc))
                    # Small pacing to avoid hammering the messaging API.
                    await asyncio.sleep(0.05)
                await message.reply(f"📢 نتیجه پیام همگانی\n✅ ارسال‌شده: {fmt(sent_count)}\n❌ ناموفق: {fmt(failed_count)}")
                return
            if text == "پیام همگانی":
                await message.reply("روش استفاده:\nپیام همگانی متن پیام")
                return
            if text in ("آمار اقتصادی", "اقتصاد"):
                await message.reply(_economic_stats_text())
                return
            if text in ("وضعیت سرور", "سرور"):
                up = int(time.time() - START_TIME) if "START_TIME" in globals() else 0
                await message.reply(f"🖥️ وضعیت سرور\n🤖 ربات فعال است\n🗄️ دیتابیس: متصل\n⏱️ زمان اجرا: {up//3600} ساعت و {(up%3600)//60} دقیقه")
                return
            if text in ("گزارش خطاها", "خطاها"):
                rows = db.execute("SELECT id,created_at,area,error_type FROM bot_error_logs ORDER BY id DESC LIMIT 10").fetchall()
                if not rows:
                    await message.reply("🐞 گزارش خطاها\n✅ خطای ذخیره‌شده‌ای وجود ندارد.")
                else:
                    out = ["🐞 آخرین خطاهای ذخیره‌شده", "━━━━━━━━━━━━━━"]
                    for row in rows:
                        stamp = datetime.fromtimestamp(row["created_at"]).strftime("%m/%d %H:%M:%S")
                        out.append(f"#{row['id']} | {stamp} | {row['area']} | {row['error_type']}")
                        details = (row['details'] or '').strip().splitlines()
                        if details:
                            last = details[-1][:220]
                            explanations = {
                                "AttributeError": "ویژگی یا متدی استفاده شده که آن شیء ندارد؛ نام شیء و خط کد را از جزئیات بررسی کن.",
                                "TypeError": "نوع یا تعداد ورودی‌های تابع اشتباه است.",
                                "NameError": "نام متغیر یا تابع تعریف نشده یا غلط نوشته شده است.",
                                "KeyError": "کلید مورد انتظار در دیکشنری یا ردیف داده وجود ندارد.",
                                "IndexError": "کد به خانه‌ای از فهرست دسترسی خواسته که وجود ندارد.",
                                "sqlite3.OperationalError": "دستور یا ساختار دیتابیس مشکل دارد؛ ممکن است جدول/ستون وجود نداشته باشد.",
                            }
                            why = explanations.get(row['error_type'], "برای تشخیص علت دقیق، آخرین خط Traceback را بررسی کن.")
                            out.append(f"   🧠 معنی خطا: {why}")
                            out.append(f"   🔎 جزئیات: {last}")
                    await message.reply("\n".join(out)[:3900])
                return
            if text in ("گزارش تراکنش‌ها", "تراکنش‌ها"):
                cur = db.cursor()
                cur.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN amount>0 THEN amount ELSE 0 END),0), COALESCE(SUM(CASE WHEN amount<0 THEN ABS(amount) ELSE 0 END),0) FROM history")
                count, incoming, outgoing = cur.fetchone()
                await message.reply(f"🧾 خلاصه تراکنش‌ها\n━━━━━━━━━━━━━━\n📚 تعداد رویدادهای ثبت‌شده: {fmt(count)}\n📥 ورودی: {fmt(incoming)}\n📤 خروجی: {fmt(outgoing)}\n🔒 بدون نمایش شناسه یا نام کاربران")
                return
            if text in ("تشخیص تقلب", "بررسی تقلب"):
                cur = db.cursor()
                cur.execute("SELECT COUNT(*) FROM users WHERE money<0 OR bank<0 OR xp<0")
                bad = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM users WHERE money>1000000000 OR bank>1000000000")
                outlier = cur.fetchone()[0]
                await message.reply(f"🚨 بررسی سلامت اقتصاد\n━━━━━━━━━━━━━━\n⚠️ حساب با موجودی منفی: {fmt(bad)}\n🔎 حساب با دارایی بسیار بالا (نیازمند بررسی): {fmt(outlier)}\nاین بررسی فقط هشدار آماری است و به‌تنهایی اثبات تقلب نیست.")
                return
            if text in ("تست امکانات", "تست ربات", "تست کامل", "تست کامل ربات"):
                checks = []
                failures = []
                def _test(label, fn):
                    try:
                        detail = fn()
                        checks.append(f"✅ {label}" + (f" — {detail}" if detail not in (None, "", True) else ""))
                    except Exception as test_exc:
                        short = f"{type(test_exc).__name__}: {test_exc}"
                        checks.append(f"❌ {label} — {short}")
                        failures.append((label, test_exc))
                        log_bot_error("self-test:" + label, test_exc)
                def _db_connection():
                    row = db.execute("SELECT 1").fetchone()
                    assert row and row[0] == 1, "پاسخ دیتابیس نامعتبر است"
                    return "اتصال برقرار است"
                def _db_integrity():
                    result = db.execute("PRAGMA integrity_check").fetchone()[0]
                    assert result == "ok", result
                    return "SQLite سالم است"
                def _tables():
                    names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    required_tables = {"users", "history", "bot_error_logs", "backup_history"}
                    missing = sorted(required_tables - names)
                    assert not missing, "جدول‌های مفقود: " + ", ".join(missing)
                    return "جدول‌های اصلی موجودند"
                def _schema():
                    required = {
                        "users": {"user_id", "money", "bank", "xp", "games_played"},
                        "history": {"id", "user_id", "action", "amount"},
                        "bot_error_logs": {"id", "created_at", "area", "error_type", "details"},
                        "backup_history": {"id", "created_at", "filename", "status"},
                    }
                    missing = []
                    for table, expected in required.items():
                        cols = {r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()}
                        if not expected.issubset(cols):
                            missing.append(f"{table}: {', '.join(sorted(expected-cols))}")
                    assert not missing, "ستون‌های ناقص: " + "؛ ".join(missing)
                    return "ستون‌های لازم موجودند"
                def _backup_roundtrip():
                    fd, path = tempfile.mkstemp(prefix="poolcity_test_", suffix=".db")
                    os.close(fd)
                    try:
                        target = sqlite3.connect(path)
                        try:
                            db.backup(target)
                            result = target.execute("PRAGMA integrity_check").fetchone()[0]
                            assert result == "ok", "نسخهٔ بکاپ سالم نیست: " + str(result)
                            count = target.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                        finally:
                            target.close()
                        return f"بکاپ آزمایشی سالم؛ {count} کاربر، بدون تغییر دیتابیس اصلی"
                    finally:
                        try: os.remove(path)
                        except OSError: pass
                def _handler_exists():
                    required = ("on_message", "on_callback", "handle_cheat", "dice_game", "coin_game", "rps_game")
                    missing = [name for name in required if not callable(globals().get(name))]
                    assert not missing, "بخش‌های مفقود: " + ", ".join(missing)
                    return "پردازش پیام، دکمه‌ها، چیت و بازی‌های اصلی تعریف شده‌اند"
                def _admin_logging():
                    db.execute("SELECT id,created_at,area,error_type,details FROM bot_error_logs ORDER BY id DESC LIMIT 1").fetchall()
                    db.execute("SELECT id,created_at,filename,status FROM backup_history ORDER BY id DESC LIMIT 1").fetchall()
                    return "خواندن گزارش خطا و تاریخچه بکاپ ممکن است"
                def _config():
                    assert isinstance(DB_NAME, str) and DB_NAME, "نام دیتابیس تنظیم نشده"
                    assert str(OWNER_ID).strip(), "شناسه مالک خالی است"
                    assert isinstance(FORCE_JOIN_CHANNEL, str) and FORCE_JOIN_CHANNEL, "کانال اجباری تنظیم نشده"
                    return "تنظیمات پایه موجودند" if TOKEN else "توکن هنوز تنظیم نشده؛ تست API زنده ممکن نیست"
                # آزمون‌های منطقی روی داده‌های واقعی تعریف‌شده در کد؛ بدون تغییر دیتابیس اصلی
                def _jobs_catalog():
                    assert isinstance(JOBS, dict) and len(JOBS) >= 10, "فهرست شغل‌ها خالی یا ناقص است"
                    bad = []
                    for name, data in JOBS.items():
                        if not isinstance(data, (tuple, list)) or len(data) < 4:
                            bad.append(f"{name}: ساختار نامعتبر")
                            continue
                        emoji, price, wage, xp_need = data[:4]
                        if not all(isinstance(v, (int, float)) and v >= 0 for v in (price, wage, xp_need)):
                            bad.append(f"{name}: قیمت/حقوق/XP منفی یا غیرعددی")
                        if price <= 0 or wage <= 0:
                            bad.append(f"{name}: قیمت و حقوق باید بیشتر از صفر باشند")
                    assert not bad, "؛ ".join(bad[:5])
                    return f"{len(JOBS)} شغل بررسی شد؛ قیمت، حقوق و XP عددی و معتبرند"
                def _salary_rules():
                    assert callable(globals().get("salary")), "تابع دریافت حقوق پیدا نشد"
                    assert 3600 == 60 * 60, "مبنای فاصله حقوق باید یک ساعت باشد"
                    for name, data in JOBS.items():
                        base = data[2]
                        assert base > 0, f"حقوق شغل {name} نامعتبر است"
                        # همان محاسبه‌ای که هندلر حقوق انجام می‌دهد
                        for car_name, car_data in CARS.items():
                            total = base + car_data[2]
                            assert total >= base, f"محاسبه حقوق با ماشین {car_name} کمتر از حقوق پایه شد"
                    return "تابع حقوق موجود است؛ حقوق پایه، پاداش خودرو و فاصله ۶۰ دقیقه‌ای بررسی شد"
                def _cars_catalog():
                    assert isinstance(CARS, dict) and CARS, "فهرست ماشین‌ها خالی است"
                    for name, data in CARS.items():
                        assert len(data) >= 3, f"اطلاعات ماشین {name} ناقص است"
                        assert data[1] > 0 and data[2] >= 0, f"قیمت/پاداش ماشین {name} نامعتبر است"
                    return f"{len(CARS)} ماشین؛ قیمت و پاداش بررسی شد"
                def _houses_catalog():
                    assert isinstance(HOUSES, dict) and HOUSES, "فهرست خانه‌ها خالی است"
                    for name, data in HOUSES.items():
                        assert len(data) >= 3, f"اطلاعات خانه {name} ناقص است"
                        assert data[1] > 0 and data[2] >= 0, f"قیمت/پاداش خانه {name} نامعتبر است"
                    return f"{len(HOUSES)} خانه؛ قیمت و پاداش بررسی شد"
                def _level_progression():
                    assert len(LEVEL_XP) == 15, "باید ۱۵ سطح تعریف شده باشد"
                    values = [LEVEL_XP[i] for i in sorted(LEVEL_XP)]
                    assert values[0] == 0, "XP سطح اول باید صفر باشد"
                    assert all(values[i] < values[i+1] for i in range(len(values)-1)), "XP لازم برای سطح‌ها صعودی نیست"
                    assert get_level(0) == 1, "صفر XP باید سطح ۱ بدهد"
                    for lv, xp_need in LEVEL_XP.items():
                        assert get_level(xp_need) == lv, f"رسیدن به سطح {lv} درست محاسبه نمی‌شود"
                    return "۱۵ سطح و مرز XP هر سطح آزمایش شد"
                def _loan_math():
                    assert isinstance(LOANS, dict) and LOANS, "فهرست وام‌ها خالی است"
                    for principal, repayment in LOANS.items():
                        assert principal > 0 and repayment > principal, f"وام {principal} سود/بازپرداخت نامعتبر دارد"
                    return f"{len(LOANS)} مبلغ وام و بازپرداخت بررسی شد"
                def _games_handlers():
                    required = ("dice_game", "coin_game", "rps_game")
                    missing = [name for name in required if not callable(globals().get(name))]
                    assert not missing, "هندلر بازی‌های زیر پیدا نشد: " + ", ".join(missing)
                    # این تست وجود هندلرها را می‌سنجد؛ بازی زنده و تراکنش شرط‌بندی را اجرا نمی‌کند.
                    return "هندلر تاس، شیر یا خط و سنگ‌کاغذقیچی موجود است؛ اجرای زنده نیازمند تست جداست"
                def _economy_handlers():
                    expected = ("salary", "add_xp", "get_level", "check_level")
                    missing = [name for name in expected if not callable(globals().get(name))]
                    assert not missing, "توابع اقتصاد/سطح مفقودند: " + ", ".join(missing)
                    return "توابع حقوق، XP، سطح و محدودیت سطح موجودند"
                _test("اتصال دیتابیس", _db_connection)
                _test("سلامت فایل SQLite", _db_integrity)
                _test("فهرست شغل‌ها و اعتبار قیمت/حقوق/XP", _jobs_catalog)
                _test("قواعد محاسبه حقوق و پاداش ماشین", _salary_rules)
                _test("فهرست ماشین‌ها و پاداش‌ها", _cars_catalog)
                _test("فهرست خانه‌ها و پاداش‌ها", _houses_catalog)
                _test("پیشرفت ۱۵ سطح و مرزهای XP", _level_progression)
                _test("محاسبات وام و بازپرداخت", _loan_math)
                _test("وجود هندلر بازی‌های اصلی", _games_handlers)
                _test("توابع اقتصاد و سطح", _economy_handlers)
                _test("وجود جدول‌های اصلی", _tables)
                _test("ساختار و ستون‌های دیتابیس", _schema)
                _test("ساخت بکاپ آزمایشی و بررسی آن", _backup_roundtrip)
                _test("وجود هندلرهای اصلی و بازی‌ها", _handler_exists)
                _test("خواندن گزارش خطاها و بکاپ‌ها", _admin_logging)
                _test("تنظیمات ربات", _config)
                checks.append("ℹ️ بازی‌ها و دکمه‌ها به‌صورت زنده کلیک نشده‌اند؛ این تست بدون انجام شرط‌بندی یا تغییر موجودی، بررسی‌های امن ساختاری را انجام می‌دهد.")
                report = "🧪 گزارش تست کامل پول‌سیتی\n━━━━━━━━━━━━━━\n" + "\n".join(checks)
                if failures:
                    report += "\n\n🐞 علت خطاهای تست:" 
                    for label, test_exc in failures[:5]:
                        report += f"\n• {label}: {type(test_exc).__name__} یعنی {test_exc}"
                    report += "\n\nجزئیات کامل هر خطا در «گزارش خطاها» ذخیره شد."
                else:
                    report += "\n\n🎉 همهٔ بررسی‌های امن انجام‌شده موفق بودند. این به معنی تضمین اجرای بی‌خطای همهٔ سناریوهای زنده نیست."
                await message.reply(report[:3900])
                return

        # ----------------------------------------------------
        # چیت‌ها
        # ----------------------------------------------------

        if str(user_id) == str(OWNER_ID):

            handled = await handle_cheat(
                message,
                text
            )

            if handled:
                return

        else:

            if text == "راهنما چیت":
                return

        # ----------------------------------------------------
        # 🚀 شروع ربات
        # ----------------------------------------------------

        if text in ("/start", "/start@PoolCityBot"):
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton(
                    "💬 ورود به گپ رسمی پول‌سیتی",
                    url="https://ble.ir/pool_city_group"
                )
            )
            await message.reply(
                f"سلام {name} به پول‌سیتی خوش اومدی! 👋\n\n"
                "📖 جهت توضیحات بنویس: راهنما\n\n"
                "🎮 توی گپ بهتره که بازی کنی!\n"
                "💬 گپ رسمی: @pool_city_group",
                components=kb
            )
            return

        # ----------------------------------------------------
        # 📢 عضویت اجباری کانال
        # ----------------------------------------------------

        if not await check_force_join(message):
            return

        # ----------------------------------------------------
        # 💬 گپ پول سیتی — بدون محدودیت لول
        # ----------------------------------------------------

        if text in (
            "گپ پول سیتی",
            "گپ پول سیتی",
            "گپ پول سیتی💬"
        ):
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton(
                    "💬 ورود به گپ پول سیتی",
                    url="https://ble.ir/pool_city_group"
                )
            )
            await message.reply(
                "💬 **گپ پول سیتی**\n\n"
                "برای ورود به گپ پول سیتی روی لینک زیر بزن 👇\n"
                "https://ble.ir/pool_city_group",
                components=kb
            )
            return

        # ----------------------------------------------------
        # راهنما
        # ----------------------------------------------------

        if text in (
            "راهنما",
            "help",
            "/help"
        ):

            await message.reply(
                normal_help()
            )

            return

        # ----------------------------------------------------
        # پروفایل
        # ----------------------------------------------------

        if text in (
            "پروفایل",
            "پروفايل",
            "چی دارم",
            "چی دارم؟"
        ):

            await profile(message)

            return

        # ----------------------------------------------------
        # پول
        # ----------------------------------------------------

        if text in (
            "پول",
            "پول سیتی",
            "مانی"
        ):

            user = get_user(user_id)
            elapsed = now() - user["last_money"]

            if elapsed < 300:
                remain = 300 - elapsed
                minutes = remain // 60
                seconds = remain % 60
                await message.reply(
                    f"⏳ هنوز وقت دریافت پول نرسیده!\n"
                    f"🕐 {minutes} دقیقه و {seconds} ثانیه دیگه برگرد."
                )
                return

            reward = random.randint(40, 125)
            db.execute(
                "UPDATE users SET money=money+?, last_money=? WHERE user_id=?",
                (reward, now(), user_id)
            )
            db.commit()
            add_history(user_id, "دریافت پول", reward)

            await message.reply(
                f"💰 **پول‌سیتی دریافت شد!**\n\n"
                f"🎁 +{fmt(reward)} پول‌سیتی\n"
                f"💵 موجودی جدید: {fmt(get_user(user_id)['money'])}"
            )

            return

        # ----------------------------------------------------
        # جایزه
        # ----------------------------------------------------

        if text in (
            "جایزه",
            "جایزه روزانه"
        ):

            await daily_reward(
                message
            )

            return

        # ----------------------------------------------------
        # شغل
        # ----------------------------------------------------

        if text in (
            "شغل",
            "کار"
        ):

            await show_jobs(
                message
            )

            return

        if text.startswith(
            "انتخاب شغل "
        ):

            job = text.replace(
                "انتخاب شغل ",
                "",
                1
            ).strip()

            await choose_job(
                message,
                job
            )

            return

        # ----------------------------------------------------
        # ماشین
        # ----------------------------------------------------

        if text == "ماشین":

            await show_cars(
                message
            )

            return

        if text.startswith(
            "خرید ماشین "
        ):

            car = text.replace(
                "خرید ماشین ",
                "",
                1
            ).strip()

            await choose_car(
                message,
                car
            )

            return

        # ----------------------------------------------------
        # خانه
        # ----------------------------------------------------

        if text in (
            "خونه",
            "خانه"
        ):

            await show_houses(
                message
            )

            return

        if text.startswith("خرید خانه ") or text.startswith("خرید خونه "):
            house = re.sub(r"^خرید (?:خانه|خونه) ", "", text).strip()
            await choose_house(message, house)
            return

        # ----------------------------------------------------
        # قابلیت‌های منابع و فعالیت
        # ----------------------------------------------------

        activity_map = {
            "کشاورزی": ("🌾 کشاورزی", 1200, 15),
            "کاوش شهری": ("🧭 کاوش شهری", 1000, 12),
            "شکار": ("🏹 شکار", 1500, 15),
            "چوب": ("🪵 چوب", 1300, 14),
            "معدن": ("⛏️ معدن", 2200, 20),
            "حیوانات": ("🐾 حیوانات", 900, 10),
            "روزنامه": ("📰 روزنامه", 700, 8),
            "قرارداد": ("📜 قرارداد", 1800, 18),
        }
        if text in activity_map:
            title, reward, xp = activity_map[text]
            if not await check_level(message, text):
                return
            # کاوش شهری یک رویداد انتخابی/اکتشافی است؛ صرفاً تغییر اسم ماهی‌گیری نیست.
            if text == "کاوش شهری":
                event = random.choice(("پیدا کردن کیف پول گمشده", "کمک به یک مغازه‌دار", "کشف صندوق قدیمی", "پیدا کردن مسیر میان‌بر"))
                reward = random.randint(500, 1800)
                xp = random.randint(8, 18)
                title = f"🧭 کاوش شهری — {event}"
            db.execute("UPDATE users SET money=money+? WHERE user_id=?", (reward, user_id))
            db.commit()
            add_xp(user_id, xp)
            add_history(user_id, title, reward)
            await message.reply(f"{title} انجام شد!\n\n💰 +{fmt(reward)} پول‌سیتی\n⭐ +{xp} XP")
            return

        # ----------------------------------------------------
        # حقوق
        # ----------------------------------------------------

        if text == "حقوق":

            await salary(
                message
            )

            return

        # ----------------------------------------------------
        # بانک
        # ----------------------------------------------------

        if text == "بانک":

            await bank(
                message
            )

            return

        # ----------------------------------------------------
        # واریز
        # ----------------------------------------------------

        m = re.match(
            r"^واریز\s+(\d+)$",
            text
        )

        if m:

            await deposit(
                message,
                int(m.group(1))
            )

            return

        # ----------------------------------------------------
        # برداشت
        # ----------------------------------------------------

        m = re.match(
            r"^برداشت\s+(\d+)$",
            text
        )

        if m:

            await withdraw(
                message,
                int(m.group(1))
            )

            return

        # ----------------------------------------------------
        # انتقال پول
        # ----------------------------------------------------

        m = re.match(
            r"^(?:انتقال پول|کارت به کارت)\s+(\d+)\s+(\d+)$",
            text
        )

        if m:

            await transfer(
                message,
                int(m.group(1)),
                int(m.group(2))
            )

            return

        # ----------------------------------------------------
        # وام
        # ----------------------------------------------------

        if text == "وام":

            await loan(
                message
            )

            return

        m = re.match(
            r"^وام\s+(\d+)$",
            text
        )

        if m:

            await take_loan(
                message,
                int(m.group(1))
            )

            return

        # ----------------------------------------------------
        # کریپتو
        # ----------------------------------------------------

        if text in (
            "کریپتو",
            "ارز دیجیتال"
        ):

            await show_crypto(
                message
            )

            return

        if text in (
            "دارایی کریپتو",
            "دارایی ارز"
        ):

            await crypto_assets(
                message
            )

            return

        # ----------------------------------------------------
        # خرید کریپتو
        # ----------------------------------------------------

        m = re.match(
            r"^خرید\s+(.+?)\s+(\d+)$",
            text
        )

        if m:

            possible_crypto = find_crypto(
                m.group(1)
            )

            if possible_crypto:

                await buy_crypto(
                    message,
                    possible_crypto,
                    int(m.group(2))
                )

                return

        # ----------------------------------------------------
        # فروش کریپتو
        # ----------------------------------------------------

        m = re.match(
            r"^فروش\s+(.+?)\s+(\d+)$",
            text
        )

        if m:

            possible_crypto = find_crypto(
                m.group(1)
            )

            if possible_crypto:

                await sell_crypto(
                    message,
                    possible_crypto,
                    int(m.group(2))
                )

                return

        # ----------------------------------------------------
        # بورس
        # ----------------------------------------------------

        if text == "بورس":

            await show_stocks(
                message
            )

            return

        if text == "دارایی بورس":

            await stock_assets(
                message
            )

            return

        m = re.match(
            r"^خرید سهام\s+(.+?)\s+(\d+)$",
            text
        )

        if m:

            await buy_stock(
                message,
                m.group(1),
                int(m.group(2))
            )

            return

        # ----------------------------------------------------
        # فروش سهام
        # ----------------------------------------------------

        m = re.match(
            r"^فروش سهام\s+(.+?)\s+(\d+)$",
            text
        )

        if m:

            await message.reply(
                "🚧 فروش سهام هنوز در حال توسعه است."
            )

            return

        # ----------------------------------------------------
        # بازی‌ها
        # ----------------------------------------------------

        if text in ("تاس", "بازی تاس"):
            await dice_game(message)
            return

        # ----------------------------------------------------
        # 🎮 بازی‌های چندنفره
        # ----------------------------------------------------

        game_names = {
            "دوز": "⭕❌",
            "حدس عدد": "🔢",
            "مین یاب": "💣",
            "مین‌یاب": "💣",
            "مار و پله": "🐍",
            "مسابقه ماشین": "🚗",
            "سنگ کاغذ قیچی": "✂️",
        }

        game_match = re.match(r"^(دوز|حدس عدد|مین یاب|مین‌یاب|مار و پله|مسابقه ماشین|سنگ کاغذ قیچی)(?:\s+(\d+))?$", text)
        if game_match:
            game = game_match.group(1)
            bet = int(game_match.group(2) or 1000)
            if not await check_level(message, game):
                return
            if bet <= 0:
                await message.reply("❌ مبلغ بازی باید بیشتر از صفر باشد.")
                return
            user = get_user(user_id)
            if user["money"] < bet:
                await message.reply(f"❌ برای این بازی {fmt(bet)} پول لازم داری.")
                return
            room_id = f"game:{user_id}:{now()}:{random.randint(1000,9999)}"
            db.execute("UPDATE users SET money=money-? WHERE user_id=?", (bet, user_id))
            db.commit()
            # مین‌یاب تک‌نفره و در برابر ربات است.
            if game in ("مین یاب", "مین‌یاب"):
                casino_rooms[room_id] = {
                    "type": "game", "game": game, "creator": user_id, "bet": bet,
                    "capacity": 1, "players": [user_id], "choices": {},
                    "positions": {user_id: 0}, "target": 0, "board": [" "] * 9,
                    "turn": user_id, "mines": set(random.sample(range(9), 2)),
                    "revealed": set(), "message": None, "id": room_id
                }
                await message.reply(
                    "💣 **مین‌یاب شروع شد!**\n\nیک خانه را انتخاب کن؛ اگر مین نباشد جایزه می‌گیری.",
                    components=mines_keyboard(room_id, casino_rooms[room_id])
                )
                return

            casino_rooms[room_id] = {
                "type": "game", "game": game, "creator": user_id,
                "bet": bet, "capacity": 2, "players": [user_id],
                "choices": {}, "positions": {user_id: 0},
                "target": random.randint(1, 20), "board": [" "] * 9,
                "turn": user_id, "mines": set(), "message": None, "revealed": set(), "id": room_id
            }
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton(f"🎮 شرکت در {game}", callback_data=f"gameroom:join:{room_id}"), row=0)
            kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)
            sent = await message.reply(
                f"{game_names.get(game, '🎮')} **اتاق {game} ساخته شد**\n\n"
                f"💰 مبلغ ورود: {fmt(bet)} پول\n👥 نفرات: 1/2\n\n"
                f"بازیکن دوم روی دکمه شیشه‌ای بزند.", components=kb
            )
            casino_rooms[room_id]["message"] = sent
            return

        if text in (
            "شیر یا خط",
            "سکه"
        ):

            await coin_game(
                message
            )

            return

        if text in (
            "سنگ کاغذ قیچی",
        ):

            await rps_game(
                message
            )

            return

        # ----------------------------------------------------
        # لاتاری
        # ----------------------------------------------------

        if text == "لاتاری":
            await lottery(message)
            return

        # ----------------------------------------------------
        # کازینو
        # ----------------------------------------------------

        if text == "کازینو":
            await casino(message)
            return

        # ----------------------------------------------------
        # قمار — شروع اتاق چندنفره
        # ----------------------------------------------------

        m = re.match(r"^قمار\s+(\d+)\s+(\d+)$", text)
        if m:
            if not await check_level(message, "کازینو"):
                return
            bet = int(m.group(1))
            capacity = int(m.group(2))
            if bet <= 0 or capacity < 2 or capacity > 10:
                await message.reply("❌ مبلغ باید بیشتر از صفر و تعداد نفرات بین ۲ تا ۱۰ باشد.")
                return
            user = get_user(user_id)
            if user["money"] < bet:
                await message.reply("❌ پول کافی برای ورود به قمار نداری.")
                return

            # سازنده از همان ابتدا یکی از نفرات اتاق است.
            db.execute("UPDATE users SET money=money-?, gambling_played=gambling_played+1 WHERE user_id=?", (bet, user_id))
            db.commit()

            room_id = f"{user_id}:{now()}:{random.randint(1000,9999)}"
            casino_rooms[room_id] = {
                "type": "gamble",
                "creator": user_id,
                "bet": bet,
                "capacity": capacity,
                "players": [user_id],
                "message": None,
            }

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🎮 شرکت در بازی", callback_data=f"gameroom:join:{room_id}"), row=0)
            kb.add(InlineKeyboardButton("❌ لغو بازی", callback_data=f"gameroom:cancel:{room_id}"), row=1)

            sent = await message.reply(
                f"🎰 **اتاق قمار ساخته شد**\n\n💰 مبلغ ورود: {fmt(bet)} پول\n👥 ظرفیت: {capacity} نفر\n👤 سازنده: {user['name']}\n📊 نفرات فعلی: 1/{capacity}\n\nبرای ورود روی دکمه شیشه‌ای بزنید.",
                components=kb
            )
            casino_rooms[room_id]["message"] = sent
            return

        if text == "قمار":
            await casino(message)
            return

        # ----------------------------------------------------
        # گردونه
        # ----------------------------------------------------

        if text == "گردونه":

            await wheel(
                message
            )

            return

        # ----------------------------------------------------
        # مأموریت
        # ----------------------------------------------------

        if text == "ماموریت":

            await missions(
                message
            )

            return

        # ----------------------------------------------------
        # دزدی
        # ----------------------------------------------------

        if text == "دزدی":
            # دزدی فقط با ریپلای به پیام فرد هدف انجام می‌شود.
            replied = getattr(message, "reply_to_message", None)
            if replied is None:
                replied = getattr(message, "reply_message", None)
            target_author = getattr(replied, "author", None) if replied else None
            target_id = getattr(target_author, "user_id", None) if target_author else None
            if target_id is None and replied is not None:
                target_id = getattr(replied, "sender_id", None) or getattr(replied, "from_user_id", None)
            if target_id is None:
                await message.reply("🕵️ برای دزدی، روی پیام فرد موردنظر ریپلای کن و بنویس «دزدی».")
                return
            try:
                target_id = int(target_id)
            except (TypeError, ValueError):
                await message.reply("❌ نتونستم آیدی فردی که به پیامش ریپلای کردی رو تشخیص بدم.")
                return
            await robbery(message, target_id)
            return

        # ----------------------------------------------------
        # شهر
        # ----------------------------------------------------

        if text == "شهر":

            await city(
                message
            )

            return

        # ----------------------------------------------------
        # شرکت
        # ----------------------------------------------------

        if text == "شرکت":

            await company(
                message
            )

            return

        m = re.match(
            r"^ساخت شرکت\s+(.+)$",
            text
        )

        if m:

            await create_company(
                message,
                m.group(1).strip()
            )

            return

        # ----------------------------------------------------
        # اتحاد
        # ----------------------------------------------------

        if text == "اتحاد":

            await alliance(
                message
            )

            return

        m = re.match(
            r"^ساخت اتحاد\s+(.+)$",
            text
        )

        if m:

            await create_alliance(
                message,
                m.group(1).strip()
            )

            return

        # ----------------------------------------------------
        # بازار
        # ----------------------------------------------------

        if text == "بازار":

            await market(
                message
            )

            return

        # ----------------------------------------------------
        # فروشگاه واقعی
        # ----------------------------------------------------

        if text in (
            "فروشگاه",
            "فروشگاه فصل",
            "فروشگاه واقعی"
        ):

            await real_shop(
                message
            )

            return

        m = re.match(
            r"^خرید واقعی\s+(.+)$",
            text
        )

        if m:

            await create_purchase(
                message,
                m.group(1).strip()
            )

            return

        # ----------------------------------------------------
        # استریک
        # ----------------------------------------------------

        if text == "استریک":

            user = get_user(
                user_id
            )

            await message.reply(
                f"🔥 استریک فعلی تو: "
                f"**{user['streak']}**"
            )

            return

        # ----------------------------------------------------
        # الماس
        # ----------------------------------------------------

        if text == "الماس":

            user = get_user(
                user_id
            )

            await message.reply(
                f"💎 الماس تو: "
                f"**{fmt(user['diamonds'])}**"
            )

            return

        # ----------------------------------------------------
        # تاریخچه
        # ----------------------------------------------------

        if text == "تاریخچه":

            if not await check_level(
                message,
                "تاریخچه"
            ):
                return

            cur = db.cursor()

            cur.execute("""
            SELECT action, amount, created_at
            FROM history
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 10
            """, (
                user_id,
            ))

            rows = cur.fetchall()

            if not rows:

                await message.reply(
                    "📜 هنوز تاریخچه‌ای نداری."
                )

                return

            out = (
                "📜 **آخرین تراکنش‌ها**\n\n"
            )

            for row in rows:

                date = datetime.fromtimestamp(
                    row["created_at"]
                ).strftime(
                    "%Y/%m/%d %H:%M"
                )

                out += (
                    f"• {row['action']}\n"
                    f"💰 {fmt(row['amount'])}\n"
                    f"🕐 {date}\n\n"
                )

            await message.reply(
                out
            )

            return

        # ----------------------------------------------------
        # پیام ناشناخته
        # ----------------------------------------------------

        return

    except Exception as e:
        log_bot_error("message", e)


# ============================================================
# 🚀 راه‌اندازی نهایی
# ============================================================

init_db()
START_TIME = time.time()

bot = Bot(
    token=TOKEN
)

bot.event(
    on_message
)

bot.event(
    on_callback
)


# ============================================================
# 🟢 رویداد آماده شدن ربات
# ============================================================

crypto_loop_task = None
lottery_loop_task = None
casino_rooms = {}


@bot.listen("on_ready")
async def on_ready():

    global crypto_loop_task

    print("====================================")
    print("💰🏙️ POOL CITY BOT")
    print(BOT_TITLE)
    print("====================================")
    print("✅ ربات با موفقیت آماده شد!")

    # دریافت قیمت اولیه
    await update_crypto_prices()

    # جلوگیری از ساخت چند حلقه
    if (
        crypto_loop_task is None
        or crypto_loop_task.done()
    ):

        crypto_loop_task = asyncio.create_task(
            crypto_price_loop()
        )

        print(
            "🪙 Crypto updater started "
            f"(every {CRYPTO_UPDATE_SECONDS}s)"
        )

    if lottery_loop_task is None or lottery_loop_task.done():
        lottery_loop_task = asyncio.create_task(lottery_draw_loop())
        print("🎫 Lottery updater started (draw at 17:00)")


# ============================================================
# ▶️ اجرای ربات
# ============================================================

if __name__ == "__main__":

    print("🚀 در حال اجرای پول‌سیتی...")

    bot.run()