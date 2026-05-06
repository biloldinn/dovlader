@echo off
:loop
echo Bot ishga tushmoqda...
.\venv\Scripts\python.exe media_bot/main.py
echo Bot xatolik tufayli to'xtadi. 5 soniyadan so'ng qayta ishga tushadi...
timeout /t 5
goto loop
