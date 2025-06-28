import pytest
from accounts.models import CustomUser, SubscriptionPlan, UserSubscription
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
def test_subscription_plan_str():
    plan = SubscriptionPlan.objects.create(name="Monthly", price=100.0, duration_days=30)
    assert str(plan) == "Monthly - 100.0 جنيه / 30 يوم"

@pytest.mark.django_db
def test_custom_user_creation():
    user = CustomUser.objects.create_user(username="testuser", password="12345", role="manager")
    assert user.username == "testuser"
    assert user.is_manager()

@pytest.mark.django_db
def test_user_subscription_active():
    user = CustomUser.objects.create_user(username="activeuser", password="12345")
    plan = SubscriptionPlan.objects.create(name="Trial", price=0, duration_days=1)
    sub = UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=1)
    )
    assert sub.is_active()
