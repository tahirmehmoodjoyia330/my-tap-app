from flask import Flask, render_template_string

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Tap to Earn - Pro Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { user-select: none; -webkit-user-select: none; background: #0f172a; font-family: sans-serif; overflow: hidden; }
        .tap-btn { transition: transform 0.05s ease; }
        .tap-btn:active { transform: scale(0.92); }
        .float-text {
            position: absolute; font-weight: 800; font-size: 1.8rem; color: #f59e0b;
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.8); pointer-events: none;
            animation: floatUp 0.8s ease-out forwards;
        }
        @keyframes floatUp {
            0% { opacity: 1; transform: translateY(0) scale(1); }
            100% { opacity: 0; transform: translateY(-100px) scale(1.3); }
        }
    </style>
</head>
<body class="h-screen flex flex-col justify-between text-white">

    <div class="p-4 bg-slate-900/80 border-b border-slate-800">
        <div class="flex justify-between items-center mb-3">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-full border-2 border-yellow-500 bg-slate-800 flex items-center justify-center">
                    <i class="fa-solid fa-user-ninja text-2xl text-yellow-500"></i>
                </div>
                <div>
                    <h3 class="font-bold text-sm text-yellow-400">PRO GAMER</h3>
                    <div class="text-xs text-slate-400">Level 1 / 30</div>
                </div>
            </div>
            <div class="bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-700 flex items-center gap-2">
                <i class="fa-solid fa-coins text-yellow-500"></i>
                <span id="balance" class="font-black text-sm">0</span>
            </div>
        </div>
    </div>

    <div class="relative flex-1 flex flex-col items-center justify-center" id="tap-zone">
        <div class="tap-btn relative w-64 h-64 rounded-full bg-slate-800/50 border-4 border-yellow-500/30 flex items-center justify-center cursor-pointer shadow-2xl">
            <img src="https://cdn-icons-png.flaticon.com/512/616/616408.png" class="w-48 h-48 object-contain pointer-events-none">
        </div>
    </div>

    <div class="p-4 bg-slate-900/90 border-t border-slate-800">
        <div class="flex justify-between items-center mb-4 px-2">
            <div class="flex items-center gap-2 text-yellow-400 font-bold">
                <i class="fa-solid fa-bolt text-lg"></i>
                <span id="energy">500</span> / 500
            </div>
        </div>
    </div>

    <script>
        let balance = 0;
        let energy = 500;
        const balanceEl = document.getElementById('balance');
        const energyEl = document.getElementById('energy');
        const tapZone = document.getElementById('tap-zone');

        tapZone.addEventListener('pointerdown', (e) => {
            if (energy <= 0) return;
            balance += 1;
            energy -= 1;
            balanceEl.innerText = balance.toLocaleString();
            energyEl.innerText = energy;

            const floatText = document.createElement('div');
            floatText.className = 'float-text';
            floatText.innerText = '+1';
            floatText.style.left = `${e.clientX - 15}px`;
            floatText.style.top = `${e.clientY - 30}px`;
            document.body.appendChild(floatText);

            setTimeout(() => floatText.remove(), 800);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
