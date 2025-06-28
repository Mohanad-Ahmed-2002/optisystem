from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import core.models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# Create your models here.

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_days = models.PositiveIntegerField(help_text="عدد أيام الاشتراك مثل 30 أو 90")

    def __str__(self):
        return f"{self.name} - {self.price} جنيه / {self.duration_days} يوم"

class UserSubscription(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def is_active(self):
        return timezone.now() <= self.end_date

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'مدير'),
        ('employee', 'موظف'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', verbose_name="الدور")
    shop = models.ForeignKey('core.Shop', on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name="تمت الموافقة؟")



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

