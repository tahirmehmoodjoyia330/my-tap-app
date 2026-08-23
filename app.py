from flask import Flask, request, session, redirect, url_for, jsonify, render_template_string
import sqlite3
import hashlib
import secrets
import time
import os
import re
from functools import wraps
from datetime import datetime, timezone, timedelta

# ============================================================
# STONE MINING NETWORK
# SINGLE FILE APP.PY
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stone.db")

MINING_TIME = 24 * 60 * 60
MINING_REWARD = 100
AD_REWARD = 25
MAX_ADS_DAY = 5
XP_MINING = 100
XP_AD = 20
XP_DAILY = 50
XP_MISSION = 75

# ------------------------------------------------------------
# IMPORTANT
# These are image slots.
# Replace these URLs with your own licensed/generated
# photorealistic car images.
# ------------------------------------------------------------

CAR_IMAGES = {
    1: "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?auto=format&fit=crop&w=1400&q=90",
    2: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1400&q=90",
    3: "https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=1400&q=90",
    4: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1400&q=90",
    5: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1400&q=90",
    6: "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1400&q=90",
    7: "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1400&q=90",
    8: "https://images.unsplash.com/photo-1493238792000-8113da705763?auto=format&fit=crop&w=1400&q=90",
    9: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1400&q=90",
    10: "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1400&q=90",
    11: "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=1400&q=90",
    12: "https://images.unsplash.com/photo-1504215680853-026ed2a45def?auto=format&fit=crop&w=1400&q=90",
    13: "https://images.unsplash.com/photo-1614200187524-dc4b892acf16?auto=format&fit=crop&w=1400&q=90",
    14: "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?auto=format&fit=crop&w=1400&q=90",
    15: "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1400&q=90",
    16: "https://images.unsplash.com/photo-1617814076668-6f7f84f1b1e0?auto=format&fit=crop&w=1400&q=90",
    17: "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?auto=format&fit=crop&w=1400&q=90",
    18: "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=1400&q=90",
    19: "https://images.unsplash.com/photo-1566023880904-8c4c5fbd0a45?auto=format&fit=crop&w=1400&q=90",
    20: "https://images.unsplash.com/photo-1504215680853-026ed2a45def?auto=format&fit=crop&w=1400&q=90",
    21: "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&w=1400&q=90",
    22: "https://images.unsplash.com/photo-1592198084033-aade902d1aae?auto=format&fit=crop&w=1400&q=90",
    23: "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1400&q=90",
    24: "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=1400&q=90",
    25: "https://images.unsplash.com/photo-1583121274602-3e2820c69888?auto=format&fit=crop&w=1400&q=90",
    26: "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=1400&q=90",
    27: "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1400&q=90",
    28: "https://images.unsplash.com/photo-1566023880904-8c4c5fbd0a45?auto=format&fit=crop&w=1400&q=90",
    29: "https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=1400&q=90",
    30: "https://images.unsplash.com/photo-1592198084033-aade902d1aae?auto=format&fit=crop&w=1400&q=90"
}


# ============================================================
# 30 LEVEL CAR ROADMAP
# ============================================================

CARS = [
    (1, "Dacia Sandero", "STARTER", "Affordable Starter"),
    (2, "Suzuki Alto", "CITY", "Urban Starter"),
    (3, "Toyota Yaris", "CITY", "City Cruiser"),
    (4, "Honda City", "CITY", "City Premium"),
    (5, "Honda Civic", "ROAD", "Road Icon"),
    (6, "Toyota Corolla", "ROAD", "Global Classic"),
    (7, "Mazda 3", "SPORT", "Sport Sedan"),
    (8, "Kia Stinger", "SPORT", "Performance"),
    (9, "Audi A4", "PREMIUM", "Executive"),
    (10, "BMW 3 Series", "PREMIUM", "BMW Class"),
    (11, "BMW 5 Series", "PREMIUM", "Executive BMW"),
    (12, "Mercedes C-Class", "LUXURY", "Luxury"),
    (13, "Mercedes E-Class", "LUXURY", "Business Luxury"),
    (14, "Audi RS5", "SPORT LUXURY", "RS Performance"),
    (15, "Mercedes AMG GT", "LUXURY", "AMG"),
    (16, "BMW M4", "M PERFORMANCE", "M Power"),
    (17, "Audi R8", "SUPERCAR", "Supercar"),
    (18, "Nissan GT-R", "SUPERCAR", "Godzilla"),
    (19, "Jaguar F-Type", "JAGUAR", "British Performance"),
    (20, "Porsche 911", "PORSCHE", "Legend"),
    (21, "Porsche Taycan", "PORSCHE", "Electric Performance"),
    (22, "Lamborghini Huracan", "LAMBORGHINI", "Italian Supercar"),
    (23, "Ferrari Roma", "FERRARI", "Italian Luxury"),
    (24, "Ferrari 296 GTB", "FERRARI", "Hybrid Supercar"),
    (25, "Lamborghini Aventador", "LAMBORGHINI", "V12 Legend"),
    (26, "McLaren 750S", "MCLAREN", "Track Weapon"),
    (27, "Aston Martin DBS", "ASTON MARTIN", "British GT"),
    (28, "Bentley Continental GT", "ULTRA LUXURY", "Grand Touring"),
    (29, "Rolls-Royce Spectre", "ROYAL", "Ultra Luxury"),
    (30, "Bugatti Chiron", "LEGENDARY", "LEVEL 30 LEGEND")
]


