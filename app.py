from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Nexus Tap Pro - Crypto Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        .tap-btn { transition: transform 0.05s ease; }
        .tap-btn:active { transform: scale(0.90); }
        .float-text {
            position: absolute; font-weight: 900; font-size: 2rem; color: #fbbf24;
            text-shadow: 0 0 15px rgba(251, 191, 36, 0.9); pointer-events: none;
            animation: floatUp 0.7s ease-out forwards;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0) scale(1); }
            100% { opacity: 0; transform: translateY(-120px) scale(1.4); }
        }
        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; }
        .glass-panel { background: rgba(17, 24, 39, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); }
    </style>
</head>
<body class="flex flex-col h-screen justify-between">

    <!-- Top Profile & Balance Header -->
    <div class="px-5 pt-4 flex justify-between items-center bg-gray-900/80 pb-3 border-b border-gray-800">
        <div class="flex items-center space-x-3">
            <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <i class="fa-solid fa-gamepad text-gray-950 text-xl font-bold"></i>
            </div>
            <div>
                <h2 class="text-xs font-bold text-gray-400">PLAYER RANK</h2>
                <p class="text-sm font-extrabold text-amber-400">Grandmaster</p>
            </div>
        </div>
        <div class="glass-panel px-4 py-2 rounded-2xl flex items-center space-x-2">
            <i class="fa-solid fa-coins text-amber-400 text-base"></i>
            <span id="top-balance" class="font-black text-base text-amber-300">0</span>
        </div>
    </div>

    <!-- MAIN TAB: TAP TO EARN GAME -->
    <div id="tab-tap" class="tab-content active flex-1 p-5 justify-between items-center">
        <div class="text-center mt-3">
            <p class="text-xs text-gray-400 uppercase tracking-widest font-bold mb-1">Total Earned Coins</p>
            <div class="flex items-center justify-center space-x-2">
                <i class="fa-solid fa-coins text-3xl text-amber-400 animate-pulse"></i>
                <span id="balance" class="text-5xl font-black tracking-tight text-white">0</span>
            </div>
        </div>

        <!-- Big Tap Coin Button -->
        <div id="tap-zone" class="tap-btn relative w-64 h-64 rounded-full bg-gradient-to-b from-amber-400 via-yellow-500 to-amber-700 p-2 shadow-[0_0_60px_rgba(245,158,11,0.35)] cursor-pointer flex items-center justify-center border-4 border-amber-200">
            <div class="w-full h-full rounded-full bg-gray-950 flex items-center justify-center border-2 border-amber-500/40 shadow-inner">
                <i class="fa-solid fa-bolt text-7xl text-amber-400 drop-shadow-[0_0_20px_rgba(245,158,11,0.8)]"></i>
            </div>
        </div>

        <!-- Energy Bar Section -->
        <div class="w-full max-w-xs mb-3">
            <div class="flex justify-between text-xs font-bold text-gray-400 mb-1.5">
                <span class="flex items-center gap-1"><i class="fa-solid fa-bolt text-amber-400"></i> Energy</span>
                <div><span id="energy">1000</span> / <span id="max-energy">1000</span></div>
            </div>
            <div class="w-full bg-gray-900 h-3.5 rounded-full overflow-hidden p-0.5 border border-gray-800">
                <div id="energy-bar" class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full w-full rounded-full transition-all duration-100"></div>
            </div>
        </div>
    </div>

    <!-- TAB: BOOSTS & UPGRADES -->
    <div id="tab-boost" class="tab-content flex-1 p-5 overflow-y-auto space-y-4">
        <div>
            <h2 class="text-xl font-black text-white">Store & Boosters</h2>
            <p class="text-xs text-gray-400">Upgrade your power to earn faster.</p>
        </div>
        <div class="space-y-3">
            <div onclick="buyMultiTap()" class="glass-panel p-4 rounded-2xl flex justify-between items-center cursor-pointer active:scale-98 transition shadow-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400"><i class="fa-solid fa-hand-pointer text-lg"></i></div>
                    <div>
                        <h3 class="font-bold text-sm text-white">Multitap Booster</h3>
                        <p class="text-xs text-gray-400">+1 Coin per tap (Lvl <span id="multi-lvl">1</span>)</p>
                    </div>
                </div>
                <button class="bg-amber-500 hover:bg-amber-400 text-gray-950 font-black px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md">
                    <i class="fa-solid fa-coins"></i> <span id="multi-cost">100</span>
                </button>
            </div>
            <div onclick="buyEnergyBoost()" class="glass-panel p-4 rounded-2xl flex justify-between items-center cursor-pointer active:scale-98 transition shadow-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400"><i class="fa-solid fa-battery-high text-lg"></i></div>
                    <div>
                        <h3 class="font-bold text-sm text-white">Max Energy Pack</h3>
                        <p class="text-xs text-gray-400">+500 Limit (Lvl <span id="energy-lvl">1</span>)</p>
                    </div>
                </div>
                <button class="bg-amber-500 hover:bg-amber-400 text-gray-950 font-black px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md">
                    <i class="fa-solid fa-coins"></i> <span id="energy-cost">200</span>
                </button>
            </div>
        </div>
    </div>

    <!-- TAB: TASKS & REWARDS -->
    <div id="tab-tasks" class="tab-content flex-1 p-5 overflow-y-auto space-y-4">
        <div>
            <h2 class="text-xl font-black text-white">Daily Tasks</h2>
            <p class="text-xs text-gray-400">Complete tasks to claim instant cash rewards.</p>
        </div>
        <div class="space-y-3">
            <div id="task-1" onclick="completeTask('task-1', 5000)" class="glass-panel p-4 rounded-2xl flex justify-between items-center cursor-pointer">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-sky-500/20 flex items-center justify-center text-sky-400"><i class="fa-brands fa-telegram text-xl"></i></div>
                    <div>
                        <h3 class="font-bold text-sm text-white">Join Telegram Channel</h3>
                        <p class="text-xs text-amber-400 font-bold">+5,000 Coins</p>
                    </div>
                </div>
                <button class="bg-gray-800 text-amber-400 border border-amber-500/30 font-bold px-3.5 py-1.5 rounded-xl text-xs">Claim</button>
            </div>
            <div id="task-2" onclick="completeTask('task-2', 10000)" class="glass-panel p-4 rounded-2xl flex justify-between items-center cursor-pointer">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-pink-500/20 flex items-center justify-center text-pink-400"><i class="fa-brands fa-youtube text-xl"></i></div>
                    <div>
                        <h3 class="font-bold text-sm text-white">Subscribe YouTube Channel</h3>
                        <p class="text-xs text-amber-400 font-bold">+10,000 Coins</p>
                    </div>
                </div>
                <button class="bg-gray-800 text-amber-400 border border-amber-500/30 font-bold px-3.5 py-1.5 rounded-xl text-xs">Claim</button>
            </div>
        </div>
    </div>

    <!-- Bottom Navigation Bar -->
    <div class="glass-panel border-t border-gray-800 px-6 py-2.5 flex justify-around items-center z-50">
        <button onclick="switchTab('tap')" id="nav-tap" class="flex flex-col items-center text-amber-400 transition">
            <i class="fa-solid fa-hand-pointer text-xl"></i>
            <span class="text-[11px] mt-1 font-bold">Tap Game</span>
        </button>
        <button onclick="switchTab('boost')" id="nav-boost" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-rocket text-xl"></i>
            <span class="text-[11px] mt-1 font-bold">Boosts</span>
        </button>
        <button onclick="switchTab('tasks')" id="nav-tasks" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-list-check text-xl"></i>
            <span class="text-[11px] mt-1 font-bold">Tasks</span>
        </button>
    </div>

    <script>
        let balance = 0;
        let energy = 1000;
        let maxEnergy = 1000;
        let tapValue = 1;
        let multiCost = 100;
        let multiLvl = 1;
        let energyCost = 200;
        let energyLvl = 1;

        const balanceEl = document.getElementById('balance');
        const topBalanceEl = document.getElementById('top-balance');
        const energyEl = document.getElementById('energy');
        const maxEnergyEl = document.getElementById('max-energy');
        const energyBar = document.getElementById('energy-bar');
        const tapZone = document.getElementById('tap-zone');

        function updateUI() {
            balanceEl.innerText = balance.toLocaleString();
            topBalanceEl.innerText = balance.toLocaleString();
            energyEl.innerText = energy;
            maxEnergyEl.innerText = maxEnergy;
            energyBar.style.width = (energy / maxEnergy * 100) + '%';
        }

        tapZone.addEventListener('pointerdown', (e) => {
            if (energy < tapValue) return;
            balance += tapValue;
            energy -= tapValue;
            updateUI();

            const floatText = document.createElement('div');
            floatText.className = 'float-text';
            floatText.innerText = '+' + tapValue;
            floatText.style.left = (e.clientX - 20) + 'px';
            floatText.style.top = (e.clientY - 40) + 'px';
            document.body.appendChild(floatText);
            setTimeout(() => floatText.remove(), 700);
        });

        setInterval(() => {
            if (energy < maxEnergy) {
                energy = Math.min(maxEnergy, energy + 5);
                updateUI();
            }
        }, 1000);

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.glass-panel button, .glass-panel div button').forEach(el => {});
            document.querySelectorAll('nav button, .glass-panel.border-t button').forEach(el => el.className = 'flex flex-col items-center text-gray-400 transition');
            
            document.getElementById('tab-' + tabName).classList.add('active');
            document.getElementById('nav-' + tabName).className = 'flex flex-col items-center text-amber-400 transition';
        }

        function buyMultiTap() {
            if (balance >= multiCost) {
                balance -= multiCost;
                tapValue += 1;
                multiLvl += 1;
                multiCost *= 2;
                document.getElementById('multi-lvl').innerText = multiLvl;
                document.getElementById('multi-cost').innerText = multiCost;
                updateUI();
            }
        }

        function buyEnergyBoost() {
            if (balance >= energyCost) {
                balance -= energyCost;
                maxEnergy += 500;
                energy = maxEnergy;
                energyLvl += 1;
                energyCost *= 2;
                document.getElementById('energy-lvl').innerText = energyLvl;
                document.getElementById('energy-cost').innerText = energyCost;
                updateUI();
            }
        }

        function completeTask(taskId, reward) {
            const taskCard = document.getElementById(taskId);
            const btn = taskCard.querySelector('button');
            if (btn.innerText === 'Claim') {
                balance += reward;
                updateUI();
                btn.innerText = 'Done';
                btn.className = 'bg-emerald-600 text-white font-bold px-3.5 py-1.5 rounded-xl text-xs';
                taskCard.style.opacity = '0.6';
            }
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
