import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_login_view_get(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert "اسم المستخدم" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_add_employee_requires_login(client):
    response = client.get(reverse("add_employee"))
    assert response.status_code == 302  # Redirect to login
