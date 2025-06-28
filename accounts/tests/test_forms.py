from accounts.forms import LoginForm, CustomUserCreationForm, CreateEmployeeForm

def test_login_form_valid_data():
    form = LoginForm(data={"username": "user", "password": "secret"})
    assert form.is_valid()

def test_custom_user_creation_form_fields():
    form = CustomUserCreationForm()
    assert "username" in form.fields
    assert "email" in form.fields
    assert "password1" in form.fields
    assert "password2" in form.fields
