from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Bums Pro Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; background-color: #0b131d; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        .tap-btn { transition: transform 0.04s ease; }
        .tap-btn:active { transform: scale(0.92); }
        .float-text {
            position: absolute; font-weight: 900; font-size: 2.2rem; color: #fbbf24;
            text-shadow: 0 0 15px rgba(251, 191, 36, 0.9); pointer-events: none;
            animation: floatUp 0.7s ease-out forwards;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0) scale(1); }
            100% { opacity: 0; transform: translateY(-130px) scale(1.4); }
        }
        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; }
        .side-btn { background: rgba(22, 33, 49, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.12); box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        .glass-panel { background: rgba(18, 26, 38, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="flex flex-col h-screen justify-between">

    <!-- Top Header & Stats -->
    <div class="px-3 pt-2.5 flex justify-between items-center bg-gray-950/90 pb-2 border-b border-gray-800 z-20">
        <div class="flex items-center space-x-2">
            <div class="relative">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-yellow-400 flex items-center justify-center border border-amber-300">
                    <i class="fa-solid fa-user-ninja text-gray-950 text-lg font-black"></i>
                </div>
                <span class="absolute -bottom-1 -right-1 bg-blue-600 text-[9px] font-bold px-1 rounded text-white">Lv.15</span>
            </div>
            <div>
                <div class="w-16 bg-gray-800 h-2 rounded-full overflow-hidden border border-gray-700 mt-1">
                    <div class="bg-blue-500 h-full w-2/3"></div>
                </div>
                <span class="text-[9px] text-gray-400 font-bold">65% Progress</span>
            </div>
        </div>

        <!-- Currencies Bar -->
        <div class="flex items-center space-x-2">
            <div class="glass-panel px-2.5 py-1 rounded-xl flex items-center space-x-1.5 border-amber-500/30">
                <i class="fa-solid fa-coins text-amber-400 text-xs"></i>
                <span id="top-balance" class="font-black text-xs text-amber-300">22.3T</span>
            </div>
            <div class="glass-panel px-2.5 py-1 rounded-xl flex items-center space-x-1.5 border-blue-500/30">
                <i class="fa-solid fa-gem text-blue-400 text-xs"></i>
                <span class="font-black text-xs text-blue-300">70,680</span>
            </div>
        </div>
    </div>

    <!-- MAIN HOME TAB: BUMS EXACT LAYOUT -->
    <div id="tab-home" class="tab-content active flex-1 p-2 justify-between items-center relative overflow-hidden">
        
        <!-- Background Lighting Effect -->
        <div class="absolute inset-0 bg-radial from-teal-900/20 via-transparent to-transparent pointer-events-none"></div>

        <!-- LEFT SIDE MENU BUTTONS -->
        <div class="absolute left-2 top-14 flex flex-col space-y-2 z-10">
            <div onclick="triggerAction('Special Offer unlocked!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-fire text-amber-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">OFFER</p>
            </div>
            <div onclick="triggerAction('Upgrades opened!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-arrow-up-right-dots text-emerald-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">UPGRADE</p>
            </div>
            <div onclick="triggerAction('Passport verified!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-id-card text-blue-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">PASSPORT</p>
            </div>
            <div onclick="triggerAction('Skinshop opened!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-shirt text-purple-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">SKINSHOP</p>
            </div>
            <div onclick="switchTab('tasks')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-list-check text-yellow-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">TASK</p>
            </div>
            <div onclick="triggerAction('Invite link copied!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-user-plus text-pink-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">INVITE</p>
            </div>
        </div>

        <!-- RIGHT SIDE MENU BUTTONS -->
        <div class="absolute right-2 top-14 flex flex-col space-y-2 z-10">
            <div onclick="triggerAction('Daily task claimed!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-calendar-days text-amber-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">DAILY</p>
            </div>
            <div onclick="triggerAction('Avatar battle queued!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-shield-halved text-rose-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">BATTLE</p>
            </div>
            <div onclick="triggerAction('Expedition started!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-compass text-sky-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">EXPEDITION</p>
            </div>
            <div onclick="triggerAction('Autotap activated!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-robot text-purple-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">AUTOTAP</p>
            </div>
            <div onclick="triggerAction('Launchpad open!')" class="side-btn p-2 rounded-xl text-center cursor-pointer active:scale-95 w-14">
                <i class="fa-solid fa-rocket text-indigo-400 text-sm"></i>
                <p class="text-[9px] font-black text-gray-200 mt-0.5">LAUNCH</p>
            </div>
        </div>

        <!-- Center Big Counter -->
        <div class="text-center z-10 mt-1">
            <span id="balance" class="text-3xl font-black tracking-tight text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">22,294,936,245,44</span>
        </div>

        <!-- Central Character & Tap Zone -->
        <div id="tap-zone" class="tap-btn relative w-48 h-64 flex flex-col items-center justify-center cursor-pointer z-10 my-auto">
            <div class="absolute inset-0 bg-teal-500/10 rounded-full blur-xl pointer-events-none"></div>
            <i class="fa-solid fa-user-secret text-8xl text-teal-400 drop-shadow-[0_0_25px_rgba(45,212,191,0.6)] mb-2"></i>
            <h2 class="text-2xl font-black tracking-wider text-white drop-shadow-md">Tap Me</h2>
        </div>

        <!-- Bottom Energy & Per Tap Stats -->
        <div class="w-full px-4 mb-1 z-10 flex flex-col space-y-1.5">
            <div class="flex justify-between items-center">
                <div class="w-36 bg-gray-900 h-3 rounded-full overflow-hidden border border-gray-800 p-0.5">
                    <div id="energy-bar" class="bg-blue-500 h-full w-3/4 rounded-full"></div>
                </div>
                <div class="flex items-center space-x-1.5 bg-gray-900/90 px-3 py-1 rounded-xl border border-gray-800">
                    <i class="fa-solid fa-coins text-amber-400 text-xs"></i>
                    <span class="font-black text-xs text-white">+3,522</span>
                    <span class="text-[10px] text-gray-400">Per tap</span>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: GAME CENTER -->
    <div id="tab-game" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <h2 class="text-lg font-black text-amber-400">Game Center</h2>
        <div onclick="triggerAction('Mini-game launched!')" class="glass-panel p-4 rounded-2xl cursor-pointer flex justify-between items-center">
            <div>
                <h3 class="font-bold text-sm">Lucky Battle Arena</h3>
                <p class="text-xs text-gray-400">Play & win massive coin rewards.</p>
            </div>
            <button class="bg-amber-500 text-gray-950 font-bold px-3 py-1.5 rounded-xl text-xs">Play</button>
        </div>
    </div>

    <!-- TAB 3: SLOT -->
    <div id="tab-slot" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <h2 class="text-lg font-black text-amber-400">Slot Machine</h2>
        <div onclick="triggerAction('Spinning slot... Win!')" class="glass-panel p-6 text-center rounded-2xl cursor-pointer">
            <i class="fa-solid fa-dice text-4xl text-amber-400 mb-2"></i>
            <h3 class="font-bold text-base">Tap to Spin & Win</h3>
            <p class="text-xs text-gray-400 mt-1">Get 3 matching icons for jackpot!</p>
        </div>
    </div>

    <!-- TAB 4: TREASURE HUNTER -->
    <div id="tab-treasure" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <h2 class="text-lg font-black text-amber-400">Treasure Hunter</h2>
        <div onclick="triggerAction('Chest opened! +50,000 Coins')" class="glass-panel p-4 rounded-2xl cursor-pointer flex justify-between items-center">
            <div>
                <h3 class="font-bold text-sm">Mystery Gold Chest</h3>
                <p class="text-xs text-gray-400">Unlock to reveal hidden treasures.</p>
            </div>
            <button class="bg-purple-600 text-white font-bold px-3 py-1.5 rounded-xl text-xs">Open</button>
        </div>
    </div>

    <!-- TAB 5: ALPHA -->
    <div id="tab-alpha" class="tab-content flex-1 p-4 overflow-y-auto space-y-3">
        <h2 class="text-lg font-black text-amber-400">Alpha Ecosystem</h2>
        <div class="glass-panel p-4 rounded-2xl">
            <h3 class="font-bold text-sm">Exclusive Node Status</h3>
            <p class="text-xs text-gray-400 mt-1">Connected to decentralized Bums liquidity cluster.</p>
        </div>
    </div>

    <!-- Bottom Navigation Bar (5 Exact Tabs like Bums) -->
    <div class="glass-panel border-t border-gray-800 px-2 py-2 flex justify-around items-center z-20">
        <button onclick="switchTab('home')" id="nav-home" class="flex flex-col items-center text-amber-400 transition">
            <i class="fa-solid fa-house text-base"></i>
            <span class="text-[9px] mt-1 font-bold">HOME</span>
        </button>
        <button onclick="switchTab('game')" id="nav-game" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-gamepad text-base"></i>
            <span class="text-[9px] mt-1 font-bold">GAME CENTER</span>
        </button>
        <button onclick="switchTab('slot')" id="nav-slot" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-dice text-base"></i>
            <span class="text-[9px] mt-1 font-bold">SLOT</span>
        </button>
        <button onclick="switchTab('treasure')" id="nav-treasure" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-chess-rook text-base"></i>
            <span class="text-[9px] mt-1 font-bold">TREASURE</span>
        </button>
        <button onclick="switchTab('alpha')" id="nav-alpha" class="flex flex-col items-center text-gray-400 transition">
            <i class="fa-solid fa-box-archive text-base"></i>
            <span class="text-[9px] mt-1 font-bold">ALPHA</span>
        </button>
    </div>

    <script>
        let balance = 2229493624544;
        const balanceEl = document.getElementById('balance');
        const topBalanceEl = document.getElementById('top-balance');
        const tapZone = document.getElementById('tap-zone');

        tapZone.addEventListener('pointerdown', (e) => {
            balance += 3522;
            topBalanceEl.innerText = (balance / 1e9).toFixed(1) + 'B';
            balanceEl.innerText = balance.toLocaleString();

            const floatText = document.createElement('div');
            floatText.className = 'float-text';
            floatText.innerText = '+3,522';
            floatText.style.left = (e.clientX - 25) + 'px';
            floatText.style.top = (e.clientY - 40) + 'px';
            document.body.appendChild(floatText);
            setTimeout(() => floatText.remove(), 700);
        });

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.glass-panel.border-t button').forEach(el => el.className = 'flex flex-col items-center text-gray-400 transition');
            
            document.getElementById('tab-' + tabName).classList.add('active');
            document.getElementById('nav-' + tabName).className = 'flex flex-col items-center text-amber-400 transition';
        }

        function triggerAction(msg) {
            alert('⚡ ' + msg);
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
