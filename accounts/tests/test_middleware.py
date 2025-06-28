import pytest
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser, SubscriptionPlan, UserSubscription

@pytest.mark.django_db
def test_subscription_expired_redirect(client):
    user = CustomUser.objects.create_user(username='expired', password='1234')
    plan = SubscriptionPlan.objects.create(name='monthly', price=10, duration_days=30)
    UserSubscription.objects.create(user=user, plan=plan, end_date=timezone.now() - timezone.timedelta(days=1))
    
    client.login(username='expired', password='1234')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/choose-plan' in response.url
