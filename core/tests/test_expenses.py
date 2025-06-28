
import pytest
from django.urls import reverse
from core.models import Expense, MonthlySession
from django.utils.timezone import now
from decimal import Decimal

@pytest.mark.django_db
def test_add_expense_success(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    # الشهر الحالي مفتوح
    month_start = now().date().replace(day=1)
    session = MonthlySession.objects.create(month=month_start, shop=shop, status='open')

    response = client.post(reverse('add_expense'), data={
        'title': 'كهرباء',
        'amount': '150',
        'category': 'electricity',
        'notes': 'فاتورة شهرية'
    })

    assert response.status_code == 302
    assert Expense.objects.count() == 1
    expense = Expense.objects.first()
    assert expense.shop == shop
    assert expense.amount == Decimal('150.00')

@pytest.mark.django_db
def test_add_expense_closed_session(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    # شهر مغلق
    month_start = now().date().replace(day=1)
    MonthlySession.objects.create(month=month_start, shop=shop, status='closed')

    response = client.post(reverse('add_expense'), data={
        'title': 'إيجار',
        'amount': '500',
        'category': 'rent',
        'notes': 'شهر 6'
    }, follow=True)

    content = response.content.decode('utf-8')
    assert 'لا يمكن إضافة مصروفات لأن هذا الشهر مغلق.' in content
    assert Expense.objects.count() == 0

@pytest.mark.django_db
def test_expenses_list_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    Expense.objects.create(title='إيجار', amount=500, category='rent', shop=shop)
    Expense.objects.create(title='صيانة', amount=250, category='maintenance', shop=shop)

    response = client.get(reverse('expenses_list'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'إيجار' in content
    assert 'صيانة' in content
