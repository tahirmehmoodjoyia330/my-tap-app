from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Apex Luxury Mining - Elite Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; background: radial-gradient(circle at center, #111827 0%, #030712 100%); color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        
        /* Splash Screen Animation */
        #splash-screen {
            position: fixed; inset: 0; background: #030712; z-index: 9999;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            transition: opacity 0.6s ease-out;
        }
        .logo-glow {
            animation: pulseLogo 2s infinite alternate;
        }
        @keyframes pulseLogo {
            0% { transform: scale(1); filter: drop-shadow(0 0 15px rgba(234, 179, 8, 0.4)); }
            100% { transform: scale(1.08); filter: drop-shadow(0 0 35px rgba(234, 179, 8, 0.8)); }
        }

        .luxury-glass {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.7) 0%, rgba(17, 24, 39, 0.85) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(234, 179, 8, 0.2);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        }
        
        .gold-border { border: 1px solid rgba(234, 179, 8, 0.4); }
        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; }
        
        .car-float {
            animation: floatCar 3s ease-in-out infinite;
        }
        @keyframes floatCar {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
        }
        
        .mine-btn-glow {
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
            transition: all 0.2s ease;
        }
        .mine-btn-glow:active { transform: scale(0.95); }
    </style>
</head>
<body class="flex flex-col h-screen justify-between">

    <!-- 5. SPLASH SCREEN WITH LOGO ANIMATION -->
    <div id="splash-screen">
        <div class="logo-glow text-center flex flex-col items-center">
            <div class="w-24 h-24 rounded-3xl bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-600 flex items-center justify-center shadow-2xl mb-4 border-2 border-amber-200">
                <i class="fa-solid fa-gem text-gray-950 text-4xl font-black"></i>
            </div>
            <h1 class="text-2xl font-black tracking-widest text-amber-400 uppercase">Apex Luxury</h1>
            <p class="text-xs text-gray-400 tracking-widest mt-1">Cloud Mining & Wealth Engine</p>
        </div>
        <div class="w-48 bg-gray-800 h-1.5 rounded-full overflow-hidden mt-8 border border-gray-700">
            <div id="loader-bar" class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full w-0 transition-all duration-700"></div>
        </div>
    </div>

    <!-- TOP HEADER: BALANCES & CURRENCIES -->
    <div class="px-4 pt-3 pb-2.5 flex justify-between items-center bg-gray-950/90 border-b border-gray-800/80 z-20">
        <div class="flex items-center space-x-2.5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-600 flex items-center justify-center gold-border shadow-lg">
                <i class="fa-solid fa-crown text-gray-950 text-base font-bold"></i>
            </div>
            <div>
                <div class="flex items-center space-x-1">
                    <span class="text-[10px] font-bold text-gray-400 uppercase">Level <span id="user-level" class="text-amber-400">1</span></span>
                </div>
                <p class="text-xs font-extrabold text-white truncate max-w-[100px]" id="car-name-header">Mehran (Starter)</p>
            </div>
        </div>

        <!-- Currencies (Normal Coins & Stone 🪨) -->
        <div class="flex items-center space-x-2">
            <div class="luxury-glass px-3 py-1.5 rounded-2xl flex items-center space-x-1.5">
                <i class="fa-solid fa-coins text-amber-400 text-xs"></i>
                <span id="top-balance" class="font-black text-xs text-amber-300">0</span>
            </div>
            <div class="luxury-glass px-3 py-1.5 rounded-2xl flex items-center space-x-1.5 border-purple-500/40">
                <span class="text-sm">🪨</span>
                <span id="stone-balance" class="font-black text-xs text-purple-300">0</span>
            </div>
        </div>
    </div>

    <!-- TAB 1: HOME (24H CLINING & CAR SHOWCASE) -->
    <div id="tab-home" class="tab-content active flex-1 p-4 justify-between items-center relative overflow-hidden">
        
        <!-- Luxury Background Glow -->
        <div class="absolute inset-0 bg-gradient-to-b from-amber-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>

        <!-- Level Car Showcase Display -->
        <div class="text-center z-10 w-full mt-1">
            <div class="inline-block px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] font-black tracking-wider uppercase mb-2">
                Garage Showcase • Level <span id="display-level">1</span>
            </div>
            <div class="car-float my-2 flex justify-center items-center">
                <div id="car-icon-container" class="w-32 h-32 rounded-3xl bg-gradient-to-tr from-gray-900 to-gray-800 gold-border flex items-center justify-center shadow-2xl relative">
                    <i id="car-icon" class="fa-solid fa-car text-5xl text-amber-400 drop-shadow-[0_0_15px_rgba(234,179,8,0.6)]"></i>
                    <span id="car-badge" class="absolute -bottom-2 bg-amber-500 text-gray-950 text-[9px] font-black px-2 py-0.5 rounded-full shadow">Basic</span>
                </div>
            </div>
            <h2 id="car-title" class="text-lg font-black text-white tracking-wide mt-1">Suzuki Mehran</h2>
            <p id="car-desc" class="text-[11px] text-gray-400">The legendary street starter.</p>
        </div>

        <!-- 1. 24H ONE-TAP CLOUD MINING ENGINE -->
        <div class="luxury-glass w-full p-4 rounded-3xl z-10 text-center space-y-3">
            <div class="flex justify-between items-center px-1">
                <div class="text-left">
                    <p class="text-[10px] text-gray-400 font-bold uppercase">Cloud Mining Status</p>
                    <p id="mining-status-text" class="text-xs font-black text-emerald-400">Ready to Mine ⛏️</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] text-gray-400 font-bold uppercase">Reward Pool</p>
                    <p class="text-xs font-black text-amber-300">+50,000 Coins</p>
                </div>
            </div>

            <!-- Big 24H Mining Button -->
            <button id="mining-btn" onclick="startMining()" class="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-500 text-white font-black text-sm tracking-wider mine-btn-glow flex items-center justify-center space-x-2">
                <i class="fa-solid fa-pickaxe text-lg"></i>
                <span id="mining-btn-text">START 24H MINING ⛏️</span>
            </button>
            <p id="mining-timer" class="text-[10px] text-gray-400 font-bold">Tap once every 24 hours to secure earnings.</p>
        </div>

        <!-- Bottom XP Progress Bar -->
        <div class="w-full px-1 z-10 mb-1">
            <div class="flex justify-between text-[11px] font-bold text-gray-400 mb-1">
                <span>Garage XP Progress</span>
                <span id="xp-text">0 / 100 XP</span>
            </div>
            <div class="w-full bg-gray-900 h-2.5 rounded-full overflow-hidden border border-gray-800">
                <div id="xp-bar" class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full w-0 rounded-full transition-all duration-300"></div>
            </div>
        </div>
    </div>

    <!-- TAB 2: GARAGE & CARS (Level Upgrades) -->
    <div id="tab-garage" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <div>
            <h2 class="text-lg font-black text-white">Luxury Garage</h2>
            <p class="text-xs text-gray-400">Upgrade your level to unlock world-class supercars.</p>
        </div>
        <div class="space-y-3" id="garage-list">
            <!-- Dynamically populated or static luxury list -->
            <div class="luxury-glass p-3.5 rounded-2xl flex justify-between items-center border-amber-500/40">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-xl bg-amber-500/10 gold-border flex items-center justify-center text-amber-400 text-xl font-bold">🚗</div>
                <div>
                        <h3 class="font-bold text-xs text-white">Level 1: Suzuki Mehran</h3>
                        <p class="text-[10px] text-gray-400">Unlocked • Current Ride</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-emerald-400">Active</span>
            </div>
            <div class="luxury-glass p-3.5 rounded-2xl flex justify-between items-center opacity-70">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 text-xl">🚙</div>
                    <div>
                        <h3 class="font-bold text-xs text-white">Level 5: Toyota Civic</h3>
                        <p class="text-[10px] text-gray-400">Cost: 500,000 Coins</p>
                    </div>
                </div>
                <button onclick="upgradeLevel(5, 500000, 'Toyota Civic', 'fa-car-side')" class="bg-amber-500 text-gray-950 font-black px-3 py-1.5 rounded-xl text-xs">Unlock</button>
            </div>
            <div class="luxury-glass p-3.5 rounded-2xl flex justify-between items-center opacity-70">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 text-xl">🐆</div>
                    <div>
                        <h3 class="font-bold text-xs text-white">Level 15: Jaguar F-Type</h3>
                        <p class="text-[10px] text-gray-400">Cost: 5,000,000 Coins</p>
                    </div>
                </div>
                <button onclick="upgradeLevel(15, 5000000, 'Jaguar F-Type', 'fa-gauge-high')" class="bg-amber-500 text-gray-950 font-black px-3 py-1.5 rounded-xl text-xs">Unlock</button>
            </div>
            <div class="luxury-glass p-3.5 rounded-2xl flex justify-between items-center opacity-70">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 text-xl">🏎️</div>
                    <div>
                        <h3 class="font-bold text-xs text-white">Level 30: BMW M8 & Bugatti</h3>
                        <p class="text-[10px] text-gray-400">Cost: 50,000,000 Coins</p>
                    </div>
                </div>
                <button onclick="upgradeLevel(30, 50000000, 'Bugatti Chiron', 'fa-bolt')" class="bg-amber-500 text-gray-950 font-black px-3 py-1.5 rounded-xl text-xs">Unlock</button>
            </div>
        </div>
    </div>

    <!-- TAB 3: STREAKS & STONE 🪨 REWARDS -->
    <div id="tab-streaks" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <div>
            <h2 class="text-lg font-black text-white">Weekly Streak & Stone 🪨</h2>
            <p class="text-xs text-gray-400">Maintain a 7-day mining streak to earn premium Stone coins.</p>
        </div>
        
        <div class="luxury-glass p-4 rounded-3xl text-center space-y-3 border-purple-500/30">
            <div class="w-16 h-16 rounded-2xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center mx-auto text-3xl">
                🪨
            </div>
            <h3 class="font-black text-base text-white">Weekly Stone Vault</h3>
            <p class="text-xs text-gray-400">Complete 7 consecutive daily check-ins to claim 1 Rare Stone 🪨.</p>
            
            <div class="flex justify-center space-x-2 my-2" id="streak-dots">
                <span class="w-8 h-8 rounded-xl bg-amber-500 text-gray-950 font-black flex items-center justify-center text-xs">1</span>
                <span class="w-8 h-8 rounded-xl bg-gray-800 text-gray-400 font-black flex items-center justify-center text-xs">2</span>
                <span class="w-8 h-8 rounded-xl bg-gray-800 text-gray-400 font-black flex items-center justify-center text-xs">3</span>
                <span class="w-8 h-8 rounded-xl bg-gray-800 text-gray-400 font-black flex items-center justify-center text-xs">4</span>
                <span class="w-8 h-8 rounded-xl bg-gray-800 text-gray-400 font-black flex items-center justify-center text-xs">5</span>
                <span class="w-8 h-8 rounded-xl bg-gray-800 text-gray-400 font-black flex items-center justify-center text-xs">6</span>
                <span class="w-8 h-8 rounded-xl bg-purple-600 text-white font-black flex items-center justify-center text-xs">🪨</span>
            </div>

            <button onclick="claimWeeklyStone()" class="w-full py-3 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-black text-xs shadow-lg">
                CHECK-IN & CLAIM STREAK
            </button>
        </div>
    </div>

    <!-- BOTTOM NAVIGATION BAR -->
    <div class="luxury-glass border-t border-gray-800 px-6 py-2 flex justify-around items-center z-20">
        <button onclick="switchTab('home')" id="nav-home" class="flex flex-col items-center text-amber-400 transition">
            <i class="fa-solid fa-house text-base"></i>
            <span class="text-[9px] mt-1 font-bold">MINING</span>
        </button>
        <button onclick="switchTab('garage')" id="nav-garage" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-car text-base"></i>
            <span class="text-[9px] mt-1 font-bold">GARAGE</span>
        </button>
        <button onclick="switchTab('streaks')" id="nav-streaks" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-fire text-base"></i>
            <span class="text-[9px] mt-1 font-bold">STREAKS & 🪨</span>
        </button>
    </div>

    <script>
        // App State
        let balance = 15000;
        let stones = 0;
        let level = 1;
        let xp = 20;
        let maxXp = 100;
        let isMiningActive = false;
        let miningEndTime = 0;

        const balanceEl = document.getElementById('top-balance');
        const stoneEl = document.getElementById('stone-balance');
        const userLevelEl = document.getElementById('user-level');
        const displayLevelEl = document.getElementById('display-level');
        const carNameHeader = document.getElementById('car-name-header');
        const carTitle = document.getElementById('car-title');
        const carDesc = document.getElementById('car-desc');
        const carIcon = document.getElementById('car-icon');
        const xpText = document.getElementById('xp-text');
        const xpBar = document.getElementById('xp-bar');

        // Splash screen dismissal animation
        window.addEventListener('load', () => {
            const loaderBar = document.getElementById('loader-bar');
            loaderBar.style.width = '100%';
            setTimeout(() => {
                const splash = document.getElementById('splash-screen');
                splash.style.opacity = '0';
                setTimeout(() => splash.remove(), 600);
            }, 800);
            updateUI();
        });

        function updateUI() {
            balanceEl.innerText = balance.toLocaleString();
            stoneEl.innerText = stones;
            userLevelEl.innerText = level;
            displayLevelEl.innerText = level;
            xpText.innerText = xp + ' / ' + maxXp + ' XP';
            xpBar.style.width = (xp / maxXp * 100) + '%';
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.luxury-glass.border-t button, .luxury-glass.border-t button').forEach(el => {});
            document.querySelectorAll('body > .luxury-glass.border-t button').forEach(el => el.className = 'flex flex-col items-center text-gray-400 transition');
            
            document.getElementById('tab-' + tabName).classList.add('active');
            document.getElementById('nav-' + tabName).className = 'flex flex-col items-center text-amber-400 transition';
        }

        // 24H Cloud Mining Logic
        function startMining() {
            if (isMiningActive) {
                alert('⏳ Mining is already active! Check back when timer finishes.');
                return;
            }

            isMiningActive = true;
            const btn = document.getElementById('mining-btn');
            const statusText = document.getElementById('mining-status-text');
            const timerText = document.getElementById('mining-timer');
            
            btn.className = 'w-full py-4 rounded-2xl bg-gray-800 text-gray-400 font-black text-sm tracking-wider cursor-not-allowed flex items-center justify-center space-x-2';
            document.getElementById('mining-btn-text').innerText = 'MINING IN PROGRESS ⛏️';
            statusText.innerText = 'Active (24h Countdown)';

            let timeLeft = 10; // Simulated for demo speed (can be 86400 for 24h)
            let countdown = setInterval(() => {
                let hours = Math.floor(timeLeft / 3600);
                let mins = Math.floor((timeLeft % 3600) / 60);
                let secs = timeLeft % 60;
                timerText.innerText = `Time remaining: ${hours}h ${mins}m ${secs}s`;
                
                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    isMiningActive = false;
                    balance += 50000;
                    xp += 30;
                    if (xp >= maxXp) { level++; maxXp += 100; }
                    updateUI();
                    btn.className = 'w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-500 text-white font-black text-sm tracking-wider mine-btn-glow flex items-center justify-center space-x-2';
                    document.getElementById('mining-btn-text').innerText = 'CLAIM & RESTART MINING ⛏️';
                    statusText.innerText = 'Completed! Claim Reward';
                    timerText.innerText = 'Tap to start next 24h cycle.';
                }
                timeLeft--;
            }, 1000);
        }

        // Level & Car Upgrades
        function upgradeLevel(targetLevel, cost, carName, iconClass) {
            if (balance >= cost) {
                balance -= cost;
                level = targetLevel;
                carNameHeader.innerText = carName;
                carTitle.innerText = carName;
                carDesc.innerText = 'Elite Level ' + targetLevel + ' Luxury Supercar Unlocked!';
                carIcon.className = 'fa-solid ' + iconClass + ' text-5xl text-amber-400 drop-shadow-[0_0_15px_rgba(234,179,8,0.6)]';
                updateUI();
                alert('🎉 Congratulations! You unlocked ' + carName + '!');
            } else {
                alert('❌ Insufficient balance! Earn more through mining.');
            }
        }

        // Weekly Streak & Stone Reward
        function claimWeeklyStone() {
            stones += 1;
            balance += 100000;
            updateUI();
            alert('🌟 Streak Claimed! You received +1 Rare Stone 🪨 and +100,000 Coins!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
