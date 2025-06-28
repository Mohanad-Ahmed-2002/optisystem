
import pytest
from django.urls import reverse
from core.models import MonthlySession, Invoice, Expense
from django.utils.timezone import now

@pytest.mark.django_db
def test_manage_months_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    MonthlySession.objects.create(month=now().date().replace(day=1), shop=shop, status='open')

    response = client.get(reverse('manage_months'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'إدارة الشهور' in content or 'شهر' in content

@pytest.mark.django_db
def test_toggle_month_status_close(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    session = MonthlySession.objects.create(month=now().date().replace(day=1), shop=shop, status='open')
    Invoice.objects.create(shop=shop, monthly_session=session, total=100, amount_paid=100, payment_method='نقدًا')
    Expense.objects.create(shop=shop, monthly_session=session, title='إيجار', amount=30, category='rent')

    response = client.get(reverse('toggle_month_status', args=[session.id]), follow=True)
    session.refresh_from_db()

    assert response.status_code == 200
    assert session.status == 'closed'

@pytest.mark.django_db
def test_toggle_month_status_open(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    session = MonthlySession.objects.create(month=now().date().replace(day=1), shop=shop, status='closed')
    response = client.get(reverse('toggle_month_status', args=[session.id]), follow=True)
    session.refresh_from_db()

    assert response.status_code == 200
    assert session.status == 'open'

@pytest.mark.django_db
def test_monthly_report_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    session = MonthlySession.objects.create(month=now().date().replace(day=1), shop=shop, status='open')
    Invoice.objects.create(shop=shop, monthly_session=session, total=500, amount_paid=500, payment_method='نقدًا')
    Expense.objects.create(shop=shop, monthly_session=session, title='كهرباء', amount=100, category='electricity')

    response = client.get(reverse('monthly_report', args=[session.id]))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'التقارير' in content or 'المصروفات' in content
