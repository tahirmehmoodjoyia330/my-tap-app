import os
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, g
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# ==================== APP CONFIG ====================
app = Flask(__name__, template_folder='.')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///mining.db'
).replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

db = SQLAlchemy(app)

# ==================== CAR LEVELS (Luxury) ====================
# Level 1 → cheapest popular, Level 30+ → ultra luxury
# body: sedan | suv | sports
CARS = {
    1:  {"name": "Suzuki Mehran",       "color": "#94a3b8", "body": "sedan",  "accent": "#64748b"},
    2:  {"name": "Toyota Corolla",      "color": "#64748b", "body": "sedan",  "accent": "#475569"},
    3:  {"name": "Honda Civic",         "color": "#475569", "body": "sedan",  "accent": "#334155"},
    4:  {"name": "Toyota Camry",        "color": "#1e293b", "body": "sedan",  "accent": "#0f172a"},
    5:  {"name": "Honda Accord",        "color": "#0f172a", "body": "sedan",  "accent": "#020617"},
    6:  {"name": "Hyundai Sonata",      "color": "#1e3a5f", "body": "sedan",  "accent": "#1e40af"},
    7:  {"name": "Toyota Fortuner",     "color": "#1e40af", "body": "suv",    "accent": "#1d4ed8"},
    8:  {"name": "Mitsubishi Pajero",   "color": "#1d4ed8", "body": "suv",    "accent": "#2563eb"},
    9:  {"name": "Nissan Patrol",       "color": "#2563eb", "body": "suv",    "accent": "#3b82f6"},
    10: {"name": "Toyota Land Cruiser", "color": "#1e3a8a", "body": "suv",    "accent": "#1e40af"},
    11: {"name": "BMW 3 Series",        "color": "#1e293b", "body": "sedan",  "accent": "#3b82f6"},
    12: {"name": "Audi A4",             "color": "#0f172a", "body": "sedan",  "accent": "#60a5fa"},
    13: {"name": "Mercedes C-Class",    "color": "#18181b", "body": "sedan",  "accent": "#a1a1aa"},
    14: {"name": "BMW 5 Series",        "color": "#0c0a09", "body": "sedan",  "accent": "#3b82f6"},
    15: {"name": "Audi A6",             "color": "#18181b", "body": "sedan",  "accent": "#94a3b8"},
    16: {"name": "Mercedes E-Class",    "color": "#1c1917", "body": "sedan",  "accent": "#d4d4d8"},
    17: {"name": "BMW X5",              "color": "#0f172a", "body": "suv",    "accent": "#3b82f6"},
    18: {"name": "Audi Q7",             "color": "#18181b", "body": "suv",    "accent": "#64748b"},
    19: {"name": "Mercedes GLE",        "color": "#0c0a09", "body": "suv",    "accent": "#a1a1aa"},
    20: {"name": "Porsche Cayenne",     "color": "#1c1917", "body": "suv",    "accent": "#f59e0b"},
    21: {"name": "BMW M5",              "color": "#0f172a", "body": "sports", "accent": "#3b82f6"},
    22: {"name": "Audi RS7",            "color": "#18181b", "body": "sports", "accent": "#ef4444"},
    23: {"name": "Mercedes AMG GT",     "color": "#0c0a09", "body": "sports", "accent": "#f59e0b"},
    24: {"name": "Jaguar F-Type",       "color": "#7f1d1d", "body": "sports", "accent": "#fbbf24"},
    25: {"name": "Porsche 911",         "color": "#1c1917", "body": "sports", "accent": "#f59e0b"},
    26: {"name": "Lamborghini Huracán", "color": "#ca8a04", "body": "sports", "accent": "#fef08a"},
    27: {"name": "Ferrari 488",         "color": "#b91c1c", "body": "sports", "accent": "#fef2f2"},
    28: {"name": "McLaren 720S",        "color": "#f59e0b", "body": "sports", "accent": "#0f172a"},
    29: {"name": "Bugatti Chiron",      "color": "#1e3a8a", "body": "sports", "accent": "#fbbf24"},
    30: {"name": "Bugatti Veyron",      "color": "#0c0a09", "body": "sports", "accent": "#fef08a"},
}

def get_car_for_level(level):
    if level >= 30:
        return CARS[30]
    return CARS.get(level, CARS[1])

