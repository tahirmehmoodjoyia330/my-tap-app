# LuxMine – Luxury Mining Web App

Mobile-first premium mining experience with 24h One-Tap Mining, level-based luxury cars, Coins + STONE rewards, referrals, tasks, leaderboard and more.

## Features

- **24h One-Tap Mining** (no tap-to-earn spam)
- **Level system** → center car upgrades (Mehran → Bugatti)
- **Coins** (normal) + **STONE** (premium – 7-day continuous mining streak)
- Dashboard, Tasks (daily + one-time), Referral system with proper link
- Wallet, Leaderboard, Profile
- Ads placeholder (ready for AdSense)
- Animated splash screen
- SQLite database (Render-friendly)
- Dark luxury UI with glassmorphism + gold accents

## Quick Start (Local)

```bash
cd mining_app
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Deploy on Render

1. Push this folder to a GitHub repository
2. Create a new **Web Service** on Render
3. Connect the repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3
5. (Optional) Add env var `SECRET_KEY` = any long random string

Render will give you a URL like `https://yourapp.onrender.com`

Referral links work automatically:  
`https://yourapp.onrender.com/register?ref=YOURCODE`

## Project Structure

```
mining_app/
├── app.py              # Main Flask application
├── requirements.txt
├── Procfile
├── README.md
└── templates/
    ├── base.html
    ├── splash.html
    ├── auth.html
    ├── home.html
    ├── dashboard.html
    ├── tasks.html
    ├── referral.html
    ├── wallet.html
    ├── leaderboard.html
    ├── profile.html
    └── ads.html
```

## How Mining Works

1. User taps **Start 24h Mining**
2. Progress circle + countdown runs for 24 hours
3. After 24h user claims coins
4. Streak increases if mined on consecutive days
5. Every 7 continuous days → +1 STONE 🪨

## Level → Car Mapping

| Level | Car                  |
|-------|----------------------|
| 1     | Suzuki Mehran        |
| 5     | Honda Accord         |
| 10    | Toyota Land Cruiser  |
| 15    | Audi A6              |
| 20    | Porsche Cayenne      |
| 24    | Jaguar F-Type 🐆     |
| 26    | Lamborghini Huracán  |
| 30    | Bugatti Veyron 💎    |

Enjoy building! ⛏️
