import pytest
from django.urls import reverse
from django.utils.timezone import localdate
from core.models import Invoice, Expense, MonthlySession
from decimal import Decimal

@pytest.mark.django_db
def test_dashboard_view(client, create_user_with_shop, authenticated_client):
    user, shop = create_user_with_shop
    client = authenticated_client(user)

    # إعداد بيانات وهمية
    session = MonthlySession.objects.create(shop=shop, month=localdate().replace(day=1), status='open', previous_profit=Decimal('200.00'))

    Invoice.objects.create(shop=shop, total=1000, amount_paid=800, monthly_session=session)
    Expense.objects.create(shop=shop, amount=100, category='rent', title='إيجار', monthly_session=session)

    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200
    assert 'monthly_total' in response.context
    assert response.context['monthly_total'] == Decimal('1000.00')
