
import pytest
from django.urls import reverse
from decimal import Decimal
from core.models import Invoice, InvoiceItem, Product, Customer, MonthlySession
from django.utils.timezone import now

@pytest.mark.django_db
def test_invoice_list_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer = Customer.objects.create(name="عميل", shop=shop)
    Invoice.objects.create(shop=shop, customer=customer, total=100, amount_paid=100, payment_method='نقدًا')

    response = client.get(reverse('invoice_list'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'عميل' in content

@pytest.mark.django_db
def test_add_invoice_success(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer = Customer.objects.create(name="عميل", shop=shop)
    product = Product.objects.create(name="نظارة", category='نظارة طبية', shop=shop,
                                     buy_price=50, sell_price=100, quantity=10)
    month_start = now().date().replace(day=1)
    MonthlySession.objects.create(shop=shop, month=month_start, status='open')

    response = client.post(reverse('add_invoice'), data={
        'customer': customer.id,
        'payment_method': 'نقدًا',
        'discount': '10',
        'amount_paid': '90',
        'product_ids': [str(product.id)],
        'quantities': ['1']
    }, follow=True)

    print(response.content.decode())

    assert response.status_code == 200
    assert Invoice.objects.count() == 1
    invoice = Invoice.objects.first()
    assert invoice.total == Decimal('90.00')
    assert invoice.amount_paid == Decimal('90.00')
    assert InvoiceItem.objects.count() == 1

@pytest.mark.django_db
def test_invoice_detail_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    customer = Customer.objects.create(name="تفاصيل عميل", shop=shop)
    invoice = Invoice.objects.create(shop=shop, customer=customer, total=100, amount_paid=100,
                                     payment_method='نقدًا')

    response = client.get(reverse('invoice_detail', args=[invoice.id]))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'تفاصيل عميل' in content