# ============================================================
# DATABASE
# ============================================================

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def now():
    return int(time.time())


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def init_db():

    c = db()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,

        coins INTEGER NOT NULL DEFAULT 0,
        stones INTEGER NOT NULL DEFAULT 0,

        xp INTEGER NOT NULL DEFAULT 0,
        level INTEGER NOT NULL DEFAULT 1,

        streak INTEGER NOT NULL DEFAULT 0,
        last_claim INTEGER NOT NULL DEFAULT 0,

        mining_started INTEGER NOT NULL DEFAULT 0,
        mining_claimable INTEGER NOT NULL DEFAULT 0,

        ads_today INTEGER NOT NULL DEFAULT 0,
        ads_date TEXT DEFAULT '',

        daily_claim_date TEXT DEFAULT '',

        referral_code TEXT UNIQUE,
        referred_by TEXT DEFAULT '',

        created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        kind TEXT NOT NULL,
        amount INTEGER NOT NULL,
        description TEXT NOT NULL,
        created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mission_code TEXT NOT NULL,
        progress INTEGER NOT NULL DEFAULT 0,
        target INTEGER NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0,
        date TEXT NOT NULL,
        UNIQUE(user_id, mission_code, date)
    );

    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        UNIQUE(user_id, code)
    );

    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        UNIQUE(referred_id)
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        read INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL
    );
    """)

    c.commit()
    c.close()


init_db()


# ============================================================
# SECURITY / HELPERS
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def user():

    uid = session.get("uid")

    if not uid:
        return None

    c = db()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    c.close()

    return u


def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if not user():
            return redirect("/login")

        return fn(*args, **kwargs)

    return wrapper


def level_from_xp(xp):

    return min(30, 1 + xp // 250)


def car_for_level(level):

    chosen = CARS[0]

    for car in CARS:
        if level >= car[0]:
            chosen = car

    return chosen


def next_car(level):

    for car in CARS:
        if car[0] > level:
            return car

    return None


def car_image(level):

    return CAR_IMAGES.get(level, CAR_IMAGES[1])


def transaction(uid, kind, amount, description):

    c = db()

    c.execute("""
        INSERT INTO transactions
        (user_id, kind, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        uid,
        kind,
        amount,
        description,
        now()
    ))

    c.commit()
    c.close()


def notification(uid, title, message):

    c = db()

    c.execute("""
        INSERT INTO notifications
        (user_id, title, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        uid,
        title,
        message,
        now()
    ))

    c.commit()
    c.close()


def achievement(uid, code, title):

    c = db()

    try:

        c.execute("""
            INSERT INTO achievements
            (user_id, code, title, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            uid,
            code,
            title,
            now()
        ))

        c.commit()

        notification(
            uid,
            "Achievement Unlocked 🏆",
            title
        )

    except sqlite3.IntegrityError:
        pass

    c.close()


def remaining_mining(u):

    if not u["mining_started"]:
        return 0

    if u["mining_claimable"]:
        return 0

    left = MINING_TIME - (now() - u["mining_started"])

    return max(0, left)


def refresh_mining(uid):

    c = db()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    if (
        u
        and u["mining_started"]
        and not u["mining_claimable"]
        and now() - u["mining_started"] >= MINING_TIME
    ):

        c.execute("""
            UPDATE users
            SET mining_claimable=1
            WHERE id=?
        """, (uid,))

        c.commit()

    c.close()


def daily_missions(uid):

    date = today()

    missions = [
        ("mine", "Complete Mining", 1),
        ("ad", "Watch Rewarded Ads", 3),
        ("login", "Daily Login", 1)
    ]

    c = db()

    for code, title, target in missions:

        c.execute("""
            INSERT OR IGNORE INTO missions
            (user_id, mission_code, progress, target, date)
            VALUES (?, ?, 0, ?, ?)
        """, (
            uid,
            code,
            target,
            date
        ))

    c.commit()

    rows = c.execute("""
        SELECT *
        FROM missions
        WHERE user_id=?
        AND date=?
    """, (
        uid,
        date
    )).fetchall()

    c.close()

    return rows


