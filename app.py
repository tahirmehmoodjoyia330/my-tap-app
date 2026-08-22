from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Tap to Earn Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { user-select: none; -webkit-user-select: none; background-color: #0b0e14; color: white; font-family: sans-serif; }
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
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body class="flex flex-col h-screen justify-between overflow-hidden">

    <!-- Top Header -->
    <div class="px-5 pt-4 flex justify-between items-center bg-gray-900/50 pb-3 border-b border-gray-800">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/40">
                <i class="fa-solid fa-user-ninja text-amber-400"></i>
            </div>
            <div>
                <h2 class="text-sm font-bold text-gray-200">PRO GAMER</h2>
                <p class="text-xs text-amber-400 font-semibold">Level 1 / 30</p>
            </div>
        </div>
        <div class="bg-gray-800/80 px-3 py-1.5 rounded-full border border-gray-700 flex items-center space-x-2">
            <i class="fa-solid fa-coins text-amber-400 text-sm"></i>
            <span id="top-balance" class="font-bold text-sm">0</span>
        </div>
    </div>

    <!-- MAIN TAB: TAP GAME -->
    <div id="tab-tap" class="tab-content active flex-1 flex flex-col items-center justify-between p-5">
        <div class="text-center mt-2">
            <p class="text-xs text-gray-400 uppercase tracking-widest font-semibold mb-1">TOTAL BALANCE</p>
            <div class="flex items-center justify-center space-x-3">
                <i class="fa-solid fa-coins text-4xl text-amber-400"></i>
                <span id="balance" class="text-5xl font-black tracking-tight">0</span>
            </div>
        </div>

        <div id="tap-zone" class="tap-btn relative w-64 h-64 rounded-full bg-gradient-to-b from-amber-400 to-amber-600 p-3 shadow-[0_0_50px_rgba(245,158,11,0.3)] cursor-pointer my-auto flex items-center justify-center border-4 border-amber-300">
            <div class="w-full h-full rounded-full bg-gray-950 flex items-center justify-center border-2 border-amber-500/50">
                <i class="fa-solid fa-paw text-7xl text-amber-400 drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]"></i>
            </div>
        </div>

        <div class="w-full max-w-xs mb-2">
            <div class="flex justify-between text-xs font-bold text-gray-400 mb-1">
                <span class="flex items-center gap-1"><i class="fa-solid fa-bolt text-amber-400"></i> Energy</span>
                <div><span id="energy">500</span> / <span id="max-energy">500</span></div>
            </div>
            <div class="w-full bg-gray-800 h-3 rounded-full overflow-hidden border border-gray-700">
                <div id="energy-bar" class="bg-gradient-to-r from-amber-500 to-yellow-300 h-full w-full transition-all duration-100"></div>
            </div>
        </div>
    </div>

    <!-- TAB: BOOSTS -->
    <div id="tab-boost" class="tab-content flex-1 p-5 overfl
