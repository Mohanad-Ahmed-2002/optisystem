@echo off
REM انتقل إلى مجلد المشروع
cd /d "%~dp0optisystem\optica"

REM فعل البيئة الافتراضية
call ..\venv\Scripts\activate.bat

REM شغل السيرفر في نافذة مستقلة
start cmd /k "python manage.py runserver 127.0.0.1:8000"

REM افتح المتصفح (بعد ثواني)
timeout /t 2 >nul
start http://127.0.0.1:8000

pause
