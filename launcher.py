import os
import time
import webbrowser

print("🟢 بدء تشغيل البرنامج...")

# فعل البيئة الافتراضية وشغّل السيرفر في نافذة مستقلة
os.system("start cmd /k \"call ..\\venv\\Scripts\\activate.bat && python manage.py runserver 127.0.0.1:8000\"")

# استنّى شويّة لحد السيرفر يشتغل
time.sleep(3)

# افتح المتصفح تلقائيًا
webbrowser.open("http://127.0.0.1:8000")