# ==================== MODELS ====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    referral_code = db.Column(db.String(12), unique=True, nullable=False, index=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    coins = db.Column(db.Float, default=0.0)
    stones = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    
    # Mining
    is_mining = db.Column(db.Boolean, default=False)
    mining_start = db.Column(db.DateTime, nullable=True)
    mining_end = db.Column(db.DateTime, nullable=True)
    last_claim = db.Column(db.DateTime, nullable=True)
    
    # Streak
    streak = db.Column(db.Integer, default=0)
    last_mining_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    referrer = db.relationship('User', remote_side=[id], backref='referrals')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_mining_rate(self):
        """Coins per hour based on level"""
        base = 10.0
        return base + (self.level - 1) * 2.5

    def get_xp_for_next_level(self):
        return self.level * 500

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.get_xp_for_next_level():
            self.xp -= self.get_xp_for_next_level()
            self.level += 1

    def to_dict(self):
        car = get_car_for_level(self.level)
        return {
            'id': self.id,
            'username': self.username,
            'coins': round(self.coins, 2),
            'stones': self.stones,
            'level': self.level,
            'xp': self.xp,
            'xp_next': self.get_xp_for_next_level(),
            'streak': self.streak,
            'is_mining': self.is_mining,
            'mining_rate': self.get_mining_rate(),
            'referral_code': self.referral_code,
            'car': car,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300))
    reward_coins = db.Column(db.Float, default=50.0)
    task_type = db.Column(db.String(20), default='daily')  # daily / one-time
    icon = db.Column(db.String(10), default='✅')
    is_active = db.Column(db.Boolean, default=True)


class UserTask(db.Model):
    __tablename__ = 'user_tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='completed_tasks')
    task = db.relationship('Task')


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='coins')  # coins / stones
    type = db.Column(db.String(30))  # mining, task, referral, streak
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='transactions')


# ==================== HELPERS ====================
def generate_referral_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not User.query.filter_by(referral_code=code).first():
            return code


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.before_request
def load_user():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


def process_mining_claim(user):
    """Claim pending mining rewards if 24h completed or partial"""
    if not user.is_mining or not user.mining_start:
        return 0.0
    
    now = datetime.utcnow()
    end = user.mining_end or (user.mining_start + timedelta(hours=24))
    
    if now >= end:
        # Full 24h completed
        hours = 24.0
        user.is_mining = False
        user.mining_start = None
        user.mining_end = None
        
        # Update streak
        today = now.date()
        if user.last_mining_date:
            diff = (today - user.last_mining_date).days
            if diff == 1:
                user.streak += 1
            elif diff > 1:
                user.streak = 1
        else:
            user.streak = 1
        user.last_mining_date = today
        
        # Stone reward every 7 continuous days
        if user.streak > 0 and user.streak % 7 == 0:
            user.stones += 1
            db.session.add(Transaction(
                user_id=user.id,
                amount=1,
                currency='stones',
                type='streak',
                description=f'7-day mining streak reward (Streak: {user.streak})'
            ))
    else:
        # Partial claim (optional – we allow claim only after full 24h for simplicity)
        # For better UX we can allow partial, but sticking to 24h one-tap
        hours = 0
        return 0.0
    
    earned = hours * user.get_mining_rate()
    user.coins += earned
    user.add_xp(int(earned * 2))
    user.last_claim = now
    
    db.session.add(Transaction(
        user_id=user.id,
        amount=earned,
        currency='coins',
        type='mining',
        description=f'24h Mining completed • Rate: {user.get_mining_rate():.1f}/hr'
    ))
    db.session.commit()
    return earned


# ==================== ROUTES ====================
@app.route('/')
def index():
    if g.user:
        return redirect(url_for('home'))
    return redirect(url_for('splash'))


