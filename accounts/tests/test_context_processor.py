
import pytest
from accounts.models import CustomUser, SubscriptionPlan, UserSubscription
from accounts.context_processors import subscription_alert
from core.models import Shop
from django.test.client import RequestFactory
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
def test_subscription_alert_days_left():
    user = CustomUser.objects.create_user(username="test", password="123", role="employee")
    manager = CustomUser.objects.create_user(username="manager", password="123", role="manager")
    plan = SubscriptionPlan.objects.create(name="plan", price=100, duration_days=30)
    shop = Shop.objects.create(name="Test Shop", owner=manager)
    user.shop = shop
    user.save()

    UserSubscription.objects.create(
        user=manager,
        plan=plan,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=1)  # يوم واحد متبقي
    )

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    context = subscription_alert(request)
    assert "subscription_days_left" in context
    assert context["subscription_days_left"] == 1
