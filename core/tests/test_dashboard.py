import pytest
from django.urls import reverse
from django.utils.timezone import localdate, now
from core.models import Invoice, Expense, MonthlySession, InvoicePayment
from accounts.models import SubscriptionPlan, UserSubscription
from decimal import Decimal
from datetime import timedelta

@pytest.mark.django_db
def test_dashboard_view(client, create_user_with_shop, authenticated_client):
    user, shop = create_user_with_shop
    client = authenticated_client(user)

    # إضافة خطة اشتراك وتفعيل الاشتراك للمستخدم
    plan = SubscriptionPlan.objects.create(name="monthly", price=100, duration_days=30)
    UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=now().date(),
        end_date=now().date() + timedelta(days=plan.duration_days)
    )

    # إعداد بيانات وهمية
    session = MonthlySession.objects.create(
        shop=shop,
        month=localdate().replace(day=1),
        status='open',
        previous_profit=Decimal('200.00')
    )

    invoice = Invoice.objects.create(
        shop=shop,
        total=1000,
        payment_method='نقدًا',
        sale_type='قطاعي',
        monthly_session=session
    )

    InvoicePayment.objects.create(
        invoice=invoice,
        amount=800
    )

    Expense.objects.create(
        shop=shop,
        amount=100,
        category='rent',
        title='إيجار',
        monthly_session=session
    )

    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200
    assert 'monthly_total' in response.context
    assert response.context['monthly_total'] == Decimal('1000.00')
