
import pytest
from django.urls import reverse
from accounts.models import CustomUser
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_superuser_can_activate_user(client):
    superuser = CustomUser.objects.create_superuser(username='admin', password='123')
    target = CustomUser.objects.create_user(username='target', password='123', is_active=False, is_approved=False)
    client.login(username='admin', password='123')
    response = client.get(reverse('activate_user', kwargs={'user_id': target.id}))
    target.refresh_from_db()
    assert response.status_code == 302
    assert target.is_active and target.is_approved

@pytest.mark.django_db
def test_superuser_can_deactivate_user(client):
    superuser = CustomUser.objects.create_superuser(username='admin2', password='123')
    target = CustomUser.objects.create_user(username='target2', password='123', is_active=True)
    client.login(username='admin2', password='123')
    response = client.get(reverse('deactivate_user', kwargs={'user_id': target2.id}))
    target.refresh_from_db()
    assert response.status_code == 302
    assert not target.is_active

@pytest.mark.django_db
def test_superuser_can_delete_user(client):
    superuser = CustomUser.objects.create_superuser(username='admin3', password='123')
    target = CustomUser.objects.create_user(username='target3', password='123')
    client.login(username='admin3', password='123')
    response = client.get(reverse('superuser_delete_user', kwargs={'user_id': target.id}))
    assert response.status_code == 302
    assert not CustomUser.objects.filter(id=target.id).exists()
