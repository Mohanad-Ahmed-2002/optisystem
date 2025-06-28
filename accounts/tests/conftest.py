import os
import django
import pytest

# تحديد إعدادات Django الخاصة بمشروعك
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica.settings')

# تهيئة بيئة Django قبل أي اختبار
django.setup()
