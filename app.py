from flask import Flask, request, session, redirect, url_for, jsonify, render_template_string
import sqlite3
import hashlib
import secrets
import time
import os
from datetime import datetime, timezone

# ============================================================
# STONE — 24H ONE-TAP MINING
# Single-file Flask application
# ============================================================

app = Flask(__name__)

# IMPORTANT:
# Set a strong SECRET_KEY in your hosting environment.
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stone.db")

MINING_DURATION = 24 * 60 * 60
MINING_REWARD = 100
AD_REWARD = 25
MAX_ADS_PER_DAY = 5
XP_PER_MINING = 100
XP_PER_AD = 20
STONE_STREAK_DAYS = 7


# ============================================================
# CAR / LEVEL SYSTEM
# ============================================================

CARS = [
    {"level": 1, "name": "Dacia Sandero", "class": "STARTER"},
    {"level": 2, "name": "Suzuki Alto", "class": "CITY"},
    {"level": 3, "name": "Toyota Yaris", "class": "CITY"},
    {"level": 4, "name": "Honda City", "class": "CITY"},
    {"level": 5, "name": "Honda Civic", "class": "ROAD"},
    {"level": 6, "name": "Toyota Corolla", "class": "ROAD"},
    {"level": 7, "name": "Mazda 3", "class": "SPORT"},
    {"level": 8, "name": "Kia Stinger", "class": "SPORT"},
    {"level": 9, "name": "Audi A4", "class": "PREMIUM"},
    {"level": 10, "name": "BMW 3 Series", "class": "PREMIUM"},
    {"level": 11, "name": "BMW 5 Series", "class": "PREMIUM"},
    {"level": 12, "name": "Mercedes C-Class", "class": "LUXURY"},
    {"level": 13, "name": "Mercedes E-Class", "class": "LUXURY"},
    {"level": 14, "name": "Audi RS5", "class": "SPORT LUXURY"},
    {"level": 15, "name": "Mercedes AMG GT", "class": "LUXURY"},
    {"level": 16, "name": "BMW M4", "class": "M PERFORMANCE"},
    {"level": 17, "name": "Audi R8", "class": "SUPERCAR"},
    {"level": 18, "name": "Nissan GT-R", "class": "SUPERCAR"},
    {"level": 19, "name": "Jaguar F-Type", "class": "JAGUAR"},
    {"level": 20, "name": "Porsche 911", "class": "PORSCHE"},
    {"level": 21, "name": "Porsche Taycan", "class": "PORSCHE"},
    {"level": 22, "name": "Lamborghini Huracan", "class": "LAMBORGHINI"},
    {"level": 23, "name": "Ferrari Roma", "class": "FERRARI"},
    {"level": 24, "name": "Ferrari 296 GTB", "class": "FERRARI"},
    {"level": 25, "name": "Lamborghini Aventador", "class": "LAMBORGHINI"},
    {"level": 26, "name": "McLaren 750S", "class": "MCLAREN"},
    {"level": 27, "name": "Aston Martin DBS", "class": "ASTON MARTIN"},
    {"level": 28, "name": "Bentley Continental GT", "class": "ULTRA LUXURY"},
    {"level": 29, "name": "Rolls-Royce Spectre", "class": "ROYAL"},
    {"level": 30, "name": "Bugatti Chiron", "class": "LEGENDARY"},
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    db = get_db()

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,

            coins INTEGER DEFAULT 0,
            stones INTEGER DEFAULT 0,

            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,

            streak INTEGER DEFAULT 0,
            last_mining_claim INTEGER DEFAULT 0,

            mining_started INTEGER DEFAULT 0,
            mining_claimable INTEGER DEFAULT 0,

            ads_today INTEGER DEFAULT 0,
            ads_date TEXT DEFAULT '',

            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            UNIQUE(user_id, code)
        );
    """)

    db.commit()
    db.close()


# ============================================================
# HELPERS
# ============================================================

def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    db.close()

    return user


def current_timestamp():
    return int(time.time())


def current_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_level_from_xp(xp):
    """
    Every 250 XP = one level.
    Maximum level = 30.
    """
    level = 1 + (xp // 250)

    if level > 30:
        level = 30

    return level


def get_current_car(level):
    selected = CARS[0]

    for car in CARS:
        if level >= car["level"]:
            selected = car

    return selected


def get_next_car(level):
    for car in CARS:
        if car["level"] > level:
            return car

    return None


def add_transaction(user_id, transaction_type, amount, description):
    db = get_db()

    db.execute("""
        INSERT INTO transactions
        (user_id, transaction_type, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        transaction_type,
        amount,
        description,
        current_timestamp()
    ))

    db.commit()
    db.close()


