
import pytest
from django.urls import reverse
from core.models import Lens

@pytest.mark.django_db
def test_add_lens_success(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    response = client.post(reverse('add_lens'), data={
        'name': 'عدسة زجاجية',
        'company': 'LensCo',
        'buy_price': '40.00',
        'sell_price': '80.00'
    })

    assert response.status_code == 302
    assert Lens.objects.count() == 1
    lens = Lens.objects.first()
    assert lens.name == 'عدسة زجاجية'
    assert lens.shop == shop

@pytest.mark.django_db
def test_lens_list_view(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    Lens.objects.create(name='عدسة A', company='CoA', buy_price=30, sell_price=60, shop=shop)
    Lens.objects.create(name='عدسة B', company='CoB', buy_price=50, sell_price=100, shop=shop)

    response = client.get(reverse('lens_list'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'عدسة A' in content
    assert 'عدسة B' in content

@pytest.mark.django_db
def test_edit_lens(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    lens = Lens.objects.create(name='LensX', company='OldCo', buy_price=20, sell_price=45, shop=shop)
    response = client.post(reverse('edit_lens', args=[lens.id]), data={
        'name': 'LensX Updated',
        'company': 'NewCo',
        'buy_price': '25',
        'sell_price': '55'
    })

    lens.refresh_from_db()
    assert lens.name == 'LensX Updated'
    assert lens.company == 'NewCo'
    assert lens.sell_price == 55

@pytest.mark.django_db
def test_delete_lens(authenticated_client, create_user_with_shop):
    user, shop = create_user_with_shop
    client = authenticated_client()

    lens = Lens.objects.create(name='ToDelete', company='X', buy_price=10, sell_price=20, shop=shop)
    response = client.post(reverse('delete_lens', args=[lens.id]), follow=True)

    assert Lens.objects.count() == 0
