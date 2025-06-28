import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import SubscriptionPlan, UserSubscription
from django.utils import timezone
from django.test import RequestFactory
from accounts.middleware import SubscriptionMiddleware
from datetime import timedelta

User = get_user_model()

# -------------------------------
# Login view tests
# -------------------------------

@pytest.mark.django_db
def test_login_valid_credentials(client, django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    response = client.post(reverse("login"), {"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # redirect to dashboard

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    response = client.post(reverse("login"), {"username": "wrong", "password": "wrong"})
    assert "اسم المستخدم أو كلمة المرور غير صحيحة" in response.content.decode("utf-8")

# -------------------------------
# Signup with plan tests
# -------------------------------

@pytest.mark.django_db
def test_signup_with_valid_plan(client):
    plan = SubscriptionPlan.objects.create(name="monthly", price=100, duration_days=30)
    session = client.session
    session['selected_plan'] = 'monthly'
    session.save()

    response = client.post(
        reverse("signup_with_plan", kwargs={"plan_id": plan.id}),
        {
            "username": "newuser",
            "email": "new@ex.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123"
        }
    )
    assert response.status_code == 302
    assert UserSubscription.objects.filter(user__username="newuser").exists()

# -------------------------------
# Middleware tests
# -------------------------------

@pytest.mark.django_db
def test_middleware_expired_subscription():
    factory = RequestFactory()
    user = User.objects.create_user(username="expired", password="123")
    plan = SubscriptionPlan.objects.create(name="Expired Plan", price=0, duration_days=1)
    UserSubscription.objects.create(user=user, plan=plan, end_date=timezone.now() - timedelta(days=1))

    request = factory.get("/dashboard/")
    request.user = user

    middleware = SubscriptionMiddleware(lambda r: r)
    response = middleware(request)

    assert response.status_code == 302
    assert response.url == reverse("choose_plan")

# -------------------------------
# Additional views and middleware edge cases
# -------------------------------

@pytest.mark.django_db
def test_choose_plan_invalid_post(client):
    response = client.post(reverse("choose_plan"), {"plan": "invalid"})
    assert response.status_code == 200
    assert "يرجى اختيار خطة صحيحة" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_signup_with_plan_invalid_form(client):
    plan = SubscriptionPlan.objects.create(name="monthly", price=100, duration_days=30)
    response = client.post(
        reverse("signup_with_plan", kwargs={"plan_id": plan.id}),
        {
            "username": "baduser",
            "email": "bad@ex.com",
            "password1": "StrongPass123",
            "password2": "Mismatch123"
        }
    )
    assert response.status_code == 200
    assert "هذا الحقل مطلوب." in response.content.decode("utf-8") or "غير متطابق" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_login_view_invalid_form(client):
    response = client.post(reverse("login"), {})  # no data
    assert response.status_code == 200
    assert "اسم المستخدم" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_middleware_no_subscription():
    factory = RequestFactory()
    user = User.objects.create_user(username="nosub", password="123")

    request = factory.get("/dashboard/")
    request.user = user

    middleware = SubscriptionMiddleware(lambda r: r)
    response = middleware(request)

    assert response.status_code == 302
    assert response.url == reverse("choose_plan")
