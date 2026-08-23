from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexusAI Pro - Financial & Task Intelligence</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #030712; color: #f3f4f6; font-family: 'Inter', sans-serif; }
        .glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="glass-card border-b border-gray-800 px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <i class="fa-solid fa-network-wired text-white text-lg"></i>
            </div>
            <div>
                <h1 class="font-bold text-lg tracking-wide bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">NexusAI Pro</h1>
                <p class="text-xs text-gray-400">Enterprise Cloud Dashboard</p>
            </div>
        </div>
        <div class="flex items-center space-x-3">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span class="w-2 h-2 mr-1.5 rounded-full bg-emerald-500 animate-pulse"></span> System Live
            </span>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="glass-card p-5 rounded-2xl shadow-xl">
                <div class="flex justify-between items-center text-gray-400 mb-2">
                    <span class="text-sm font-medium">Total Portfolio</span>
                    <i class="fa-solid fa-wallet text-blue-400"></i>
                </div>
                <h3 class="text-2xl font-bold text-white">$24,892.50</h3>
                <span class="text-xs text-emerald-400 font-semibold mt-1 inline-block"><i class="fa-solid fa-arrow-trend-up"></i> +14.2% this month</span>
            </div>
            <div class="glass-card p-5 rounded-2xl shadow-xl">
                <div class="flex justify-between items-center text-gray-400 mb-2">
                    <span class="text-sm font-medium">Active Tasks</span>
                    <i class="fa-solid fa-list-check text-indigo-400"></i>
                </div>
                <h3 class="text-2xl font-bold text-white">12 / 15</h3>
                <span class="text-xs text-indigo-400 font-semibold mt-1 inline-block">80% Efficiency</span>
            </div>
            <div class="glass-card p-5 rounded-2xl shadow-xl">
                <div class="flex justify-between items-center text-gray-400 mb-2">
                    <span class="text-sm font-medium">Cloud Nodes</span>
                    <i class="fa-solid fa-server text-purple-400"></i>
                </div>
                <h3 class="text-2xl font-bold text-white">99.98%</h3>
                <span class="text-xs text-purple-400 font-semibold mt-1 inline-block">Zero Latency</span>
            </div>
            <div class="glass-card p-5 rounded-2xl shadow-xl">
                <div class="flex justify-between items-center text-gray-400 mb-2">
                    <span class="text-sm font-medium">Security Level</span>
                    <i class="fa-solid fa-shield-halved text-amber-400"></i>
                </div>
                <h3 class="text-2xl font-bold text-white">Maximum</h3>
                <span class="text-xs text-amber-400 font-semibold mt-1 inline-block">Protected by AI</span>
            </div>
        </div>

        <!-- Interactive Section -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 glass-card p-6 rounded-2xl shadow-xl flex flex-col justify-between">
                <div>
                    <h2 class="text-lg font-bold text-white mb-2">Performance Analytics</h2>
                    <p class="text-sm text-gray-400 mb-6">Real-time telemetry and resource usage tracking across clusters.</p>
                </div>
                <div class="h-64 flex items-center justify-center border border-dashed border-gray-800 rounded-xl bg-gray-900/40">
                    <div class="text-center space-y-2">
                        <i class="fa-solid fa-chart-line text-4xl text-blue-500 animate-bounce"></i>
                        <p class="text-sm text-gray-400">Telemetry Stream Connected & Active</p>
                    </div>
                </div>
            </div>

            <!-- Quick Actions Panel -->
            <div class="glass-card p-6 rounded-2xl shadow-xl space-y-4">
                <h2 class="text-lg font-bold text-white">Quick Control</h2>
                <p class="text-sm text-gray-400">Execute instant infrastructure commands.</p>
                <div class="space-y-3 pt-2">
                    <button onclick="triggerAction('Cluster Sync initiated...')" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-xl transition duration-200 shadow-lg shadow-blue-600/20 text-sm flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-rotate"></i> <span>Sync Clusters</span>
                    </button>
                    <button onclick="triggerAction('Security audit completed successfully.')" class="w-full bg-gray-800 hover:bg-gray-700 text-gray-200 font-semibold py-3 px-4 rounded-xl transition duration-200 border border-gray-700 text-sm flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-shield"></i> <span>Run Security Audit</span>
                    </button>
                </div>
                <div id="action-status" class="text-xs text-emerald-400 font-medium text-center pt-2 h-6"></div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-4 text-center text-xs text-gray-500">
        &copy; 2026 NexusAI Systems Inc. All rights reserved. Powered by Render Cloud.
    </footer>

    <script>
        function triggerAction(message) {
            const statusEl = document.getElementById('action-status');
            statusEl.innerText = message;
            setTimeout(() => {
                statusEl.innerText = '';
            }, 3000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
