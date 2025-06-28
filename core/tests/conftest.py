import pytest
from django.contrib.auth import get_user_model
from core.models import Shop
from accounts.models import UserSubscription, SubscriptionPlan
from datetime import timedelta
from django.utils.timezone import now

User = get_user_model()

@pytest.fixture
def create_user_with_shop(db):
    # إنشاء خطة اشتراك
    plan = SubscriptionPlan.objects.create(name="monthly", price=100, duration_days=30)

    # إنشاء مستخدم ومدير
    user = User.objects.create_user(username='manager', password='test1234', role='manager')
    shop = Shop.objects.create(name='Test Shop', owner=user)
    user.shop = shop
    user.save()

    # إنشاء اشتراك نشط
    UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=now() - timedelta(days=1),
        end_date=now() + timedelta(days=30),
    )

    return user, shop

@pytest.fixture
def authenticated_client(client, create_user_with_shop):
    user, _ = create_user_with_shop
    client.login(username='manager', password='test1234')
    return lambda u=None: client
