from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropee Tap Bot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; }
        .tap-btn:active { transform: scale(0.92); }
        .floating-text {
            position: absolute;
            animation: floatUp 0.8s ease-out forwards;
            font-weight: bold;
            color: #60a5fa;
            pointer-events: none;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0px) scale(1); }
            100% { opacity: 0; transform: translateY(-80px) scale(1.5); }
        }
    </style>
</head>
<body class="bg-[#0b0e14] text-white flex flex-col h-screen justify-between font-sans">

    <!-- Header Balance Section -->
    <div class="p-5 bg-gradient-to-b from-[#161b26] to-[#0b0e14] text-center border-b border-gray-800/50 shadow-lg">
        <p class="text-gray-400 text-xs tracking-wider uppercase">Total Balance</p>
        <div class="flex items-center justify-center gap-2 mt-1">
            <i class="fa-solid fa-coins text-yellow-400 text-3xl"></i>
            <h1 id="balance" class="text-4xl font-extrabold text-white tracking-tight">1,000</h1>
        </div>
    </div>

    <!-- TAB 1: TAP SCREEN -->
    <div id="tab-tap" class="tab-content flex-1 flex flex-col items-center justify-center p-4 relative overflow-hidden">
        
        <div id="tap-area" onclick="handleTap(event)" class="tap-btn w-64 h-64 rounded-full bg-gradient-to-tr from-blue-700 via-blue-500 to-cyan-400 p-2 shadow-[0_0_50px_rgba(37,99,235,0.4)] flex items-center justify-center cursor-pointer relative">
            <div class="w-full h-full rounded-full bg-[#0e131f] flex flex-col items-center justify-center border-2 border-blue-400/30">
                <i class="fa-solid fa-[#0e131f] fa-hand-pointer text-6xl text-blue-400 mb-2 drop-shadow-[0_0_10px_rgba(96,165,250,0.8)]"></i>
                <span class="text-lg font-black tracking-wider text-blue-200">TAP TOKEN</span>
            </div>
        </div>

        <!-- Energy Bar Section -->
        <div class="w-full max-w-xs mt-10 bg-[#161b26] p-3 rounded-2xl border border-gray-800">
            <div class="flex justify-between items-center text-xs font-semibold mb-2 px-1">
                <span class="text-yellow-400 flex items-center gap-1"><i class="fa-solid fa-bolt"></i> Energy</span>
                <span id="energy-text" class="text-gray-300">500 / 500</span>
            </div>
            <div class="w-full bg-gray-800/80 h-3 rounded-full overflow-hidden p-0.5">
                <div id="energy-bar" class="bg-gradient-to-r from-yellow-500 to-amber-300 h-full w-full rounded-full transition-all duration-200"></div>
            </div>
        </div>
    </div>

    <!-- TAB 2: TASKS SCREEN (Social Links) -->
    <div id="tab-tasks" class="tab-content hidden flex-1 p-5 overflow-y-auto">
        <h2 class="text-2xl font-bold mb-1">Earn Tasks</h2>
        <p class="text-xs text-gray-400 mb-5">Complete tasks to earn bonus rewards</p>

        <!-- YouTube Task -->
        <div class="bg-[#161b26] p-4 rounded-2xl border border-gray-800/80 flex items-center justify-between mb-3 shadow-md">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-red-600/20 text-red-500 flex items-center justify-center text-xl">
                    <i class="fa-brands fa-youtube"></i>
                </div>
                <div>
                    <p class="font-bold text-sm">Subscribe YouTube</p>
                    <p class="text-xs text-yellow-400 font-semibold">+1,000 Coins</p>
                </div>
            </div>
            <button onclick="openSocialTask('https://youtube.com', 1000, this)" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-xs font-bold transition-all">Start</button>
        </div>

        <!-- Twitter Task -->
        <div class="bg-[#161b26] p-4 rounded-2xl border border-gray-800/80 flex items-center justify-between mb-3 shadow-md">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center text-xl">
                    <i class="fa-brands fa-x-twitter"></i>
                </div>
                <div>
                    <p class="font-bold text-sm">Follow Twitter (X)</p>
                    <p class="text-xs text-yellow-400 font-semibold">+500 Coins</p>
                </div>
            </div>
            <button onclick="openSocialTask('https://x.com', 500, this)" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-xs font-bold transition-all">Start</button>
        </div>

        <!-- Telegram Task -->
        <div class="bg-[#161b26] p-4 rounded-2xl border border-gray-800/80 flex items-center justify-between mb-3 shadow-md">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center text-xl">
                    <i class="fa-brands fa-telegram"></i>
                </div>
                <div>
                    <p class="font-bold text-sm">Join Telegram Channel</p>
                    <p class="text-xs text-yellow-400 font-semibold">+800 Coins</p>
                </div>
            </div>
            <button onclick="openSocialTask('https://t.me', 800, this)" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-xs font-bold transition-all">Start</button>
        </div>
    </div>

    <!-- TAB 3: FRIENDS SCREEN -->
    <div id="tab-friends" class="tab-content hidden flex-1 p-5 text-center">
        <div class="w-16 h-16 bg-blue-600/20 text-blue-400 rounded-full flex items-center justify-center text-2xl mx-auto mb-3">
            <i class="fa-solid fa-users"></i>
        </div>
        <h2 class="text-2xl font-bold mb-1">Invite Friends</h2>
        <p class="text-xs text-gray-400 mb-6">Earn 10% commission from your friends!</p>
        
        <div class="bg-[#161b26] p-4 rounded-2xl border border-gray-800/80 text-left">
            <p class="text-xs text-gray-400 font-medium mb-2">Your Invite Link</p>
            <div class="flex gap-2">
                <input type="text" value="https://t.me/dropee_bot?start=ref123" readonly class="bg-[#0b0e14] text-blue-400 text-xs p-3 rounded-xl border border-gray-800 w-full font-mono">
                <button onclick="alert('Link Copied!')" class="bg-blue-600 px-4 rounded-xl text-xs font-bold active:scale-95 transition-all">Copy</button>
            </div>
        </div>
    </div>

    <!-- Navigation Bar -->
    <div class="bg-[#161b26] border-t border-gray-800/80 flex justify-around py-3 px-2">
        <button onclick="switchTab('tap', this)" class="nav-btn text-blue-500 flex flex-col items-center text-xs gap-1 font-bold">
            <i class="fa-solid fa-bolt text-lg"></i>
            <span>Tap</span>
        </button>
        <button onclick="switchTab('tasks', this)" class="nav-btn text-gray-500 flex flex-col items-center text-xs gap-1 font-bold">
            <i class="fa-solid fa-list-check text-lg"></i>
            <span>Tasks</span>
        </button>
        <button onclick="switchTab('friends', this)" class="nav-btn text-gray-500 flex flex-col items-center text-xs gap-1 font-bold">
            <i class="fa-solid fa-user-group text-lg"></i>
            <span>Friends</span>
        </button>
    </div>

    <script>
        let balance = 1000;
        let energy = 500;
        const maxEnergy = 500;

        function handleTap(e) {
            if (energy >= 1) {
                balance += 1;
                energy -= 1;
                
                // Floating Text Effect (+1)
                const area = document.getElementById('tab-tap');
                const text = document.createElement('div');
                text.className = 'floating-text';
                text.innerText = '+1';
                
                const rect = area.getBoundingClientRect();
                text.style.left = (e.clientX - rect.left - 10) + 'px';
                text.style.top = (e.clientY - rect.top - 20) + 'px';
                
                area.appendChild(text);
                setTimeout(() => text.remove(), 800);

                updateDisplay();
            }
        }

        function openSocialTask(url, reward, btn) {
            window.open(url, '_blank');
            btn.innerText = "Checking...";
            btn.className = "bg-yellow-600/30 text-yellow-400 border border-yellow-500/40 px-3 py-2 rounded-xl text-xs font-bold";
            
            setTimeout(() => {
                balance += reward;
                updateDisplay();
                btn.innerText = "Claimed";
                btn.disabled = true;
                btn.className = "bg-gray-800 text-gray-500 px-3 py-2 rounded-xl text-xs font-bold cursor-not-allowed";
            }, 4000);
        }

        function updateDisplay() {
            document.getElementById('balance').innerText = balance.toLocaleString();
            document.getElementById('energy-text').innerText = energy + " / " + maxEnergy;
            document.getElementById('energy-bar').style.width = (energy / maxEnergy * 100) + "%";
        }

        function switchTab(tabName, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.nav-btn').forEach(el => el.className = 'nav-btn text-gray-500 flex flex-col items-center text-xs gap-1 font-bold');
            
            document.getElementById('tab-' + tabName).classList.remove('hidden');
            btn.className = 'nav-btn text-blue-500 flex flex-col items-center text-xs gap-1 font-bold';
        }

        setInterval(() => {
            if (energy < maxEnergy) {
                energy += 1;
                updateDisplay();
            }
        }, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