@app.route('/splash')
def splash():
    return render_template('splash.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('home'))
    
    ref_code = request.args.get('ref', '').strip().upper()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        ref_input = request.form.get('referral', '').strip().upper() or ref_code
        
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return render_template('auth.html', mode='register', ref=ref_code)
        if len(password) < 4:
            flash('Password must be at least 4 characters', 'error')
            return render_template('auth.html', mode='register', ref=ref_code)
        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth.html', mode='register', ref=ref_code)
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('auth.html', mode='register', ref=ref_code)
        
        referred_by = None
        if ref_input:
            referrer = User.query.filter_by(referral_code=ref_input).first()
            if referrer:
                referred_by = referrer.id
        
        user = User(
            username=username,
            referral_code=generate_referral_code(),
            referred_by=referred_by,
            coins=100.0  # Welcome bonus
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Referral reward
        if referred_by:
            referrer = User.query.get(referred_by)
            if referrer:
                referrer.coins += 150
                db.session.add(Transaction(
                    user_id=referrer.id,
                    amount=150,
                    currency='coins',
                    type='referral',
                    description=f'Referral bonus for inviting {username}'
                ))
                user.coins += 50  # New user also gets small bonus
                db.session.add(Transaction(
                    user_id=user.id,
                    amount=50,
                    currency='coins',
                    type='referral',
                    description='Welcome referral bonus'
                ))
                db.session.commit()
        
        session['user_id'] = user.id
        session.permanent = True
        flash('Welcome to LuxMine! +100 Coins welcome bonus 🎉', 'success')
        return redirect(url_for('home'))
    
    return render_template('auth.html', mode='register', ref=ref_code)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('home'))
        flash('Invalid username or password', 'error')
    
    return render_template('auth.html', mode='login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    user = g.user
    # Auto claim if mining finished
    if user.is_mining and user.mining_end and datetime.utcnow() >= user.mining_end:
        process_mining_claim(user)
        user = User.query.get(user.id)  # refresh
    
    car = get_car_for_level(user.level)
    
    # Mining progress
    mining_progress = 0
    remaining_seconds = 0
    if user.is_mining and user.mining_start and user.mining_end:
        total = (user.mining_end - user.mining_start).total_seconds()
        elapsed = (datetime.utcnow() - user.mining_start).total_seconds()
        mining_progress = min(100, max(0, (elapsed / total) * 100))
        remaining_seconds = max(0, int((user.mining_end - datetime.utcnow()).total_seconds()))
    
    return render_template(
        'home.html',
        user=user,
        car=car,
        mining_progress=mining_progress,
        remaining_seconds=remaining_seconds
    )


@app.route('/start_mining', methods=['POST'])
@login_required
def start_mining():
    user = g.user
    
    if user.is_mining:
        return jsonify({'success': False, 'message': 'Already mining!'})
    
    now = datetime.utcnow()
    user.is_mining = True
    user.mining_start = now
    user.mining_end = now + timedelta(hours=24)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '24h Mining started! ⛏️',
        'end_time': user.mining_end.isoformat()
    })


@app.route('/claim_mining', methods=['POST'])
@login_required
def claim_mining():
    user = g.user
    earned = process_mining_claim(user)
    if earned > 0:
        return jsonify({
            'success': True,
            'message': f'Claimed {earned:.2f} Coins! 💰',
            'earned': earned,
            'coins': user.coins,
            'stones': user.stones,
            'level': user.level,
            'streak': user.streak
        })
    return jsonify({'success': False, 'message': 'Mining not complete yet'})


@app.route('/dashboard')
@login_required
def dashboard():
    user = g.user
    car = get_car_for_level(user.level)
    recent_tx = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', user=user, car=car, transactions=recent_tx)


@app.route('/tasks')
@login_required
def tasks():
    user = g.user
    all_tasks = Task.query.filter_by(is_active=True).all()
    
    # Get completed task ids for today (daily) and all (one-time)
    today = datetime.utcnow().date()
    completed = {}
    for ut in UserTask.query.filter_by(user_id=user.id).all():
        task = ut.task
        if task.task_type == 'one-time':
            completed[task.id] = True
        elif task.task_type == 'daily' and ut.completed_at.date() == today:
            completed[task.id] = True
    
    return render_template('tasks.html', user=user, tasks=all_tasks, completed=completed)