def update_level(user_id):
    db = get_db()

    user = db.execute(
        "SELECT xp, level FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user:
        db.close()
        return 1

    new_level = get_level_from_xp(user["xp"])

    if new_level != user["level"]:
        db.execute(
            "UPDATE users SET level = ? WHERE id = ?",
            (new_level, user_id)
        )
        db.commit()

    db.close()

    return new_level


def unlock_achievement(user_id, code, title):
    db = get_db()

    try:
        db.execute("""
            INSERT INTO achievements
            (user_id, code, title)
            VALUES (?, ?, ?)
        """, (
            user_id,
            code,
            title
        ))

        db.commit()
        created = True

    except sqlite3.IntegrityError:
        created = False

    db.close()

    return created


def calculate_mining_remaining(user):
    if not user:
        return 0

    if not user["mining_started"]:
        return 0

    if user["mining_claimable"]:
        return 0

    elapsed = current_timestamp() - user["mining_started"]

    remaining = MINING_DURATION - elapsed

    if remaining <= 0:
        return 0

    return remaining


def refresh_mining_state(user_id):
    """
    Marks a mining session claimable when its 24 hours have elapsed.
    """

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user:
        db.close()
        return

    if (
        user["mining_started"]
        and not user["mining_claimable"]
        and current_timestamp() - user["mining_started"] >= MINING_DURATION
    ):
        db.execute("""
            UPDATE users
            SET mining_claimable = 1
            WHERE id = ?
        """, (user_id,))

        db.commit()

    db.close()


# ============================================================
# AUTHENTICATION
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if get_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3:
            return render_template_string(
                AUTH_HTML,
                mode="register",
                error="Username must contain at least 3 characters."
            )

        if len(password) < 6:
            return render_template_string(
                AUTH_HTML,
                mode="register",
                error="Password must contain at least 6 characters."
            )

        db = get_db()

        try:

            db.execute("""
                INSERT INTO users
                (
                    username,
                    password,
                    created_at
                )
                VALUES (?, ?, ?)
            """, (
                username,
                password_hash(password),
                current_timestamp()
            ))

            db.commit()

            user = db.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            session["user_id"] = user["id"]

            db.close()

            return redirect(url_for("dashboard"))

        except sqlite3.IntegrityError:

            db.close()

            return render_template_string(
                AUTH_HTML,
                mode="register",
                error="That username already exists."
            )

    return render_template_string(
        AUTH_HTML,
        mode="register",
        error=None
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if get_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        user = db.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password_hash(password)
        )).fetchone()

        db.close()

        if not user:

            return render_template_string(
                AUTH_HTML,
                mode="login",
                error="Invalid username or password."
            )

        session["user_id"] = user["id"]

        return redirect(url_for("dashboard"))

    return render_template_string(
        AUTH_HTML,
        mode="login",
        error=None
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# MAIN DASHBOARD
# ============================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    refresh_mining_state(user["id"])

    user = get_user()

    remaining = calculate_mining_remaining(user)

    current_car = get_current_car(user["level"])
    next_car = get_next_car(user["level"])

    xp_inside_level = user["xp"] % 250
    xp_percent = int((xp_inside_level / 250) * 100)

    today = current_date()

    ads_used = user["ads_today"]

    if user["ads_date"] != today:
        ads_used = 0

    return render_template_string(
        DASHBOARD_HTML,
        user=user,
        remaining=remaining,
        current_car=current_car,
        next_car=next_car,
        xp_percent=xp_percent,
        ads_used=ads_used,
        max_ads=MAX_ADS_PER_DAY,
        cars=CARS,
        mining_reward=MINING_REWARD,
        ad_reward=AD_REWARD
    )


# ============================================================
# START MINING
# ============================================================

@app.post("/api/start-mining")
def start_mining():

    user = get_user()

    if not user:
        return jsonify({
            "success": False,
            "error": "Login required."
        }), 401

    refresh_mining_state(user["id"])

    user = get_user()

    if user["mining_started"] and not user["mining_claimable"]:

        remaining = calculate_mining_remaining(user)

        return jsonify({
            "success": False,
            "error": "Mining is already active.",
            "remaining": remaining
        })

    db = get_db()

    started = current_timestamp()

    db.execute("""
        UPDATE users
        SET
            mining_started = ?,
            mining_claimable = 0
        WHERE id = ?
    """, (
        started,
        user["id"]
    ))

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "started": started,
        "duration": MINING_DURATION
    })


# ============================================================
# CLAIM MINING
# ============================================================

@app.post("/api/claim-mining")
def claim_mining():

    user = get_user()

    if not user:
        return jsonify({
            "success": False,
            "error": "Login required."
        }), 401

    refresh_mining_state(user["id"])

    user = get_user()

    if not user["mining_started"]:

        return jsonify({
            "success": False,
            "error": "No active mining session."
        })

    if not user["mining_claimable"]:

        remaining = calculate_mining_remaining(user)

        return jsonify({
            "success": False,
            "error": "Mining has not completed yet.",
            "remaining": remaining
        })

    # --------------------------------------------------------
    # STREAK
    # --------------------------------------------------------

    now = current_timestamp()

    previous_claim = user["last_mining_claim"]

    new_streak = 1

    if previous_claim:

        difference = now - previous_claim

        # Approximate one-day continuity.
        # A grace period of 48h prevents small timing issues.
        if difference <= 48 * 60 * 60:
            new_streak = user["streak"] + 1

    stone_reward = 0

    if new_streak % STONE_STREAK_DAYS == 0:
        stone_reward = 1

    # --------------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------------

    new_xp = user["xp"] + XP_PER_MINING
    new_level = get_level_from_xp(new_xp)

    db = get_db()

    db.execute("""
        UPDATE users
        SET
            coins = coins + ?,
            stones = stones + ?,
            xp = ?,
            level = ?,
            streak = ?,
            last_mining_claim = ?,
            mining_started = 0,
            mining_claimable = 0
        WHERE id = ?
    """, (
        MINING_REWARD,
        stone_reward,
        new_xp,
        new_level,
        new_streak,
        now,
        user["id"]
    ))

    db.commit()
    db.close()

    add_transaction(
        user["id"],
        "MINING",
        MINING_REWARD,
        "24H ONE-TAP MINING reward"
    )

    if stone_reward:

        add_transaction(
            user["id"],
            "STONE",
            stone_reward,
            "7-day mining streak reward"
        )

        unlock_achievement(
            user["id"],
            "first_stone",
            "STONE Hunter"
        )

    if new_streak >= 3:
        unlock_achievement(
            user["id"],
            "three_day_streak",
            "3 Day Warrior"
        )

    if new_streak >= 7:
        unlock_achievement(
            user["id"],
            "seven_day_streak",
            "7 Day Legend"
        )

    if new_level >= 10:
        unlock_achievement(
            user["id"],
            "level_10",
            "Level 10"
        )

    if new_level >= 20:
        unlock_achievement(
            user["id"],
            "level_20",
            "Level 20"
        )

    if new_level >= 30:
        unlock_achievement(
            user["id"],
            "level_30",
            "LEGENDARY LEVEL 30"
        )

    return jsonify({
        "success": True,
        "coins": MINING_REWARD,
        "stone": stone_reward,
        "streak": new_streak,
        "xp": new_xp,
        "level": new_level,
        "car": get_current_car(new_level)["name"]
    })


# ============================================================
# REWARDED ADS
# ============================================================

@app.post("/api/rewarded-ad")
def rewarded_ad():

    user = get_user()

    if not user:
        return jsonify({
            "success": False,
            "error": "Login required."
        }), 401

    today = current_date()

    if user["ads_date"] == today:
        ads_used = user["ads_today"]
    else:
        ads_used = 0

    if ads_used >= MAX_ADS_PER_DAY:

        return jsonify({
            "success": False,
            "error": "Daily rewarded-ad limit reached."
        })

    ads_used += 1

    new_xp = user["xp"] + XP_PER_AD
    new_level = get_level_from_xp(new_xp)

    db = get_db()

    db.execute("""
        UPDATE users
        SET
            coins = coins + ?,
            xp = ?,
            level = ?,
            ads_today = ?,
            ads_date = ?
        WHERE id = ?
    """, (
        AD_REWARD,
        new_xp,
        new_level,
        ads_used,
        today,
        user["id"]
    ))

    db.commit()
    db.close()

    add_transaction(
        user["id"],
        "AD",
        AD_REWARD,
        "Rewarded advertisement bonus"
    )

    return jsonify({
        "success": True,
        "reward": AD_REWARD,
        "ads_used": ads_used,
        "ads_remaining": MAX_ADS_PER_DAY - ads_used,
        "level": new_level
    })


# ============================================================
# API STATE
# ============================================================

@app.get("/api/state")
def api_state():

    user = get_user()

    if not user:
        return jsonify({
            "success": False
        }), 401

    refresh_mining_state(user["id"])

    user = get_user()

    remaining = calculate_mining_remaining(user)

    return jsonify({
        "success": True,
        "username": user["username"],
        "coins": user["coins"],
        "stones": user["stones"],
        "xp": user["xp"],
        "level": user["level"],
        "streak": user["streak"],
        "remaining": remaining,
        "claimable": bool(user["mining_claimable"]),
        "car": get_current_car(user["level"])["name"],
        "car_class": get_current_car(user["level"])["class"]
    })


# ============================================================
# TRANSACTION HISTORY
# ============================================================

@app.route("/history")
def history():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    transactions = db.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 100
    """, (
        user["id"],
    )).fetchall()

    db.close()

    return render_template_string(
        HISTORY_HTML,
        user=user,
        transactions=transactions
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

@app.route("/achievements")
def achievements():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    achievements = db.execute("""
        SELECT *
        FROM achievements
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user["id"],
    )).fetchall()

    db.close()

    return render_template_string(
        ACHIEVEMENTS_HTML,
        user=user,
        achievements=achievements
    )


# ============================================================
# CSS
# ============================================================

CSS = r"""
:root {
    --bg: #050608;
    --panel: #101217;
    --panel2: #151821;
    --border: #292d38;
    --purple: #8768ff;
    --purple2: #b29cff;
    --gold: #e8c77b;
    --text: #f7f7fa;
    --muted: #858996;
    --green: #54e69a;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background:
        radial-gradient(circle at 50% -20%, #241a48 0%, transparent 45%),
        radial-gradient(circle at 100% 50%, #15102b 0%, transparent 35%),
        var(--bg);
    color: var(--text);
    font-family: Inter, Arial, sans-serif;
    min-height: 100vh;
}

button,
input {
    font: inherit;
}

button {
    cursor: pointer;
}

a {
    color: inherit;
    text-decoration: none;
}

.container {
    width: min(1100px, calc(100% - 28px));
    margin: auto;
    padding: 20px 0 60px;
}

/* SPLASH */

#splash {
    position: fixed;
    inset: 0;
    z-index: 99999;
    display: grid;
    place-items: center;
    background: #050608;
    transition: opacity .6s ease, visibility .6s ease;
}

#splash.hidden {
    opacity: 0;
    visibility: hidden;
}

.splash-inner {
    text-align: center;
}

.splash-icon {
    font-size: 95px;
    animation: logoPop 1.1s ease;
    filter: drop-shadow(0 0 40px #8a68ff);
}

.splash-title {
    margin-top: 10px;
    font-weight: 900;
    letter-spacing: 12px;
    font-size: 32px;
}

.splash-sub {
    color: #777b88;
    font-size: 10px;
    letter-spacing: 4px;
    margin-top: 10px;
}

.loader {
    width: 80px;
    height: 3px;
    margin: 28px auto 0;
    overflow: hidden;
    background: #232631;
    border-radius: 10px;
}

.loader span {
    display: block;
    height: 100%;
    width: 40%;
    background: var(--purple2);
    animation: loading 1s infinite;
}

@keyframes logoPop {
    0% {
        transform: scale(.3) rotate(-25deg);
        opacity: 0;
    }

    65% {
        transform: scale(1.15) rotate(7deg);
    }

    100% {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes loading {
    0% {
        transform: translateX(-100%);
    }

    100% {
        transform: translateX(300%);
    }
}

/* HEADER */

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
}

.logo {
    font-size: 28px;
    font-weight: 950;
    letter-spacing: 7px;
}

.logo span {
    color: var(--purple2);
}

.network {
    color: var(--muted);
    font-size: 9px;
    letter-spacing: 3px;
    margin-top: 5px;
}

.logout {
    border: 1px solid var(--border);
    padding: 9px 13px;
    border-radius: 13px;
    color: #aaaeba;
    font-size: 12px;
}

/* WALLETS */

.wallet-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 13px;
}

.wallet {
    position: relative;
    overflow: hidden;
    padding: 20px;
    border: 1px solid var(--border);
    border-radius: 23px;
    background: linear-gradient(145deg, #151821, #0b0c10);
    box-shadow: 0 20px 60px #0008;
}

.wallet::after {
    content: "";
    position: absolute;
    width: 130px;
    height: 130px;
    right: -70px;
    top: -70px;
    background: #8768ff22;
    border-radius: 50%;
    filter: blur(15px);
}

.wallet.stone::after {
    background: #e8c77b20;
}

.wallet-label {
    display: block;
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 2px;
}

.wallet-value {
    display: block;
    font-size: 29px;
    font-weight: 900;
    margin-top: 7px;
}

.stone-value {
    color: #ead8a1;
}

/* CAR HERO */

.hero {
    margin-top: 14px;
    padding: 25px;
    text-align: center;
    border: 1px solid var(--border);
    border-radius: 27px;
    background:
        radial-gradient(circle at center, #34265f44, transparent 55%),
        linear-gradient(145deg, #13151c, #090a0d);
    overflow: hidden;
}

.level-row {
    display: flex;
    justify-content: space-between;
    color: #aaaebb;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

.car-stage {
    position: relative;
    padding: 28px 0 15px;
}

.car-glow {
    position: absolute;
    width: 270px;
    height: 150px;
    left: calc(50% - 135px);
    top: 20px;
    border-radius: 50%;
    background: #8768ff35;
    filter: blur(45px);
}

.car-icon {
    position: relative;
    font-size: 105px;
    filter: drop-shadow(0 20px 22px #000);
    animation: floatCar 3.5s ease-in-out infinite;
}

@keyframes floatCar {
    0%, 100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-8px);
    }
}

.car-name {
    position: relative;
    font-size: 27px;
    font-weight: 950;
    margin-top: 8px;
}

.car-class {
    color: var(--purple2);
    letter-spacing: 4px;
    font-size: 9px;
    margin-top: 6px;
}

.next-car {
    color: #777c89;
    font-size: 11px;
    margin: 12px 0;
}

.xp-track {
    height: 7px;
    border-radius: 10px;
    background: #272a33;
    overflow: hidden;
}

.xp-track span {
    display: block;
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #7154ff, #d0c4ff);
    box-shadow: 0 0 15px #8768ff66;
}

/* MINING */

.mining-card {
    margin-top: 14px;
    padding: 30px 22px;
    text-align: center;
    border: 1px solid var(--border);
    border-radius: 27px;
    background: linear-gradient(145deg, #13151c, #090a0d);
}

.mining-status {
    color: var(--purple2);
    font-size: 10px;
    letter-spacing: 4px;
    font-weight: 900;
}

.timer {
    font-size: clamp(42px, 10vw, 68px);
    font-weight: 950;
    letter-spacing: 3px;
    margin: 15px 0 20px;
}

.primary-btn,
.claim-btn,
.ad-btn {
    width: 100%;
    border: 0;
    border-radius: 17px;
    padding: 17px 20px;
    color: white;
    font-weight: 900;
    letter-spacing: .5px;
}

.primary-btn {
    background: linear-gradient(135deg, #7356ff, #a58eff);
    box-shadow: 0 15px 40px #765cff40;
}

.primary-btn:hover {
    transform: translateY(-1px);
}

.claim-btn {
    background: linear-gradient(135deg, #b28a39, #f0d994);
    color: #18130a;
}

.mining-note {
    color: #777c88;
    font-size: 12px;
    margin: 14px 0 0;
}

/* STATS */

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    margin-top: 14px;
    border: 1px solid var(--border);
    border-radius: 22px;
    overflow: hidden;
    background: var(--border);
}

.stat {
    padding: 20px 10px;
    text-align: center;
    background: #101217;
}

.stat strong {
    display: block;
    font-size: 20px;
}

.stat small {
    display: block;
    margin-top: 5px;
    color: var(--muted);
    font-size: 9px;
    letter-spacing: 2px;
}

/* QUICK ACTIONS */

.actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 14px;
}

.action {
    padding: 17px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: #101217;
    text-align: center;
    color: #dddfea;
    font-size: 12px;
    font-weight: 800;
}

.action:hover {
    border-color: #6550bd;
}

/* ROADMAP */

.roadmap {
    margin-top: 14px;
    padding: 23px;
    border: 1px solid var(--border);
    border-radius: 25px;
    background: #101217;
}

.section-title {
    font-size: 16px;
    letter-spacing: 3px;
    margin: 0 0 17px;
}

.car-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 9px;
}

.car-tile {
    padding: 13px;
    border: 1px solid #252833;
    border-radius: 16px;
    opacity: .35;
    transition: .2s;
}

.car-tile.unlocked {
    opacity: 1;
    border-color: #755cff55;
    background: #171322;
}

.car-tile.current {
    border-color: var(--purple);
    box-shadow: 0 0 20px #8768ff18;
}

.car-level {
    display: block;
    color: #7c808d;
    font-size: 8px;
    letter-spacing: 1px;
}

.car-emoji {
    display: block;
    font-size: 34px;
    margin: 7px 0;
}

.car-tile-name {
    font-size: 10px;
    font-weight: 800;
}

/* AUTH */

.auth-page {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 20px;
}

.auth-box {
    width: min(420px, 100%);
    padding: 35px 28px;
    text-align: center;
    border: 1px solid var(--border);
    border-radius: 28px;
    background: linear-gradient(145deg, #14161d, #090a0d);
    box-shadow: 0 30px 100px #000a;
}

.auth-icon {
    font-size: 75px;
    filter: drop-shadow(0 0 30px #8768ff);
}

.auth-title {
    font-size: 31px;
    letter-spacing: 8px;
    font-weight: 950;
}

.auth-sub {
    color: #777c88;
    font-size: 9px;
    letter-spacing: 4px;
}

.auth-form {
    display: grid;
    gap: 12px;
    margin: 25px 0;
}

.auth-form input {
    width: 100%;
    padding: 16px;
    color: white;
    background: #08090c;
    border: 1px solid #30333d;
    border-radius: 15px;
    outline: none;
}

.auth-form input:focus {
    border-color: var(--purple);
}

.auth-form button {
    padding: 16px;
    border: 0;
    border-radius: 15px;
    color: white;
    background: linear-gradient(135deg, #7356ff, #a58eff);
    font-weight: 900;
}

.auth-link {
    color: #aaaeba;
    font-size: 12px;
}

.error {
    padding: 11px;
    margin-top: 18px;
    color: #ffabb3;
    background: #3b171c;
    border-radius: 12px;
    font-size: 12px;
}

/* HISTORY */

.page-card {
    margin-top: 15px;
    border: 1px solid var(--border);
    border-radius: 25px;
    background: #101217;
    overflow: hidden;
}

.page-head {
    padding: 22px;
    border-bottom: 1px solid var(--border);
}

.page-head h1 {
    margin: 0;
    font-size: 20px;
    letter-spacing: 3px;
}

.tx {
    display: grid;
    grid-template-columns: 100px 90px 1fr;
    gap: 14px;
    padding: 17px 20px;
    border-bottom: 1px solid #20232b;
}

.tx-type {
    color: var(--purple2);
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1px;
}

.tx-amount {
    font-weight: 900;
}

.tx-description {
    color: #858a98;
    font-size: 12px;
}

/* ACHIEVEMENTS */

.achievement {
    padding: 20px;
    border-bottom: 1px solid #20232b;
}

.achievement strong {
    display: block;
    color: var(--purple2);
}

.achievement small {
    color: #7f8491;
}

/* TOAST */

#toast {
    position: fixed;
    left: 50%;
    bottom: 25px;
    transform: translate(-50%, 30px);
    opacity: 0;
    z-index: 99999;
    background: #171921;
    border: 1px solid #3a3e4a;
    padding: 14px 18px;
    border-radius: 15px;
    box-shadow: 0 15px 50px #000a;
    transition: .3s;
    font-size: 13px;
    pointer-events: none;
}

#toast.show {
    opacity: 1;
    transform: translate(-50%, 0);
}

/* MOBILE */

@media(max-width: 700px) {

    .container {
        width: min(100% - 20px, 600px);
        padding-top: 14px;
    }

    .logo {
        font-size: 23px;
    }

    .wallet {
        padding: 16px;
    }

    .wallet-value {
        font-size: 23px;
    }

    .car-icon {
        font-size: 85px;
    }

    .car-name {
        font-size: 23px;
    }

    .car-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .tx {
        grid-template-columns: 80px 70px 1fr;
    }
}

@media(max-width: 420px) {

    .stats strong {
        font-size: 16px;
    }

    .stats small {
        font-size: 7px;
    }

    .actions {
        grid-template-columns: 1fr;
    }

    .timer {
        font-size: 39px;
    }
}
"""


# ============================================================
# DASHBOARD HTML
# ============================================================

DASHBOARD_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0, maximum-scale=1.0"
>

<meta name="theme-color" content="#050608">

<title>STONE • 24H Mining</title>

<style>
{{ css|safe }}
</style>

</head>

<body>

<!-- ========================================================
     SPLASH SCREEN
========================================================= -->

<div id="splash">

    <div class="splash-inner">

        <div class="splash-icon">
            🪨
        </div>

        <div class="splash-title">
            STONE
        </div>

        <div class="splash-sub">
            24H MINING NETWORK
        </div>

        <div class="loader">
            <span></span>
        </div>

    </div>

</div>


<div class="container">

<!-- ========================================================
     HEADER
========================================================= -->

<header class="header">

    <div>

        <div class="logo">
            STONE<span>•</span>
        </div>

        <div class="network">
            24H MINING NETWORK
        </div>

    </div>

    <a href="/logout" class="logout">
        LOGOUT
    </a>

</header>


<!-- ========================================================
     WALLET
========================================================= -->

<section class="wallet-grid">

    <div class="wallet">

        <span class="wallet-label">
            NORMAL COINS
        </span>

        <strong
            class="wallet-value"
            id="coins"
        >
            {{ user.coins }}
        </strong>

    </div>


    <div class="wallet stone">

        <span class="wallet-label">
            PREMIUM STONE 🪨
        </span>

        <strong
            class="wallet-value stone-value"
            id="stones"
        >
            {{ user.stones }}
        </strong>

    </div>

</section>


<!-- ========================================================
     LEVEL / CAR SHOWCASE
========================================================= -->

<section class="hero">

    <div class="level-row">

        <span>
            LEVEL {{ user.level }}
        </span>

        <span>
            XP {{ user.xp }}
        </span>

    </div>


    <div class="car-stage">

        <div class="car-glow"></div>

        <div class="car-icon">
            🚘
        </div>

        <div
            class="car-name"
            id="carName"
        >
            {{ current_car.name }}
        </div>

        <div class="car-class">
            {{ current_car.class }}
        </div>

    </div>


    {% if next_car %}

        <div class="next-car">

            NEXT UNLOCK →
            LEVEL {{ next_car.level }}
            •
            {{ next_car.name }}

        </div>

    {% else %}

        <div class="next-car">
            🏆 MAXIMUM LEGENDARY TIER
        </div>

    {% endif %}


    <div class="xp-track">

        <span
            style="width: {{ xp_percent }}%;"
            id="xpBar"
        ></span>

    </div>

</section>


<!-- ========================================================
     MINING
========================================================= -->

<section class="mining-card">

    <div
        class="mining-status"
        id="miningStatus"
    >
        {% if remaining > 0 %}
            MINING ACTIVE ⛏️
        {% elif user.mining_claimable %}
            MINING COMPLETE
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
        id="mineButton"
        class="primary-btn"
        onclick="startMining()"
    >
        ⛏️ 24H ONE-TAP MINING
    </button>


    <button
        id="claimButton"
        class="claim-btn"
        onclick="claimMining()"
        style="display:none;"
    >
        🪙 CLAIM MINING REWARD
    </button>


    <p class="mining-note">
        One tap starts a complete 24-hour mining session.
    </p>

</section>


<!-- ========================================================
     STATS
========================================================= -->

<section class="stats">

    <div class="stat">

        <strong>
            🔥 <span id="streak">
                {{ user.streak }}
            </span>
        </strong>

        <small>
            DAY STREAK
        </small>

    </div>


    <div class="stat">

        <strong>
            🪨 7 DAYS
        </strong>

        <small>
            1 STONE
        </small>

    </div>


    <div class="stat">

        <strong>
            📺 {{ ads_used }}/{{ max_ads }}
        </strong>

        <small>
            ADS TODAY
        </small>

    </div>

</section>


<!-- ========================================================
     QUICK ACTIONS
========================================================= -->

<section class="actions">

    <a
        class="action"
        href="/history"
    >
        📜 TRANSACTION HISTORY
    </a>


    <button
        class="action"
        onclick="watchAd()"
    >
        📺 WATCH AD +{{ ad_reward }}
    </button>


    <a
        class="action"
        href="/achievements"
    >
        🏆 ACHIEVEMENTS
    </a>


    <a
        class="action"
        href="#roadmap"
    >
        🚗 CAR ROADMAP
    </a>

</section>


<!-- ========================================================
     ROADMAP
========================================================= -->

<section
    class="roadmap"
    id="roadmap"
>

    <h2 class="section-title">
        ROAD TO LEGEND
    </h2>


    <div class="car-grid">

        {% for car in cars %}

        <div
            class="
                car-tile
                {% if user.level >= car.level %}
                    unlocked
                {% endif %}

                {% if user.level == car.level %}
                    current
                {% endif %}
            "
        >

            <span class="car-level">
                LEVEL {{ car.level }}
            </span>

            <span class="car-emoji">
                🚘
            </span>

            <div class="car-tile-name">
                {{ car.name }}
            </div>

        </div>

        {% endfor %}

    </div>

</section>

</div>


<div id="toast"></div>


<script>

let remaining = {{ remaining }};
let claimable = {{ "true" if user.mining_claimable else "false" }};


const timer =
    document.getElementById("timer");

const mineButton =
    document.getElementById("mineButton");

const claimButton =
    document.getElementById("claimButton");

const miningStatus =
    document.getElementById("miningStatus");


function formatTime(seconds) {

    seconds = Math.max(0, seconds);

    const hours =
        Math.floor(seconds / 3600);

    const minutes =
        Math.floor((seconds % 3600) / 60);

    const secs =
        seconds % 60;

    return [
        hours,
        minutes,
        secs
    ]
    .map(
        value =>
            String(value).padStart(2, "0")
    )
    .join(":");
}


function toast(message) {

    const element =
        document.getElementById("toast");

    element.textContent = message;

    element.classList.add("show");

    setTimeout(
        () => element.classList.remove("show"),
        3000
    );
}


function renderMining() {

    if (remaining > 0) {

        timer.textContent =
            formatTime(remaining);

        miningStatus.textContent =
            "MINING ACTIVE ⛏️";

        mineButton.style.display =
            "none";

        claimButton.style.display =
            "none";

        return;
    }


    if (claimable) {

        timer.textContent =
            "READY";

        miningStatus.textContent =
            "MINING COMPLETE ✨";

        mineButton.style.display =
            "none";

        claimButton.style.display =
            "block";

        return;
    }


    timer.textContent =
        "24:00:00";

    miningStatus.textContent =
        "READY TO MINE";

    mineButton.style.display =
        "block";

    claimButton.style.display =
        "none";
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

}, 1000);


async function startMining() {

    mineButton.disabled = true;

    try {

        const response =
            await fetch(
                "/api/start-mining",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();


        if (!data.success) {

            toast(data.error);

            mineButton.disabled = false;

            return;
        }


        remaining =
            data.duration;

        claimable = false;

        mineButton.disabled = false;

        renderMining();

        toast(
            "⛏️ 24H mining started!"
        );

    }

    catch (error) {

        mineButton.disabled = false;

        toast(
            "Connection error."
        );

    }

}


async function claimMining() {

    claimButton.disabled = true;

    try {

        const response =
            await fetch(
                "/api/claim-mining",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();


        if (!data.success) {

            toast(data.error);

            claimButton.disabled = false;

            return;
        }


        toast(
            data.stone > 0
            ? "🔥 7-day streak! +1 STONE 🪨"
            : "⛏️ Mining reward claimed!"
        );


        setTimeout(
            () => location.reload(),
            1200
        );

    }

    catch (error) {

        claimButton.disabled = false;

        toast(
            "Connection error."
        );

    }

}


async function watchAd() {

    /*
        DEMO REWARDED-AD HOOK

        In production, this endpoint should only be
        called after a real ad network confirms that
        the user completed a rewarded advertisement.

        Do NOT credit rewards from an unverified
        client-side ad event in production.
    */

    const confirmed =
        confirm(
            "This is the demo rewarded-ad system.\n\n" +
            "In production, a real rewarded ad would play here.\n\n" +
            "Continue with demo reward?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/rewarded-ad",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();


        if (!data.success) {

            toast(data.error);

            return;
        }


        toast(
            "📺 Reward received: +" +
            data.reward +
            " COINS"
        );


        setTimeout(
            () => location.reload(),
            900
        );

    }

    catch (error) {

        toast(
            "Connection error."
        );

    }

}


renderMining();


/* Splash animation */

setTimeout(
    () => {

        const splash =
            document.getElementById("splash");

        splash.classList.add("hidden");

    },
    1600
);

</script>

</body>

</html>
"""


# ============================================================
# AUTH HTML
# ============================================================

AUTH_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    STONE • {{ "Register" if mode == "register" else "Login" }}
</title>

<style>
{{ css|safe }}
</style>

</head>


<body>


<div class="auth-page">

    <div class="auth-box">

        <div class="auth-icon">
            🪨
        </div>


        <div class="auth-title">
            STONE
        </div>


        <div class="auth-sub">
            24H MINING NETWORK
        </div>


        {% if error %}

        <div class="error">
            {{ error }}
        </div>

        {% endif %}


        <form
            class="auth-form"
            method="POST"
        >

            <input
                type="text"
                name="username"
                placeholder="Username"
                minlength="3"
                maxlength="30"
                required
            >


            <input
                type="password"
                name="password"
                placeholder="Password"
                minlength="6"
                required
            >


            <button type="submit">

                {% if mode == "register" %}
                    CREATE ACCOUNT
                {% else %}
                    LOGIN
                {% endif %}

            </button>

        </form>


        {% if mode == "register" %}

        <a
            class="auth-link"
            href="/login"
        >
            Already have an account? Login
        </a>

        {% else %}

        <a
            class="auth-link"
            href="/register"
        >
            Create a new account
        </a>

        {% endif %}

    </div>

</div>


</body>

</html>
"""


# ============================================================
# HISTORY HTML
# ============================================================

HISTORY_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
    STONE • History
</title>

<style>
{{ css|safe }}
</style>

</head>


<body>


<div class="container">


<header class="header">

    <div>

        <div class="logo">
            STONE<span>•</span>
        </div>

        <div class="network">
            TRANSACTION CENTER
        </div>

    </div>


    <a
        class="logout"
        href="/"
    >
        ← DASHBOARD
    </a>

</header>


<section class="page-card">

    <div class="page-head">

        <h1>
            TRANSACTION HISTORY
        </h1>

    </div>


    {% if transactions %}

        {% for transaction in transactions %}

        <div class="tx">

            <div class="tx-type">
                {{ transaction.transaction_type }}
            </div>


            <div class="tx-amount">
                +{{ transaction.amount }}
            </div>


            <div class="tx-description">
                {{ transaction.description }}
            </div>

        </div>

        {% endfor %}

    {% else %}

        <div class="page-head">
            No transactions yet.
        </div>

    {% endif %}

</section>


</div>


</body>

</html>
"""


# ============================================================
# ACHIEVEMENTS HTML
# ============================================================

ACHIEVEMENTS_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
    STONE • Achievements
</title>

<style>
{{ css|safe }}
</style>

</head>


<body>


<div class="container">


<header class="header">

    <div>

        <div class="logo">
            STONE<span>•</span>
        </div>

        <div class="network">
            ACHIEVEMENT CENTER
        </div>

    </div>


    <a
        class="logout"
        href="/"
    >
        ← DASHBOARD
    </a>

</header>


<section class="page-card">

    <div class="page-head">

        <h1>
            🏆 ACHIEVEMENTS
        </h1>

    </div>


    {% if achievements %}

        {% for achievement in achievements %}

        <div class="achievement">

            <strong>
                ✦ {{ achievement.title }}
            </strong>

            <small>
                Achievement unlocked
            </small>

        </div>

        {% endfor %}

    {% else %}

        <div class="page-head">

            Start mining to unlock your first achievement.

        </div>

    {% endif %}


</section>


</div>


</body>

</html>
"""


# ============================================================
# INJECT CSS INTO ALL TEMPLATES
# ============================================================

@app.context_processor
def inject_css():

    return {
        "css": CSS
    }


# ============================================================
# START APPLICATION
# ============================================================

init_database()


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )