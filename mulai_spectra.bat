@echo off
title SPECTRA LAUNCHER

:: 1. Pindah ke folder project backend
cd /d "C:\Users\SKYMIT59\Aplikasi Spectra\SPECTRA_BACKEND"

:: 2. Buka Jendela CMD 1: Uvicorn Backend (Port 5005)
start "SPECTRA Backend (Uvicorn)" cmd /k ""C:\Users\SKYMIT59\Python311\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 5005 --reload"

:: Beri jeda 2 detik agar backend siap
timeout /t 2 /nobreak >nul

:: 3. Buka Jendela CMD 2: Cloudflare Tunnel (Port 5005)
start "SPECTRA Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:5005"

:: Tutup jendela pemanggil utama
exit