@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    user = g.user
    task = Task.query.get_or_404(task_id)
    
    today = datetime.utcnow().date()
    
    # Check if already completed
    existing = UserTask.query.filter_by(user_id=user.id, task_id=task_id).all()
    for ut in existing:
        if task.task_type == 'one-time':
            return jsonify({'success': False, 'message': 'Already completed'})
        if task.task_type == 'daily' and ut.completed_at.date() == today:
            return jsonify({'success': False, 'message': 'Already completed today'})
    
    # ===== REAL CONDITIONS (no free claims) =====
    title = (task.title or '').lower()
    
    if 'daily login' in title:
        pass  # Opening app / being logged in is enough once per day
        
    elif 'complete mining' in title:
        # Must have claimed mining today (last_claim today) or finished a session
        if not user.last_claim or user.last_claim.date() != today:
            return jsonify({'success': False, 'message': 'Finish a 24h mining session first'})
            
    elif 'invite' in title or 'friend' in title:
        ref_count = User.query.filter_by(referred_by=user.id).count()
        if ref_count < 1:
            return jsonify({'success': False, 'message': 'Invite at least 1 friend who registers'})
            
    elif 'level 5' in title or 'reach level' in title:
        if user.level < 5:
            return jsonify({'success': False, 'message': f'Reach Level 5 first (now Level {user.level})'})
            
    elif '7-day' in title or 'streak' in title:
        if user.streak < 7:
            return jsonify({'success': False, 'message': f'Need 7-day streak (now {user.streak} days)'})
            
    elif 'share referral' in title or 'referral' in title:
        if not session.get('visited_referral'):
            return jsonify({'success': False, 'message': 'Open Invite page and copy your link first'})
            
    elif 'leaderboard' in title:
        if not session.get('visited_leaderboard'):
            return jsonify({'success': False, 'message': 'Visit the Leaderboard page first'})
            
    elif 'wallet' in title:
        if not session.get('visited_wallet'):
            return jsonify({'success': False, 'message': 'Open your Wallet page first'})
    
    # Complete
    ut = UserTask(user_id=user.id, task_id=task_id, claimed=True)
    db.session.add(ut)
    
    user.coins += task.reward_coins
    user.add_xp(int(task.reward_coins))
    
    db.session.add(Transaction(
        user_id=user.id,
        amount=task.reward_coins,
        currency='coins',
        type='task',
        description=f'Task: {task.title}'
    ))
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'+{task.reward_coins} Coins! 🎉',
        'coins': user.coins
    })


@app.route('/referral')
@login_required
def referral():
    session['visited_referral'] = True
    user = g.user
    base_url = request.url_root.rstrip('/')
    referral_link = f"{base_url}/register?ref={user.referral_code}"
    
    # Count referrals
    ref_count = User.query.filter_by(referred_by=user.id).count()
    ref_users = User.query.filter_by(referred_by=user.id).order_by(User.created_at.desc()).limit(20).all()
    
    return render_template(
        'referral.html',
        user=user,
        referral_link=referral_link,
        ref_count=ref_count,
        ref_users=ref_users
    )


@app.route('/wallet')
@login_required
def wallet():
    session['visited_wallet'] = True
    user = g.user
    txs = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.created_at.desc()).limit(50).all()
    return render_template('wallet.html', user=user, transactions=txs)


@app.route('/leaderboard')
@login_required
def leaderboard():
    session['visited_leaderboard'] = True
    top_coins = User.query.order_by(User.coins.desc()).limit(20).all()
    top_level = User.query.order_by(User.level.desc(), User.xp.desc()).limit(20).all()
    top_streak = User.query.order_by(User.streak.desc()).limit(20).all()
    return render_template(
        'leaderboard.html',
        user=g.user,
        top_coins=top_coins,
        top_level=top_level,
        top_streak=top_streak
    )


@app.route('/profile')
@login_required
def profile():
    user = g.user
    car = get_car_for_level(user.level)
    return render_template('profile.html', user=user, car=car)


@app.route('/ads')
@login_required
def ads():
    return render_template('ads.html', user=g.user)


# ==================== INIT DB & SEED ====================
def seed_tasks():
    if Task.query.count() > 0:
        return
    
    tasks_data = [
        ("Daily Login", "Open the app today", 25, "daily", "📅"),
        ("Complete Mining", "Finish one 24h mining session", 80, "daily", "⛏️"),
        ("Invite a Friend", "Refer 1 friend who registers", 200, "one-time", "👥"),
        ("Reach Level 5", "Upgrade to Level 5", 150, "one-time", "⬆️"),
        ("7-Day Streak", "Maintain 7-day mining streak", 300, "one-time", "🔥"),
        ("Share Referral", "Copy your referral link", 40, "daily", "🔗"),
        ("Check Leaderboard", "Visit the leaderboard", 20, "daily", "🏆"),
        ("View Wallet", "Open your wallet page", 15, "daily", "💎"),
    ]
    
    for title, desc, reward, ttype, icon in tasks_data:
        db.session.add(Task(
            title=title,
            description=desc,
            reward_coins=reward,
            task_type=ttype,
            icon=icon
        ))
    db.session.commit()


@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    seed_tasks()
    print('Database initialized and tasks seeded.')


# Auto create tables on first request (for Render)
@app.before_request
def ensure_db():
    if not hasattr(g, '_db_initialized'):
        try:
            db.create_all()
            seed_tasks()
            g._db_initialized = True
        except Exception:
            pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_tasks()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
