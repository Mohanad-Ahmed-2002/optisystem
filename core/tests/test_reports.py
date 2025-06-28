
import pytest
from django.urls import reverse
from core.models import Invoice, Customer, MonthlySession
from django.utils.timezone import now

@pytest.mark.django_db
def test_sales_report_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer = Customer.objects.create(name='عميل التقرير', shop=shop)
    session = MonthlySession.objects.create(shop=shop, month=now().date().replace(day=1))
    Invoice.objects.create(shop=shop, customer=customer, total=200, amount_paid=200,
                           payment_method='نقدًا', monthly_session=session)

    response = client.get(reverse('sales_report'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'عميل التقرير' in content

@pytest.mark.django_db
def test_sales_report_filter_by_customer(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer_1 = Customer.objects.create(name='العميل 1', shop=shop)
    customer_2 = Customer.objects.create(name='العميل 2', shop=shop)
    session = MonthlySession.objects.create(shop=shop, month=now().date().replace(day=1))

    Invoice.objects.create(shop=shop, customer=customer_1, total=100, amount_paid=100, payment_method='نقدًا', monthly_session=session)
    Invoice.objects.create(shop=shop, customer=customer_2, total=200, amount_paid=200, payment_method='نقدًا', monthly_session=session)

    response = client.get(reverse('sales_report'), data={'customer': customer_2.id})
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'العميل 2' in content
    assert content.count('العميل 2') >= 1

@pytest.mark.django_db
def test_sales_report_print_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer = Customer.objects.create(name='مطبوع', shop=shop)
    session = MonthlySession.objects.create(shop=shop, month=now().date().replace(day=1))
    Invoice.objects.create(shop=shop, customer=customer, total=300, amount_paid=300,
                           payment_method='نقدًا', monthly_session=session)

    response = client.get(reverse('sales_report_print'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'مطبوع' in content
