
import pytest
from accounts.forms import CreateEmployeeForm

@pytest.mark.django_db
def test_create_employee_form_valid():
    form_data = {
        'username': 'emp1',
        'first_name': 'Ali',
        'last_name': 'Hassan',
        'password': 'secret123',
        'role': 'employee',
    }
    form = CreateEmployeeForm(data=form_data)
    assert form.is_valid(), form.errors

@pytest.mark.django_db
def test_create_employee_form_invalid_missing_fields():
    form_data = {
        'username': '',
        'first_name': '',
        'last_name': '',
        'password': '',
        'role': '',
    }
    form = CreateEmployeeForm(data=form_data)
    assert not form.is_valid()
