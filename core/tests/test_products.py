
import pytest
from django.urls import reverse
from core.models import Product

@pytest.mark.django_db
def test_add_product_success(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    response = client.post(reverse('add_product'), data={
        'name': 'نظارة طبية',
        'category': 'نظارة طبية',
        'brand': 'Ray-Ban',
        'buy_price': '100',
        'sell_price': '150',
        'quantity': '5',
        'barcode': '1234567890'
    })

    assert response.status_code == 302
    assert Product.objects.count() == 1
    product = Product.objects.first()
    assert product.name == 'نظارة طبية'
    assert product.shop == shop

@pytest.mark.django_db
def test_product_list_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    Product.objects.create(name='نظارة شمسية', category='نظارة شمسية', shop=shop, buy_price=50, sell_price=100, quantity=3)
    Product.objects.create(name='إكسسوارات', category='إكسسوارات', shop=shop, buy_price=10, sell_price=20, quantity=10)

    response = client.get(reverse('product_list'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'نظارة شمسية' in content
    assert 'إكسسوارات' in content

@pytest.mark.django_db
def test_edit_product(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    product = Product.objects.create(name='منتج قديم', category='إكسسوارات', shop=shop, buy_price=20, sell_price=30, quantity=2)
    response = client.post(reverse('edit_product', args=[product.id]), data={
        'name': 'منتج محدث',
        'category': 'إكسسوارات',
        'brand': 'براند',
        'buy_price': '25',
        'sell_price': '35',
        'quantity': '3',
        'barcode': '000999'
    })

    product.refresh_from_db()
    assert product.name == 'منتج محدث'
    assert product.sell_price == 35

@pytest.mark.django_db
def test_delete_product(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    product = Product.objects.create(name='للحذف', category='نظارة طبية', shop=shop, buy_price=10, sell_price=20, quantity=1)
    response = client.post(reverse('delete_product', args=[product.id]), follow=True)

    assert Product.objects.count() == 0
