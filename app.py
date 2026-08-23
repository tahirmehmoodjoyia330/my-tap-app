from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Nexus Tap Pro - Addictive Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; background-color: #07090e; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        .tap-btn { transition: transform 0.05s ease; }
        .tap-btn:active { transform: scale(0.88); }
        .float-text {
            position: absolute; font-weight: 900; font-size: 2.2rem; color: #fbbf24;
            text-shadow: 0 0 20px rgba(251, 191, 36, 1); pointer-events: none;
            animation: floatUp 0.7s ease-out forwards;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0) scale(1); }
            100% { opacity: 0; transform: translateY(-130px) scale(1.5); }
        }
        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; }
        .glass-panel { background: rgba(17, 24, 39, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .side-panel-btn { writing-mode: vertical-lr; text-orientation: mixed; }
    </style>
</head>
<body class="flex flex-col h-screen justify-between">

    <!-- Top Profile & Balance Header -->
    <div class="px-4 pt-3 flex justify-between items-center bg-gray-950/90 pb-2.5 border-b border-gray-800/80 z-20">
        <div class="flex items-center space-x-2.5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <i class="fa-solid fa-crown text-gray-950 text-base font-bold"></i>
            </div>
            <div>
                <h2 class="text-[10px] font-bold text-gray-400">STATUS</h2>
                <p class="text-xs font-extrabold text-amber-400">Elite Master</p>
            </div>
        </div>
        <div class="glass-panel px-3.5 py-1.5 rounded-2xl flex items-center space-x-2">
            <i class="fa-solid fa-coins text-amber-400 text-sm"></i>
            <span id="top-balance" class="font-black text-sm text-amber-300">0</span>
        </div>
    </div>

    <!-- MAIN TAB: TAP GAME WITH SIDE PANELS & STREAK -->
    <div id="tab-tap" class="tab-content active flex-1 p-3 justify-between items-center relative overflow-hidden">
        
        <!-- TOP CORNERS: 24H Daily Streak & Bonus Drop -->
        <div class="w-full flex justify-between items-center px-1 z-10">
            <div onclick="claimStreak()" id="streak-btn" class="glass-panel px-3 py-2 rounded-xl flex items-center space-x-2 cursor-pointer border-amber-500/30 active:scale-95 transition">
                <i class="fa-solid fa-fire text-amber-400 text-base animate-bounce"></i>
                <div>
                    <p class="text-[9px] text-gray-400 font-bold">24H STREAK</p>
                    <p class="text-xs font-black text-amber-300" id="streak-timer">Claim +2,500</p>
                </div>
            </div>
            <div onclick="claimBonusDrop()" class="glass-panel px-3 py-2 rounded-xl flex items-center space-x-2 cursor-pointer border-purple-500/30 active:scale-95 transition">
                <div class="text-right">
                    <p class="text-[9px] text-gray-400 font-bold">MEGA DROP</p>
                    <p class="text-xs font-black text-purple-400">Ready!</p>
                </div>
                <i class="fa-solid fa-gift text-purple-400 text-base animate-pulse"></i>
            </div>
        </div>

        <!-- LEFT & RIGHT SIDE PANELS (Aapki lines wali jagah par extra engaging tasks/boosts) -->
        <div class="absolute left-1 top-1/2 -translate-y-1/2 flex flex-col space-y-2 z-10">
            <div onclick="openMiniGame('spin')" class="glass-panel p-2.5 rounded-xl text-center cursor-pointer hover:bg-gray-800 transition active:scale-95 shadow-lg">
                <i class="fa-solid fa-dharmachakra text-amber-400 text-lg mb-1"></i>
                <span class="side-panel-btn text-[10px] font-bold text-gray-300 tracking-wider">SPIN WHEEL</span>
            </div>
            <div onclick="openMiniGame('lottery')" class="glass-panel p-2.5 rounded-xl text-center cursor-pointer hover:bg-gray-800 transition active:scale-95 shadow-lg">
                <i class="fa-solid fa-ticket text-emerald-400 text-lg mb-1"></i>
                <span class="side-panel-btn text-[10px] font-bold text-gray-300 tracking-wider">JACKPOT</span>
            </div>
        </div>

        <div class="absolute right-1 top-1/2 -translate-y-1/2 flex flex-col space-y-2 z-10">
            <div onclick="openMiniGame('mine')" class="glass-panel p-2.5 rounded-xl text-center cursor-pointer hover:bg-gray-800 transition active:scale-95 shadow-lg">
                <i class="fa-solid fa-hammer text-blue-400 text-lg mb-1"></i>
                <span class="side-panel-btn text-[10px] font-bold text-gray-300 tracking-wider">AUTO MINER</span>
            </div>
            <div onclick="openMiniGame('vault')" class="glass-panel p-2.5 rounded-xl text-center cursor-pointer hover:bg-gray-800 transition active:scale-95 shadow-lg">
                <i class="fa-solid fa-vault text-purple-400 text-lg mb-1"></i>
                <span class="side-panel-btn text-[10px] font-bold text-gray-300 tracking-wider">SECRET VAULT</span>
            </div>
        </div>

        <!-- Center Score Display -->
        <div class="text-center my-1 z-10">
            <p class="text-[10px] text-gray-400 uppercase tracking-widest font-black">TOTAL COINS</p>
            <div class="flex items-center justify-center space-x-2">
                <i class="fa-solid fa-coins text-2xl text-amber-400"></i>
                <span id="balance" class="text-4xl font-black tracking-tight text-white">0</span>
            </div>
        </div>

        <!-- Main Giant Tap Button -->
        <div id="tap-zone" class="tap-btn relative w-56 h-56 rounded-full bg-gradient-to-b from-amber-400 via-yellow-500 to-amber-700 p-2 shadow-[0_0_50px_rgba(245,158,11,0.4)] cursor-pointer flex items-center justify-center border-4 border-amber-200 z-10 my-2">
            <div class="w-full h-full rounded-full bg-gray-950 flex items-center justify-center border-2 border-amber-500/50 shadow-inner">
                <i class="fa-solid fa-bolt text-6xl text-amber-400 drop-shadow-[0_0_20px_rgba(245,158,11,0.9)] animate-pulse"></i>
            </div>
        </div>

        <!-- Energy Bar -->
        <div class="w-full max-w-xs mb-1 z-10">
            <div class="flex justify-between text-xs font-bold text-gray-400 mb-1">
                <span class="flex items-center gap-1"><i class="fa-solid fa-bolt text-amber-400"></i> Energy</span>
                <div><span id="energy">1500</span> / <span id="max-energy">1500</span></div>
            </div>
            <div class="w-full bg-gray-900 h-3 rounded-full overflow-hidden p-0.5 border border-gray-800">
                <div id="energy-bar" class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full w-full rounded-full transition-all duration-100"></div>
            </div>
        </div>
    </div>

    <!-- TAB: BOOSTS -->
    <div id="tab-boost" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <div>
            <h2 class="text-lg font-black text-white">Power Store</h2>
            <p class="text-xs text-gray-400">Upgrade your earning multiplier.</p>
        </div>
        <div class="space-y-2.5">
            <div onclick="buyMultiTap()" class="glass-panel p-3.5 rounded-xl flex justify-between items-center cursor-pointer active:scale-98">
                <div class="flex items-center space-x-3">
                    <div class="w-9 h-9 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400"><i class="fa-solid fa-hand-pointer"></i></div>
                    <div>
                        <h3 class="font-bold text-xs text-white">Multitap Power</h3>
                        <p class="text-[11px] text-gray-400">+1 per tap (Lvl <span id="multi-lvl">1</span>)</p>
                    </div>
                </div>
                <button class="bg-amber-500 text-gray-950 font-black px-3 py-1.5 rounded-lg text-xs flex items-center gap-1">
                    <i class="fa-solid fa-coins"></i> <span id="multi-cost">100</span>
                </button>
            </div>
        </div>
    </div>

    <!-- TAB: TASKS -->
    <div id="tab-tasks" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <div>
            <h2 class="text-lg font-black text-white">Active Missions</h2>
            <p class="text-xs text-gray-400">Complete tasks for huge coin bonuses.</p>
        </div>
        <div class="space-y-2.5">
            <div id="task-1" onclick="completeTask('task-1', 10000)" class="glass-panel p-3.5 rounded-xl flex justify-between items-center cursor-pointer">
                <div class="flex items-center space-x-3">
                    <div class="w-9 h-9 rounded-lg bg-sky-500/20 flex items-center justify-center text-sky-400"><i class="fa-brands fa-telegram text-lg"></i></div>
                    <div>
                        <h3 class="font-bold text-xs text-white">Join Community Channel</h3>
                        <p class="text-[11px] text-amber-400 font-bold">+10,000 Coins</p>
                    </div>
                </div>
                <button class="bg-gray-800 text-amber-400 border border-amber-500/30 font-bold px-3 py-1 rounded-lg text-xs">Claim</button>
            </div>
        </div>
    </div>

    <!-- Bottom Navigation Bar -->
    <div class="glass-panel border-t border-gray-800 px-6 py-2 flex justify-around items-center z-20">
        <button onclick="switchTab('tap')" id="nav-tap" class="flex flex-col items-center text-amber-400 transition">
            <i class="fa-solid fa-gamepad text-lg"></i>
            <span class="text-[10px] mt-0.5 font-bold">Game</span>
        </button>
        <button onclick="switchTab('boost')" id="nav-boost" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-rocket text-lg"></i>
            <span class="text-[10px] mt-0.5 font-bold">Boosts</span>
        </button>
        <button onclick="switchTab('tasks')" id="nav-tasks" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-list-check text-lg"></i>
            <span class="text-[10px] mt-0.5 font-bold">Tasks</span>
        </button>
    </div>

    <script>
        let balance = 0;
        let energy = 1500;
        let maxEnergy = 1500;
        let tapValue = 1;
        let multiCost = 100;
        let multiLvl = 1;

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
                energy = Math.min(maxEnergy, energy + 8);
                updateUI();
            }
        }, 1000);

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.glass-panel.border-t button').forEach(el => el.className = 'flex flex-col items-center text-gray-400 transition');
            
            document.getElementById('tab-' + tabName).classList.add('active');
            document.getElementById('nav-' + tabName).className = 'flex flex-col items-center text-amber-400 transition';
        }

        function claimStreak() {
            balance += 2500;
            updateUI();
            const btn = document.getElementById('streak-btn');
            btn.style.opacity = '0.5';
            document.getElementById('streak-timer').innerText = 'Claimed!';
            setTimeout(() => {
                btn.style.opacity = '1';
                document.getElementById('streak-timer').innerText = 'Claim +2,500';
            }, 10000);
        }

        function claimBonusDrop() {
            balance += 5000;
            updateUI();
            alert('🎉 Mega Drop Claimed: +5,000 Coins added!');
        }

        function openMiniGame(type) {
            let reward = Math.floor(Math.random() * 3000) + 1000;
            balance += reward;
            updateUI();
            alert('🎁 ' + type.toUpperCase() + ' Bonus! You won +' + reward.toLocaleString() + ' Coins!');
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

        function completeTask(taskId, reward) {
            const taskCard = document.getElementById(taskId);
            const btn = taskCard.querySelector('button');
            if (btn.innerText === 'Claim') {
                balance += reward;
                updateUI();
                btn.innerText = 'Done';
                btn.className = 'bg-emerald-600 text-white font-bold px-3 py-1 rounded-lg text-xs';
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
