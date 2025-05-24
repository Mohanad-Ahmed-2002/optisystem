from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'مدير'),
        ('employee', 'موظف'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', verbose_name="الدور")

    # إضافة related_name لتجنب التعارض
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set", # تغيير هنا
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="customuser_set", # تغيير هنا
        related_query_name="customuser",
    )


    def is_manager(self):
        return self.role == 'manager'

    def is_employee(self):
        return self.role == 'employee'

    def __str__(self):
        return self.username # أو self.get_full_name()

    class Meta:
        verbose_name = "المستخدم"
        verbose_name_plural = "المستخدمون"

