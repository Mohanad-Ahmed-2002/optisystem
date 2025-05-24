# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateEmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'role'] # تأكد من 'role' إذا كان موجودًا في CustomUser
        labels = {
            'username': 'اسم المستخدم',
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'role': 'الدور',
        }
        help_texts = {
            'username': 'مطلوب. 150 رمزًا أو أقل، مكونة من حروف وأرقام و @/./+/-/_ فقط',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'password': forms.PasswordInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
            'role': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': 'اسم المستخدم'
        })
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': 'كلمة المرور'
        })
    )