# ============================================================
# AUTH
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if user():
        return redirect("/")

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        referral = request.form.get("referral", "").strip()

        if not re.match(r"^[A-Za-z0-9_]{3,24}$", username):
            error = "Username: 3–24 letters, numbers or underscore."

        elif len(password) < 6:
            error = "Password must be at least 6 characters."

        else:

            c = db()

            try:

                referral_code = secrets.token_urlsafe(6)

                c.execute("""
                    INSERT INTO users
                    (username, password, referral_code, referred_by, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    username,
                    hash_password(password),
                    referral_code,
                    referral,
                    now()
                ))

                c.commit()

                uid = c.execute(
                    "SELECT id FROM users WHERE username=?",
                    (username,)
                ).fetchone()["id"]

                if referral:

                    referrer = c.execute(
                        "SELECT id FROM users WHERE referral_code=?",
                        (referral,)
                    ).fetchone()

                    if referrer and referrer["id"] != uid:

                        c.execute("""
                            INSERT OR IGNORE INTO referrals
                            (referrer_id, referred_id, created_at)
                            VALUES (?, ?, ?)
                        """, (
                            referrer["id"],
                            uid,
                            now()
                        ))

                        c.execute("""
                            UPDATE users
                            SET coins=coins+250
                            WHERE id=?
                        """, (
                            referrer["id"],
                        ))

                c.commit()
                c.close()

                session["uid"] = uid

                return redirect("/")

            except sqlite3.IntegrityError:

                c.close()

                error = "Username already exists."

    return render_template_string(
        AUTH_PAGE,
        mode="register",
        error=error
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if user():
        return redirect("/")

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        c = db()

        u = c.execute("""
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
        """, (
            username,
            hash_password(password)
        )).fetchone()

        c.close()

        if not u:

            error = "Invalid username or password."

        else:

            session["uid"] = u["id"]

            return redirect("/")

    return render_template_string(
        AUTH_PAGE,
        mode="login",
        error=error
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def home():

    u = user()

    refresh_mining(u["id"])

    u = user()

    missions = daily_missions(u["id"])

    car = car_for_level(u["level"])
    nxt = next_car(u["level"])

    xp_current = u["xp"] % 250

    xp_percent = int(
        xp_current / 250 * 100
    )

    ads = (
        u["ads_today"]
        if u["ads_date"] == today()
        else 0
    )

    return render_template_string(
        DASHBOARD,
        u=u,
        car=car,
        nxt=nxt,
        image=car_image(u["level"]),
        remaining=remaining_mining(u),
        missions=missions,
        xp_percent=xp_percent,
        ads=ads
    )


# ============================================================
# START MINING
# ============================================================

@app.post("/api/mine/start")
@login_required
def mine_start():

    u = user()

    refresh_mining(u["id"])
    u = user()

    if u["mining_started"] and not u["mining_claimable"]:

        return jsonify({
            "ok": False,
            "error": "Mining already active."
        })

    c = db()

    c.execute("""
        UPDATE users
        SET mining_started=?,
            mining_claimable=0
        WHERE id=?
    """, (
        now(),
        u["id"]
    ))

    c.commit()
    c.close()

    return jsonify({
        "ok": True,
        "remaining": MINING_TIME
    })


# ============================================================
# CLAIM MINING
# ============================================================

@app.post("/api/mine/claim")
@login_required
def mine_claim():

    u = user()

    refresh_mining(u["id"])
    u = user()

    if not u["mining_claimable"]:

        return jsonify({
            "ok": False,
            "error": "24 hours are not complete."
        })

    current = now()

    streak = 1

    if u["last_claim"]:

        diff = current - u["last_claim"]

        if diff <= 48 * 3600:
            streak = u["streak"] + 1

    stones = 1 if streak % 7 == 0 else 0

    xp = u["xp"] + XP_MINING
    level = level_from_xp(xp)

    old_level = u["level"]

    c = db()

    c.execute("""
        UPDATE users
        SET
            coins=coins+?,
            stones=stones+?,
            xp=?,
            level=?,
            streak=?,
            last_claim=?,
            mining_started=0,
            mining_claimable=0
        WHERE id=?
    """, (
        MINING_REWARD,
        stones,
        xp,
        level,
        streak,
        current,
        u["id"]
    ))

    c.commit()
    c.close()

    transaction(
        u["id"],
        "MINING",
        MINING_REWARD,
        "24H One-Tap Mining"
    )

    if stones:

        transaction(
            u["id"],
            "STONE",
            1,
            "7 Day Mining Streak"
        )

        achievement(
            u["id"],
            "stone_hunter",
            "STONE Hunter 🪨"
        )

    if level > old_level:

        achievement(
            u["id"],
            f"level_{level}",
            f"Level {level} Unlocked 🚗"
        )

        notification(
            u["id"],
            "NEW CAR UNLOCKED 🚗",
            car_for_level(level)[1]
        )

    if streak >= 3:
        achievement(
            u["id"],
            "streak_3",
            "3 Day Warrior 🔥"
        )

    if streak >= 7:
        achievement(
            u["id"],
            "streak_7",
            "7 Day Legend 🔥"
        )

    # mission
    c = db()

    c.execute("""
        UPDATE missions
        SET progress=MIN(target, progress+1)
        WHERE user_id=?
        AND mission_code='mine'
        AND date=?
    """, (
        u["id"],
        today()
    ))

    c.commit()
    c.close()

    return jsonify({
        "ok": True,
        "coins": MINING_REWARD,
        "stone": stones,
        "streak": streak,
        "level": level,
        "car": car_for_level(level)[1],
        "image": car_image(level)
    })


# ============================================================
# DAILY LOGIN
# ============================================================

@app.post("/api/daily")
@login_required
def daily_reward():

    u = user()

    if u["daily_claim_date"] == today():

        return jsonify({
            "ok": False,
            "error": "Daily reward already claimed."
        })

    xp = u["xp"] + XP_DAILY
    level = level_from_xp(xp)

    c = db()

    c.execute("""
        UPDATE users
        SET
            coins=coins+100,
            xp=?,
            level=?,
            daily_claim_date=?
        WHERE id=?
    """, (
        xp,
        level,
        today(),
        u["id"]
    ))

    c.commit()
    c.close()

    transaction(
        u["id"],
        "DAILY",
        100,
        "Daily login reward"
    )

    return jsonify({
        "ok": True,
        "reward": 100,
        "level": level
    })


# ============================================================
# REWARDED ADS
# ============================================================

@app.post("/api/ad")
@login_required
def rewarded_ad():

    u = user()

    ads = (
        u["ads_today"]
        if u["ads_date"] == today()
        else 0
    )

    if ads >= MAX_ADS_DAY:

        return jsonify({
            "ok": False,
            "error": "Daily ad limit reached."
        })

    # --------------------------------------------------------
    # PRODUCTION:
    # This endpoint must be called ONLY after a real ad
    # network confirms a rewarded completion.
    # --------------------------------------------------------

    ads += 1

    xp = u["xp"] + XP_AD
    level = level_from_xp(xp)

    c = db()

    c.execute("""
        UPDATE users
        SET
            coins=coins+?,
            xp=?,
            level=?,
            ads_today=?,
            ads_date=?
        WHERE id=?
    """, (
        AD_REWARD,
        xp,
        level,
        ads,
        today(),
        u["id"]
    ))

    c.commit()
    c.close()

    transaction(
        u["id"],
        "AD",
        AD_REWARD,
        "Rewarded advertisement"
    )

    c = db()

    c.execute("""
        UPDATE missions
        SET progress=MIN(target, progress+1)
        WHERE user_id=?
        AND mission_code='ad'
        AND date=?
    """, (
        u["id"],
        today()
    ))

    c.commit()
    c.close()

    return jsonify({
        "ok": True,
        "reward": AD_REWARD,
        "ads_left": MAX_ADS_DAY - ads,
        "level": level
    })


# ============================================================
# API STATE
# ============================================================

@app.get("/api/state")
@login_required
def state():

    u = user()

    refresh_mining(u["id"])

    u = user()

    return jsonify({
        "coins": u["coins"],
        "stones": u["stones"],
        "xp": u["xp"],
        "level": u["level"],
        "streak": u["streak"],
        "remaining": remaining_mining(u),
        "claimable": bool(u["mining_claimable"]),
        "car": car_for_level(u["level"])[1],
        "image": car_image(u["level"])
    })


# ============================================================
# CAR API
# ============================================================

@app.get("/api/car/<int:level>")
@login_required
def car_details(level):

    if level < 1 or level > 30:

        return jsonify({
            "ok": False
        }), 404

    car = CARS[level - 1]

    return jsonify({
        "level": car[0],
        "name": car[1],
        "class": car[2],
        "description": car[3],
        "image": car_image(level),
        "unlocked": user()["level"] >= level
    })


# ============================================================
# TRANSACTIONS
# ============================================================

@app.route("/history")
@login_required
def history():

    u = user()

    c = db()

    rows = c.execute("""
        SELECT *
        FROM transactions
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 100
    """, (
        u["id"],
    )).fetchall()

    c.close()

    return render_template_string(
        HISTORY,
        u=u,
        rows=rows
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

@app.route("/achievements")
@login_required
def achievements_page():

    u = user()

    c = db()

    rows = c.execute("""
        SELECT *
        FROM achievements
        WHERE user_id=?
        ORDER BY id DESC
    """, (
        u["id"],
    )).fetchall()

    c.close()

    return render_template_string(
        ACHIEVEMENTS,
        u=u,
        rows=rows
    )


# ============================================================
# LEADERBOARD
# ============================================================

@app.route("/leaderboard")
@login_required
def leaderboard():

    c = db()

    rows = c.execute("""
        SELECT username, level, xp, streak, coins
        FROM users
        ORDER BY level DESC, xp DESC
        LIMIT 50
    """).fetchall()

    c.close()

    return render_template_string(
        LEADERBOARD,
        rows=rows
    )


# ============================================================
# REFERRALS
# ============================================================

@app.route("/referrals")
@login_required
def referrals():

    u = user()

    c = db()

    count = c.execute("""
        SELECT COUNT(*)
        FROM referrals
        WHERE referrer_id=?
    """, (
        u["id"],
    )).fetchone()[0]

    c.close()

    return render_template_string(
        REFERRALS,
        u=u,
        count=count
    )


# ============================================================
# ADMIN
# ============================================================

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")


def admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        u = user()

        if not u or u["username"] != ADMIN_USERNAME:

            return "Unauthorized", 403

        return fn(*args, **kwargs)

    return wrapper


@app.route("/admin")
@admin_required
def admin():

    c = db()

    total_users = c.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_coins = c.execute(
        "SELECT COALESCE(SUM(coins),0) FROM users"
    ).fetchone()[0]

    total_stones = c.execute(
        "SELECT COALESCE(SUM(stones),0) FROM users"
    ).fetchone()[0]

    transactions = c.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()

    c.close()

    return render_template_string(
        ADMIN,
        users=total_users,
        coins=total_coins,
        stones=total_stones,
        transactions=transactions
    )


# ============================================================
# CSS
# ============================================================

CSS = r"""
* {
    box-sizing:border-box;
}

:root {
    --bg:#040506;
    --panel:#0d0f14;
    --panel2:#12151c;
    --line:#272b35;
    --purple:#886cff;
    --purple2:#b8a7ff;
    --gold:#e6c77b;
    --green:#55e6a0;
    --text:#f6f6fa;
    --muted:#858b99;
}

html {
    scroll-behavior:smooth;
}

body {
    margin:0;
    min-height:100vh;
    color:var(--text);
    font-family:Inter,Arial,sans-serif;
    background:
        radial-gradient(circle at 50% -15%,#33235c 0,transparent 42%),
        radial-gradient(circle at 100% 50%,#16102a 0,transparent 35%),
        var(--bg);
}

a {
    color:inherit;
    text-decoration:none;
}

button,
input {
    font:inherit;
}

button {
    cursor:pointer;
}

.wrap {
    width:min(1120px,calc(100% - 24px));
    margin:auto;
    padding:18px 0 70px;
}

.header {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:15px;
}

.logo {
    font-size:28px;
    font-weight:1000;
    letter-spacing:8px;
}

.logo span {
    color:var(--purple2);
}

.sub {
    color:#747a88;
    font-size:8px;
    letter-spacing:4px;
    margin-top:5px;
}

.nav {
    display:flex;
    gap:7px;
    flex-wrap:wrap;
}

.nav a {
    border:1px solid var(--line);
    border-radius:12px;
    padding:9px 11px;
    font-size:9px;
    color:#aeb2bd;
}

.wallets {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}

.wallet {
    position:relative;
    overflow:hidden;
    padding:18px;
    border:1px solid var(--line);
    border-radius:23px;
    background:linear-gradient(145deg,#151820,#090a0d);
}

.wallet:after {
    content:"";
    position:absolute;
    width:130px;
    height:130px;
    border-radius:50%;
    right:-70px;
    top:-70px;
    background:#8c70ff25;
    filter:blur(25px);
}

.wallet.stone:after {
    background:#e6c77b20;
}

.wallet small {
    display:block;
    color:var(--muted);
    letter-spacing:2px;
    font-size:9px;
}

.wallet strong {
    display:block;
    margin-top:8px;
    font-size:28px;
}

.wallet.stone strong {
    color:#ead9a5;
}

.hero {
    position:relative;
    overflow:hidden;
    margin-top:11px;
    border:1px solid var(--line);
    border-radius:28px;
    background:
        radial-gradient(circle at center,#4b347d30,transparent 55%),
        linear-gradient(145deg,#14171f,#08090c);
}

.levelbar {
    display:flex;
    justify-content:space-between;
    padding:18px 20px 0;
    color:#aeb2bd;
    font-size:10px;
    letter-spacing:2px;
}

.car {
    position:relative;
    min-height:400px;
    padding:25px 20px 30px;
    text-align:center;
    cursor:pointer;
    user-select:none;
}

.car-bg {
    position:absolute;
    inset:0;
    background-position:center;
    background-size:cover;
    opacity:.48;
    filter:saturate(1.1) contrast(1.05);
    transition:transform .8s ease,opacity .5s ease;
}

.car:before {
    content:"";
    position:absolute;
    inset:0;
    background:
        linear-gradient(180deg,#05060830,#050608c9 80%,#050608);
    z-index:1;
}

.car:hover .car-bg {
    transform:scale(1.04);
    opacity:.58;
}

.car-content {
    position:relative;
    z-index:2;
    min-height:350px;
    display:flex;
    flex-direction:column;
    justify-content:flex-end;
}

.tap {
    position:absolute;
    top:15px;
    left:50%;
    transform:translateX(-50%);
    padding:7px 12px;
    border:1px solid #ffffff25;
    border-radius:30px;
    background:#05060855;
    color:#c8cbd5;
    font-size:9px;
    letter-spacing:2px;
    backdrop-filter:blur(10px);
}

.car-name {
    font-size:clamp(29px,6vw,54px);
    font-weight:1000;
    letter-spacing:-1px;
    text-shadow:0 8px 30px #000;
}

.car-class {
    margin-top:7px;
    color:var(--purple2);
    font-size:9px;
    letter-spacing:5px;
    font-weight:900;
}

.car-details {
    display:none;
    position:absolute;
    inset:0;
    z-index:5;
    padding:30px;
    text-align:left;
    background:
        linear-gradient(90deg,#050608e8,#050608a8 55%,#05060855),
        var(--detail-image) center/cover;
    animation:openCar .35s ease;
}

.car.open .car-details {
    display:flex;
    flex-direction:column;
    justify-content:flex-end;
}

@keyframes openCar {
    from {
        opacity:0;
        transform:scale(.97);
    }
    to {
        opacity:1;
        transform:scale(1);
    }
}

.detail-badge {
    display:inline-block;
    width:max-content;
    padding:7px 11px;
    border:1px solid #ffffff28;
    border-radius:20px;
    background:#ffffff0c;
    color:var(--gold);
    font-size:9px;
    letter-spacing:2px;
}

.detail-title {
    margin-top:12px;
    font-size:clamp(32px,8vw,70px);
    font-weight:1000;
}

.detail-text {
    max-width:500px;
    color:#aeb2bd;
    font-size:12px;
    line-height:1.7;
}

.close-detail {
    position:absolute;
    right:20px;
    top:20px;
    width:40px;
    height:40px;
    border:1px solid #ffffff30;
    border-radius:50%;
    color:#fff;
    background:#0007;
    font-size:20px;
}

.xp {
    height:6px;
    margin:0 20px 20px;
    border-radius:20px;
    overflow:hidden;
    background:#252934;
}

.xp span {
    display:block;
    height:100%;
    border-radius:20px;
    background:linear-gradient(90deg,#7054ff,#c6baff);
    box-shadow:0 0 20px #8768ff55;
}

.mine {
    margin-top:11px;
    padding:27px 20px;
    border:1px solid var(--line);
    border-radius:27px;
    background:linear-gradient(145deg,#13161d,#08090c);
    text-align:center;
}

.mine-status {
    color:var(--purple2);
    font-size:9px;
    font-weight:900;
    letter-spacing:4px;
}

.timer {
    margin:13px 0 18px;
    font-size:clamp(40px,10vw,72px);
    font-weight:1000;
    letter-spacing:3px;
}

.btn {
    width:100%;
    border:0;
    padding:17px;
    border-radius:16px;
    color:#fff;
    font-weight:1000;
}

.mine-btn {
    background:linear-gradient(135deg,#7154ff,#ad98ff);
    box-shadow:0 15px 40px #795cff35;
}

.claim-btn {
    display:none;
    background:linear-gradient(135deg,#ad8134,#f1d58c);
    color:#171208;
}

.note {
    color:#777d89;
    font-size:11px;
}

.stats {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:1px;
    margin-top:11px;
    background:var(--line);
    border:1px solid var(--line);
    border-radius:21px;
    overflow:hidden;
}

.stat {
    padding:17px 8px;
    text-align:center;
    background:#101218;
}

.stat strong {
    display:block;
    font-size:18px;
}

.stat small {
    color:#777d89;
    font-size:8px;
    letter-spacing:1px;
}

.actions {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:9px;
    margin-top:11px;
}

.action {
    padding:16px 8px;
    border:1px solid var(--line);
    border-radius:17px;
    background:#101218;
    color:#d5d8df;
    text-align:center;
    font-size:10px;
    font-weight:900;
}

.section {
    margin-top:11px;
    padding:20px;
    border:1px solid var(--line);
    border-radius:25px;
    background:#101218;
}

.section h2 {
    margin:0 0 16px;
    font-size:15px;
    letter-spacing:3px;
}

.missions {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:9px;
}

.mission {
    padding:15px;
    border:1px solid #272b35;
    border-radius:16px;
    background:#0b0d11;
}

.mission strong {
    display:block;
    font-size:12px;
}

.mission small {
    display:block;
    margin-top:7px;
    color:#777d89;
}

.cars {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:8px;
}

.car-tile {
    position:relative;
    overflow:hidden;
    min-height:145px;
    padding:10px;
    border:1px solid #242833;
    border-radius:16px;
    opacity:.35;
    background:#090a0d;
}

.car-tile.unlocked {
    opacity:1;
}

.car-tile.current {
    border-color:var(--purple);
    box-shadow:0 0 25px #8768ff22;
}

.tile-image {
    position:absolute;
    inset:0;
    background-position:center;
    background-size:cover;
    opacity:.35;
}

.tile-content {
    position:relative;
    z-index:2;
    height:120px;
    display:flex;
    flex-direction:column;
    justify-content:flex-end;
}

.tile-level {
    color:#a3a7b2;
    font-size:8px;
}

.tile-name {
    margin-top:4px;
    font-size:10px;
    font-weight:900;
}

.login {
    min-height:100vh;
    display:grid;
    place-items:center;
    padding:20px;
}

.login-box {
    width:min(430px,100%);
    padding:34px 27px;
    text-align:center;
    border:1px solid var(--line);
    border-radius:28px;
    background:linear-gradient(145deg,#151820,#08090c);
    box-shadow:0 30px 100px #000b;
}

.login-logo {
    font-size:80px;
    filter:drop-shadow(0 0 35px #8768ff);
    animation:logo 1s ease;
}

@keyframes logo {
    from {
        transform:scale(.2) rotate(-20deg);
        opacity:0;
    }
    to {
        transform:scale(1) rotate(0);
        opacity:1;
    }
}

.login h1 {
    letter-spacing:8px;
}

.login small {
    color:#777d89;
    letter-spacing:3px;
}

.form {
    display:grid;
    gap:10px;
    margin-top:25px;
}

.form input {
    padding:16px;
    border:1px solid var(--line);
    border-radius:14px;
    outline:none;
    background:#06070a;
    color:#fff;
}

.form button {
    border:0;
    border-radius:14px;
    padding:16px;
    background:linear-gradient(135deg,#7154ff,#ad98ff);
    color:#fff;
    font-weight:1000;
}

.error {
    margin-top:15px;
    padding:10px;
    border-radius:10px;
    color:#ffadb5;
    background:#35171d;
    font-size:12px;
}

.table {
    overflow:auto;
}

table {
    width:100%;
    border-collapse:collapse;
}

td,th {
    padding:14px 10px;
    text-align:left;
    border-bottom:1px solid #222630;
    font-size:11px;
}

th {
    color:#8c92a0;
}

.toast {
    position:fixed;
    z-index:9999;
    left:50%;
    bottom:22px;
    transform:translate(-50%,30px);
    opacity:0;
    pointer-events:none;
    padding:13px 17px;
    border:1px solid #3b3f4a;
    border-radius:15px;
    background:#171a22;
    box-shadow:0 20px 60px #000a;
    transition:.3s;
    font-size:12px;
}

.toast.show {
    opacity:1;
    transform:translate(-50%,0);
}

.splash {
    position:fixed;
    inset:0;
    z-index:99999;
    display:grid;
    place-items:center;
    background:#040506;
    transition:.6s;
}

.splash.hide {
    opacity:0;
    visibility:hidden;
}

.splash-icon {
    font-size:100px;
    text-align:center;
    animation:logo 1.1s ease;
}

.splash-name {
    margin-top:8px;
    text-align:center;
    font-size:32px;
    font-weight:1000;
    letter-spacing:12px;
}

.loader {
    width:90px;
    height:3px;
    margin:25px auto;
    overflow:hidden;
    background:#252832;
}

.loader span {
    display:block;
    width:35%;
    height:100%;
    background:#ad98ff;
    animation:load 1s infinite;
}

@keyframes load {
    from {transform:translateX(-100%)}
    to {transform:translateX(350%)}
}

@media(max-width:700px) {

    .wrap {
        width:calc(100% - 14px);
    }

    .nav a {
        padding:7px;
    }

    .wallet strong {
        font-size:23px;
    }

    .car {
        min-height:330px;
    }

    .car-content {
        min-height:285px;
    }

    .actions {
        grid-template-columns:1fr 1fr;
    }

    .stats {
        grid-template-columns:repeat(2,1fr);
    }

    .missions {
        grid-template-columns:1fr;
    }

    .cars {
        grid-template-columns:repeat(2,1fr);
    }
}
"""


# ============================================================
# AUTH TEMPLATE
# ============================================================

AUTH_PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE</title>
<style>{{ css|safe }}</style>
</head>
<body>
<div class="login">
<div class="login-box">

<div class="login-logo">🪨</div>

<h1>STONE</h1>

<small>24H MINING NETWORK</small>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form class="form" method="post">

<input
name="username"
placeholder="Username"
required
maxlength="24">

<input
name="password"
type="password"
placeholder="Password"
required
minlength="6">

{% if mode == "register" %}
<input
name="referral"
placeholder="Referral code (optional)"
maxlength="50">
{% endif %}

<button>
{% if mode == "register" %}
CREATE ACCOUNT
{% else %}
LOGIN
{% endif %}
</button>

</form>

{% if mode == "register" %}

<a href="/login">Already registered? Login</a>

{% else %}

<a href="/register">Create new account</a>

{% endif %}

</div>
</div>
</body>
</html>
"""


# ============================================================
# DASHBOARD TEMPLATE
# ============================================================

DASHBOARD = """
<!doctype html>
<html>
<head>

<meta charset="utf-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1,maximum-scale=1">

<meta name="theme-color" content="#040506">

<title>STONE • Mining</title>

<style>{{ css|safe }}</style>

</head>

<body>

<div class="splash" id="splash">

<div>

<div class="splash-icon">🪨</div>

<div class="splash-name">STONE</div>

<div class="loader"><span></span></div>

</div>

</div>


<div class="wrap">


<header class="header">

<div>

<div class="logo">STONE<span>•</span></div>

<div class="sub">
24H MINING NETWORK
</div>

</div>

<div class="nav">

<a href="/leaderboard">🏆</a>
<a href="/achievements">🎖️</a>
<a href="/referrals">👥</a>
<a href="/history">📜</a>
<a href="/logout">EXIT</a>

</div>

</header>


<section class="wallets">

<div class="wallet">

<small>NORMAL COINS</small>

<strong id="coins">
{{ u.coins }}
</strong>

</div>


<div class="wallet stone">

<small>PREMIUM STONE 🪨</small>

<strong id="stones">
{{ u.stones }}
</strong>

</div>

</section>


<section class="hero">

<div class="levelbar">

<span>
LEVEL {{ u.level }}
</span>

<span>
{{ u.xp }} XP
</span>

</div>


<div
class="car"
id="car"
onclick="toggleCar()"
>

<div
class="car-bg"
style="background-image:url('{{ image }}')"
></div>


<div class="tap">
TAP CAR TO EXPLORE
</div>


<div class="car-content">

<div class="car-name" id="carName">
{{ car[1] }}
</div>

<div class="car-class">
{{ car[2] }}
</div>

</div>


<div
class="car-details"
id="carDetails"
style="--detail-image:url('{{ image }}')"
>

<button
class="close-detail"
onclick="closeCar(event)"
>
×
</button>

<div class="detail-badge">
LEVEL {{ car[0] }} • {{ car[2] }}
</div>

<div class="detail-title">
{{ car[1] }}
</div>

<p class="detail-text">
{{ car[3] }}. Tap anywhere outside the close button
to return to the main showcase.
</p>

</div>

</div>


<div class="xp">

<span style="width:{{ xp_percent }}%"></span>

</div>

</section>


<section class="mine">

<div
class="mine-status"
id="mineStatus"
>
{% if remaining > 0 %}
MINING ACTIVE ⛏️
{% elif u.mining_claimable %}
MINING COMPLETE ✨
{% else %}
READY TO MINE
{% endif %}
</div>


<div
class="timer"
id="timer"
>
24:00:00
</div>


<button
class="btn mine-btn"
id="mineBtn"
onclick="startMining()"
>
⛏️ 24H ONE-TAP MINING
</button>


<button
class="btn claim-btn"
id="claimBtn"
onclick="claimMining()"
>
🪙 CLAIM {{ MINING_REWARD }} COINS
</button>


<div class="note">
24 hours → mining reward
<br>
7 consecutive days → 🪨 1 STONE
</div>

</section>


<section class="stats">

<div class="stat">
<strong>🔥 {{ u.streak }}</strong>
<small>STREAK</small>
</div>

<div class="stat">
<strong>🪨 {{ 7 - (u.streak % 7) if u.streak % 7 else 7 }}</strong>
<small>DAYS TO STONE</small>
</div>

<div class="stat">
<strong>📺 {{ ads }}/{{ 5 }}</strong>
<small>ADS TODAY</small>
</div>

<div class="stat">
<strong>🚗 {{ u.level }}/30</strong>
<small>CAR LEVEL</small>
</div>

</section>


<section class="actions">

<button
class="action"
onclick="dailyReward()"
>
🎁 DAILY REWARD
</button>

<button
class="action"
onclick="watchAd()"
>
📺 AD +{{ AD_REWARD }}
</button>

<a
class="action"
href="/leaderboard"
>
🥇 LEADERBOARD
</a>

<a
class="action"
href="/referrals"
>
👥 INVITE
</a>

</section>


<section class="section">

<h2>
🎯 DAILY MISSIONS
</h2>

<div class="missions">

{% for m in missions %}

<div class="mission">

<strong>
{{ m.mission_code|upper }}
</strong>

<small>
{{ m.progress }}/{{ m.target }}
</small>

</div>

{% endfor %}

</div>

</section>


<section class="section">

<h2>
🚗 30 LEVEL CAR ROADMAP
</h2>

<div class="cars">

{% for x in range(1,31) %}

{% set cc = CARS[x-1] %}

<div
class="
car-tile
{% if u.level >= x %}unlocked{% endif %}
{% if u.level == x %}current{% endif %}
"
>

<div
class="tile-image"
style="background-image:url('{{ CAR_IMAGES[x] }}')"
></div>

<div class="tile-content">

<div class="tile-level">
LEVEL {{ x }}
</div>

<div class="tile-name">
{{ cc[1] }}
</div>

</div>

</div>

{% endfor %}

</div>

</section>


</div>


<div
class="toast"
id="toast"
></div>


<script>

let remaining = {{ remaining }};
let claimable = {{ "true" if u.mining_claimable else "false" }};


const timer =
document.getElementById("timer");

const mineBtn =
document.getElementById("mineBtn");

const claimBtn =
document.getElementById("claimBtn");

const status =
document.getElementById("mineStatus");


function toast(text) {

const t =
document.getElementById("toast");

t.textContent = text;

t.classList.add("show");

setTimeout(
() => t.classList.remove("show"),
3000
);

}


function formatTime(s) {

s = Math.max(0, s);

const h =
Math.floor(s / 3600);

const m =
Math.floor((s % 3600) / 60);

const x =
s % 60;

return [
h,m,x
]
.map(
v => String(v).padStart(2,"0")
)
.join(":");

}


function renderMining() {

if (remaining > 0) {

timer.textContent =
formatTime(remaining);

status.textContent =
"MINING ACTIVE ⛏️";

mineBtn.style.display =
"block";

claimBtn.style.display =
"none";

mineBtn.disabled = true;

return;

}


if (claimable) {

timer.textContent =
"READY";

status.textContent =
"MINING COMPLETE ✨";

mineBtn.style.display =
"none";

claimBtn.style.display =
"block";

return;

}


timer.textContent =
"24:00:00";

status.textContent =
"READY TO MINE";

mineBtn.style.display =
"block";

claimBtn.style.display =
"none";

mineBtn.disabled = false;

}


setInterval(() => {

if (remaining > 0) {

remaining--;

if (remaining <= 0) {

remaining = 0;

claimable = true;

}

renderMining();

}

},1000);


async function startMining() {

try {

const r =
await fetch(
"/api/mine/start",
{
method:"POST"
}
);

const data =
await r.json();

if (!data.ok) {

toast(data.error);

return;

}

remaining =
data.remaining;

claimable = false;

renderMining();

toast(
"⛏️ 24H mining started!"
);

}

catch {

toast(
"Network error."
);

}

}


async function claimMining() {

try {

const r =
await fetch(
"/api/mine/claim",
{
method:"POST"
}
);

const data =
await r.json();

if (!data.ok) {

toast(data.error);

return;

}

if (data.stone) {

toast(
"🔥 7 DAY STREAK → +1 STONE 🪨"
);

} else {

toast(
"⛏️ +100 COINS MINED!"
);

}

setTimeout(
() => location.reload(),
1000
);

}

catch {

toast(
"Network error."
);

}

}


async function dailyReward() {

try {

const r =
await fetch(
"/api/daily",
{
method:"POST"
}
);

const data =
await r.json();

if (!data.ok) {

toast(data.error);

return;

}

toast(
"🎁 +"+data.reward+" DAILY COINS!"
);

setTimeout(
() => location.reload(),
800
);

}

catch {

toast(
"Network error."
);

}

}


async function watchAd() {

const confirmAd =
confirm(
"Rewarded Ad Demo\\n\\n" +
"In production, a verified ad network should " +
"confirm the completed advertisement.\\n\\n" +
"Continue demo reward?"
);

if (!confirmAd)
return;


try {

const r =
await fetch(
"/api/ad",
{
method:"POST"
}
);

const data =
await r.json();

if (!data.ok) {

toast(data.error);

return;

}

toast(
"📺 +"+data.reward+" COINS!"
);

setTimeout(
() => location.reload(),
800
);

}

catch {

toast(
"Network error."
);

}

}


function toggleCar() {

document
.getElementById("car")
.classList.toggle("open");

}


function closeCar(event) {

event.stopPropagation();

document
.getElementById("car")
.classList.remove("open");

}


document
.getElementById("carDetails")
.addEventListener(
"click",
function(e) {

if (
e.target === this
) {

document
.getElementById("car")
.classList.remove("open");

}

}
);


renderMining();


setTimeout(
() => {

document
.getElementById("splash")
.classList.add("hide");

},
1600
);

</script>

</body>
</html>
"""


# ============================================================
# HISTORY TEMPLATE
# ============================================================

HISTORY = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE History</title>
<style>{{ css|safe }}</style>
</head>
<body>

<div class="wrap">

<header class="header">
<div>
<div class="logo">STONE<span>•</span></div>
<div class="sub">TRANSACTION CENTER</div>
</div>

<div class="nav">
<a href="/">← HOME</a>
</div>
</header>

<section class="section">

<h2>📜 TRANSACTION HISTORY</h2>

<div class="table">

<table>

<tr>
<th>TYPE</th>
<th>AMOUNT</th>
<th>DESCRIPTION</th>
<th>DATE</th>
</tr>

{% for x in rows %}

<tr>

<td>{{ x.kind }}</td>

<td>+{{ x.amount }}</td>

<td>{{ x.description }}</td>

<td>
{{ x.created_at }}
</td>

</tr>

{% endfor %}

</table>

</div>

</section>

</div>

</body>
</html>
"""


# ============================================================
# ACHIEVEMENTS TEMPLATE
# ============================================================

ACHIEVEMENTS = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE Achievements</title>
<style>{{ css|safe }}</style>
</head>
<body>

<div class="wrap">

<header class="header">

<div>
<div class="logo">STONE<span>•</span></div>
<div class="sub">ACHIEVEMENT CENTER</div>
</div>

<div class="nav">
<a href="/">← HOME</a>
</div>

</header>

<section class="section">

<h2>🏆 ACHIEVEMENTS</h2>

{% if rows %}

{% for x in rows %}

<div class="mission">

<strong>
✦ {{ x.title }}
</strong>

<small>
Unlocked {{ x.created_at }}
</small>

</div>

{% endfor %}

{% else %}

<p class="note">
Your first achievement is waiting.
</p>

{% endif %}

</section>

</div>

</body>
</html>
"""


# ============================================================
# LEADERBOARD TEMPLATE
# ============================================================

LEADERBOARD = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE Leaderboard</title>
<style>{{ css|safe }}</style>
</head>

<body>

<div class="wrap">

<header class="header">

<div>
<div class="logo">STONE<span>•</span></div>
<div class="sub">GLOBAL LEADERBOARD</div>
</div>

<div class="nav">
<a href="/">← HOME</a>
</div>

</header>

<section class="section">

<h2>🥇 TOP MINERS</h2>

<div class="table">

<table>

<tr>
<th>#</th>
<th>MINER</th>
<th>LEVEL</th>
<th>XP</th>
<th>STREAK</th>
<th>COINS</th>
</tr>

{% for x in rows %}

<tr>

<td>{{ loop.index }}</td>

<td>{{ x.username }}</td>

<td>{{ x.level }}</td>

<td>{{ x.xp }}</td>

<td>🔥 {{ x.streak }}</td>

<td>{{ x.coins }}</td>

</tr>

{% endfor %}

</table>

</div>

</section>

</div>

</body>
</html>
"""


# ============================================================
# REFERRAL TEMPLATE
# ============================================================

REFERRALS = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE Referrals</title>
<style>{{ css|safe }}</style>
</head>

<body>

<div class="wrap">

<header class="header">

<div>
<div class="logo">STONE<span>•</span></div>
<div class="sub">REFERRAL NETWORK</div>
</div>

<div class="nav">
<a href="/">← HOME</a>
</div>

</header>

<section class="section">

<h2>👥 INVITE & EARN</h2>

<p class="note">
Share your referral code with friends.
</p>

<div class="mission">

<strong>
YOUR REFERRAL CODE
</strong>

<small>
{{ u.referral_code }}
</small>

</div>

<div class="mission">

<strong>
FRIENDS JOINED
</strong>

<small>
{{ count }}
</small>

</div>

</section>

</div>

</body>
</html>
"""


# ============================================================
# ADMIN TEMPLATE
# ============================================================

ADMIN = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STONE Admin</title>
<style>{{ css|safe }}</style>
</head>

<body>

<div class="wrap">

<header class="header">

<div>
<div class="logo">STONE<span>•</span></div>
<div class="sub">ADMIN CONTROL CENTER</div>
</div>

<div class="nav">
<a href="/">HOME</a>
</div>

</header>

<section class="stats">

<div class="stat">
<strong>{{ users }}</strong>
<small>USERS</small>
</div>

<div class="stat">
<strong>{{ coins }}</strong>
<small>COINS</small>
</div>

<div class="stat">
<strong>{{ stones }}</strong>
<small>STONE</small>
</div>

<div class="stat">
<strong>30</strong>
<small>LEVELS</small>
</div>

</section>

<section class="section">

<h2>RECENT TRANSACTIONS</h2>

<div class="table">

<table>

<tr>
<th>USER</th>
<th>TYPE</th>
<th>AMOUNT</th>
<th>DESCRIPTION</th>
</tr>

{% for x in transactions %}

<tr>
<td>{{ x.user_id }}</td>
<td>{{ x.kind }}</td>
<td>{{ x.amount }}</td>
<td>{{ x.description }}</td>
</tr>

{% endfor %}

</table>

</div>

</section>

</div>

</body>
</html>
"""


# ============================================================
# TEMPLATE GLOBALS
# ============================================================

@app.context_processor
def globals_for_templates():

    return {
        "css": CSS,
        "CARS": CARS,
        "CAR_IMAGES": CAR_IMAGES,
        "MINING_REWARD": MINING_REWARD,
        "AD_REWARD": AD_REWARD
    }


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )