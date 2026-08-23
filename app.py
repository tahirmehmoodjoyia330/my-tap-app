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
# DATABASE SETUP
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
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user


def current_timestamp():
    return int(time.time())


def current_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_level_from_xp(xp):
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
        INSERT INTO transactions (user_id, transaction_type, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, transaction_type, amount, description, current_timestamp()))
    db.commit()
    db.close()


def calculate_mining_remaining(user):
    if not user or not user["mining_started"] or user["mining_claimable"]:
        return 0
    elapsed = current_timestamp() - user["mining_started"]
    remaining = MINING_DURATION - elapsed
    return remaining if remaining > 0 else 0


def refresh_mining_state(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and user["mining_started"] and not user["mining_claimable"]:
        if current_timestamp() - user["mining_started"] >= MINING_DURATION:
            db.execute("UPDATE users SET mining_claimable = 1 WHERE id = ?", (user_id,))
            db.commit()
    db.close()


# ============================================================
# STYLES & TEMPLATES (CSS + HTML)
# ============================================================

COMMON_CSS = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    body { background-color: #050608; color: #f3f4f6; font-family: 'Inter', sans-serif; user-select: none; }
    .luxury-card { background: linear-gradient(135deg, #111318 0%, #1a1d24 100%); border: 1px solid rgba(234, 179, 8, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6); }
    .gold-glow { text-shadow: 0 0 15px rgba(234, 179, 8, 0.5); }
</style>
"""

AUTH_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>STONE Mining - Authentication</title>
    {COMMON_CSS}
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="luxury-card w-full max-w-md p-8 rounded-3xl space-y-6">
        <div class="text-center">
            <div class="w-16 h-16 bg-amber-500/10 border border-amber-500/40 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <i class="fa-solid fa-gem text-amber-400 text-2xl"></i>
            </div>
            <h1 class="text-2xl font-black text-amber-400 uppercase tracking-wider">STONE Ecosystem</h1>
            <p class="text-xs text-gray-400 mt-1">24H Cloud Mining & Luxury Garage</p>
        </div>

        {% if error %}
        <div class="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3 rounded-xl text-center font-bold">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Username</label>
                <input type="text" name="username" required class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-sm text-white focus:border-amber-500 outline-none">
            </div>
            <div>
                <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Password</label>
                <input type="password" name="password" required class="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-sm text-white focus:border-amber-500 outline-none">
            </div>
            <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-gray-950 font-black rounded-xl text-sm shadow-lg shadow-amber-500/20 active:scale-95 transition">
                {{ 'CREATE ACCOUNT' if mode == 'register' else 'LOGIN TO MINING' }}
            </button>
        </form>

        <div class="text-center text-xs text-gray-400">
            {% if mode == 'register' %}
            Already have an account? <a href="/login" class="text-amber-400 font-bold">Login here</a>
            {% else %}
            Don't have an account? <a href="/register" class="text-amber-400 font-bold">Register now</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>STONE Mining Dashboard</title>
    {COMMON_CSS}
</head>
<body class="flex flex-col h-screen justify-between max-w-md mx-auto">
    <!-- Top Bar -->
    <div class="px-4 py-3 bg-gray-950/80 backdrop-blur border-b border-gray-800 flex justify-between items-center z-10">
        <div class="flex items-center space-x-2">
            <div class="w-9 h-9 bg-amber-500/20 border border-amber-500/40 rounded-xl flex items-center justify-center font-black text-amber-400 text-xs">
                L{{ user.level }}
            </div>
            <div>
                <p class="text-[10px] text-gray-400 uppercase font-bold">Current Ride</p>
                <p class="text-xs font-black text-white">{{ current_car.name }}</p>
            </div>
        </div>
        <div class="flex space-x-2">
            <div class="luxury-card px-2.5 py-1 rounded-xl flex items-center space-x-1.5 text-xs">
                <i class="fa-solid fa-coins text-amber-400"></i>
                <span id="user-coins" class="font-black text-amber-300">{{ user.coins }}</span>
            </div>
            <div class="luxury-card px-2.5 py-1 rounded-xl flex items-center space-x-1.5 text-xs border-purple-500/40">
                <span>🪨</span>
                <span id="user-stones" class="font-black text-purple-300">{{ user.stones }}</span>
            </div>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 p-4 overflow-y-auto space-y-4 flex flex-col justify-center">
        <!-- Car Showcase Box -->
        <div class="luxury-card p-5 rounded-3xl text-center relative overflow-hidden">
            <div class="absolute top-2 right-3 text-[9px] bg-amber-500/10 border border-amber-500/30 text-amber-400 px-2 py-0.5 rounded-full font-bold">
                {{ current_car.class }}
            </div>
            <div class="w-20 h-20 bg-amber-500/10 rounded-2xl border border-amber-500/30 flex items-center justify-center mx-auto my-2 shadow-inner">
                <i class="fa-solid fa-car-side text-4xl text-amber-400"></i>
            </div>
            <h2 class="text-base font-black text-white mt-1">{{ current_car.name }}</h2>
            <p class="text-[10px] text-gray-400 mt-0.5">Level {{ user.level }} Garage Elite Vehicle</p>

            <!-- XP Progress -->
            <div class="mt-4">
                <div class="flex justify-between text-[10px] font-bold text-gray-400 mb-1">
                    <span>XP Progress</span>
                    <span>{{ user.xp % 250 }} / 250 XP</span>
                </div>
                <div class="w-full bg-gray-900 h-2 rounded-full overflow-hidden border border-gray-800">
                    <div class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full rounded-full" style="width: {{ xp_percent }}%;"></div>
                </div>
            </div>
        </div>

        <!-- 24H Mining Widget -->
        <div class="luxury-card p-5 rounded-3xl space-y-3 text-center">
            <div class="flex justify-between items-center text-xs">
                <span class="text-gray-400 font-bold uppercase text-[10px]">Cloud Status</span>
                <span id="mining-status-badge" class="font-black text-emerald-400">
                    {% if user.mining_claimable %}Ready to Claim!{% elif user.mining_started %}Mining Active{% format_time %} else %}Idle{% endif %}
                </span>
            </div>

            <div id="mining-action-area">
                {% if user.mining_claimable %}
                <button onclick="claimMining()" class="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-400 text-gray-950 font-black rounded-2xl text-xs shadow-lg uppercase tracking-wider">
                    CLAIM +{{ mining_reward }} COINS ⛏️
                </button>
                {% elif user.mining_started %}
                <button disabled class="w-full py-3.5 bg-gray-800 text-gray-400 font-black rounded-2xl text-xs cursor-not-allowed">
                    MINING IN PROGRESS ⏳
                </button>
                <p id="timer-display" class="text-[10px] text-gray-400 font-bold mt-2">Remaining: {{ remaining }}s</p>
                {% else %}
                <button onclick="startMining()" class="w-full py-3.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-gray-950 font-black rounded-2xl text-xs shadow-lg uppercase tracking-wider">
                    START 24H MINING ⛏️
                </button>
                {% endif %}
            </div>
        </div>

        <!-- Extra Quick Actions -->
        <div class="grid grid-cols-2 gap-2">
            <button onclick="watchAd()" class="luxury-card p-3 rounded-2xl text-center active:scale-95 transition">
                <i class="fa-solid fa-rectangle-ad text-amber-400 text-base mb-1"></i>
                <p class="text-[10px] font-black text-white">REWARDED AD</p>
                <p class="text-[9px] text-gray-400">+{{ ad_reward }} Coins ({{ max_ads - ads_used }} left)</p>
            </button>
            <a href="/history" class="luxury-card p-3 rounded-2xl text-center flex flex-col justify-center items-center active:scale-95 transition">
                <i class="fa-solid fa-clock-rotate-left text-blue-400 text-base mb-1"></i>
                <p class="text-[10px] font-black text-white">HISTORY</p>
                <p class="text-[9px] text-gray-400">View transactions</p>
            </a>
        </div>
    </div>

    <!-- Navigation Footer -->
    <div class="bg-gray-950 border-t border-gray-800 p-2 flex justify-around text-center z-10">
        <a href="/dashboard" class="text-amber-400 text-xs font-bold flex flex-col items-center">
            <i class="fa-solid fa-house text-sm"></i>
            <span class="text-[9px] mt-0.5">MINING</span>
        </a>
        <a href="/achievements" class="text-gray-400 text-xs font-bold flex flex-col items-center">
            <i class="fa-solid fa-trophy text-sm"></i>
            <span class="text-[9px] mt-0.5">BADGES</span>
        </a>
        <a href="/logout" class="text-red-400 text-xs font-bold flex flex-col items-center">
            <i class="fa-solid fa-right-from-bracket text-sm"></i>
            <span class="text-[9px] mt-0.5">LOGOUT</span>
        </a>
    </div>

    <script>
        function startMining() {
            fetch('/api/start-mining', {{ method: 'POST' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) { location.reload(); }
                else { alert(data.error); }
            });
        }

        function claimMining() {
            fetch('/api/claim-mining', {{ method: 'POST' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) { 
                    alert('Reward Claimed successfully! Streak: ' + data.streak);
                    location.reload(); 
                } else { alert(data.error); }
            });
        }

        function watchAd() {
            fetch('/api/rewarded-ad', {{ method: 'POST' }})
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('Ad watched! Received +' + data.reward + ' Coins.');
                    location.reload();
                } else { alert(data.error); }
            });
        }
    </script>
</body>
</html>
"""

HISTORY_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Transaction History</title>
    {COMMON_CSS}
</head>
<body class="flex flex-col h-screen justify-between max-w-md mx-auto">
    <div class="p-4 bg-gray-950 border-b border-gray-800 flex items-center justify-between">
        <h1 class="text-sm font-black text-amber-400 uppercase">Transaction Logs</h1>
        <a href="/dashboard" class="text-xs text-gray-400 font-bold"><i class="fa-solid fa-arrow-left"></i> Back</a>
    </div>
    <div class="flex-1 p-4 overflow-y-auto space-y-2">
        {% for tx in transactions %}
        <div class="luxury-card p-3 rounded-xl flex justify-between items-center text-xs">
            <div>
                <p class="font-bold text-white">{{ tx.description }}</p>
                <p class="text-[9px] text-gray-500">{{ tx.transaction_type }}</p>
            </div>
            <span class="font-black text-amber-400">+{{ tx.amount }}</span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

ACHIEVEMENTS_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Badges & Achievements</title>
    {COMMON_CSS}
</head>
<body class="flex flex-col h-screen justify-between max-w-md mx-auto">
    <div class="p-4 bg-gray-950 border-b border-gray-800 flex items-center justify-between">
        <h1 class="text-sm font-black text-amber-400 uppercase">Unlocked Badges</h1>
        <a href="/dashboard" class="text-xs text-gray-400 font-bold"><i class="fa-solid fa-arrow-left"></i> Back</a>
    </div>
    <div class="flex-1 p-4 overflow-y-auto space-y-2">
        {% for ach in achievements %}
        <div class="luxury-card p-3 rounded-xl flex items-center space-x-3 text-xs">
            <i class="fa-solid fa-award text-amber-400 text-lg"></i>
            <div>
                <p class="font-bold text-white">{{ ach.title }}</p>
                <p class="text-[9px] text-gray-500">Code: {{ ach.code }}</p>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""


# ============================================================
# ROUTES & APIs
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if get_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            return render_template_string(AUTH_HTML, mode="register", error="Invalid input lengths.")
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                       (username, password_hash(password), current_timestamp()))
            db.commit()
            user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            session["user_id"] = user["id"]
            db.close()
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            db.close()
            return render_template_string(AUTH_HTML, mode="register", error="Username already exists.")
    return render_template_string(AUTH_HTML, mode="register", error=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if get_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                          (username, password_hash(password))).fetchone()
        db.close()
        if not user:
            return render_template_string(AUTH_HTML, mode="login", error="Invalid credentials.")
        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))
    return render_template_string(AUTH_HTML, mode="login", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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
    ads_used = user["ads_today"] if user["ads_date"] == today else 0

    return render_template_string(
        DASHBOARD_HTML,
        user=user,
        remaining=remaining,
        current_car=current_car,
        next_car=next_car,
        xp_percent=xp_percent,
        ads_used=ads_used,
        max_ads=MAX_ADS_PER_DAY,
        mining_reward=MINING_REWARD,
        ad_reward=AD_REWARD
    )


@app.post("/api/start-mining")
def start_mining():
    user = get_user()
    if not user:
        return jsonify({"success": False, "error": "Login required."}), 401
    refresh_mining_state(user["id"])
    user = get_user()
    if user["mining_started"] and not user["mining_claimable"]:
        return jsonify({"success": False, "error": "Mining active."})

    db = get_db()
    started = current_timestamp()
    db.execute("UPDATE users SET mining_started = ?, mining_claimable = 0 WHERE id = ?", (started, user["id"]))
    db.commit()
    db.close()
    return jsonify({"success": True, "started": started})


@app.post("/api/claim-mining")
def claim_mining():
    user = get_user()
    if not user:
        return jsonify({"success": False, "error": "Login required."}), 401
    refresh_mining_state(user["id"])
    user = get_user()
    if not user["mining_started"] or not user["mining_claimable"]:
        return jsonify({"success": False, "error": "Not ready to claim."})

    now = current_timestamp()
    new_streak = (user["streak"] + 1) if (user["last_mining_claim"] and (now - user["last_mining_claim"] <= 48 * 3600)) else 1
    stone_reward = 1 if (new_streak % STONE_STREAK_DAYS == 0) else 0

    new_xp = user["xp"] + XP_PER_MINING
    new_level = get_level_from_xp(new_xp)

    db = get_db()
    db.execute("""
        UPDATE users SET coins = coins + ?, stones = stones + ?, xp = ?, level = ?, streak = ?, last_mining_claim = ?, mining_started = 0, mining_claimable = 0 WHERE id = ?
    """, (MINING_REWARD, stone_reward, new_xp, new_level, new_streak, now, user["id"]))
    db.commit()
    db.close()

    add_transaction(user["id"], "MINING", MINING_REWARD, "24H Mining Reward")
    if stone_reward:
        add_transaction(user["id"], "STONE", stone_reward, "7-Day Streak Stone")

    return jsonify({"success": True, "streak": new_streak, "level": new_level})


@app.post("/api/rewarded-ad")
def rewarded_ad():
    user = get_user()
    if not user:
        return jsonify({"success": False, "error": "Login required."}), 401
    today = current_date()
    ads_used = user["ads_today"] if user["ads_date"] == today else 0
    if ads_used >= MAX_ADS_PER_DAY:
        return jsonify({"success": False, "error": "Ad limit reached."})

    ads_used += 1
    new_xp = user["xp"] + XP_PER_AD
    new_level = get_level_from_xp(new_xp)

    db = get_db()
    db.execute("UPDATE users SET coins = coins + ?, xp = ?, level = ?, ads_today = ?, ads_date = ? WHERE id = ?",
               (AD_REWARD, new_xp, new_level, ads_used, today, user["id"]))
    db.commit()
    db.close()

    add_transaction(user["id"], "AD", AD_REWARD, "Rewarded Ad Bonus")
    return jsonify({"success": True, "reward": AD_REWARD})


@app.route("/history")
def history():
    user = get_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user["id"],)).fetchall()
    db.close()
    return render_template_string(HISTORY_HTML, transactions=transactions)


@app.route("/achievements")
def achievements():
    user = get_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    achievements = db.execute("SELECT * FROM achievements WHERE user_id = ?", (user["id"],)).fetchall()
    db.close()
    return render_template_string(ACHIEVEMENTS_HTML, achievements=achievements)


if __name__ == '__main__':
    init_database()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
