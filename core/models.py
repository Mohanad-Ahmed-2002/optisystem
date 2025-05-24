
from django.db import models
from django.utils import timezone
from decimal import Decimal

# Create your models here.
class Customer(models.Model):

    name=models.CharField(max_length=100, verbose_name="الاســـم")
    phone=models.CharField(max_length=20,verbose_name="رقم الهـاتف", blank=True, null=True)
    address=models.CharField(max_length=200,verbose_name="العنـــوان", blank=True, null=True)
    notes=models.TextField(verbose_name="ملاحظــات", blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:

        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('نظارة طبية', 'نظارة طبية'),
        ('نظارة شمسية', 'نظارة شمسية'),
        ('عدسات', 'عدسات'),
        ('إكسسوارات', 'إكسسوارات'),
    ]

    name=models.CharField(max_length=100,verbose_name="اســم المنتج")
    category=models.CharField(max_length=20,verbose_name="الفـئة",choices=CATEGORY_CHOICES)
    brand=models.CharField(max_length=50,verbose_name="العلامة التجارية",blank=True, null=True)
    buy_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="سعر الشراء")
    sell_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="سعر البيع")
    quantity = models.PositiveIntegerField(verbose_name="الكمية في المخزن")
    barcode = models.CharField(max_length=50, verbose_name="الباركود", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

class MonthlySession(models.Model):
    month = models.DateField(unique=True, verbose_name="بداية الشهر")
    status = models.CharField(
        max_length=20,
        choices=[('open', 'مفتوح'), ('closed', 'مغلق')],
        default='open'
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.month.strftime("%B %Y") + (" - مغلق" if self.status == 'closed' else "")

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('نقدًا', 'نقدًا'),
        ('فيزا', 'فيزا'),
        ('آجل', 'آجل'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="العميل")
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفاتورة")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="طريقة الدفع")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المدفوع")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الخصم",null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الإجمالي", default=0)
    monthly_session = models.ForeignKey(MonthlySession, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_amount(self):
        return max(self.total - self.amount_paid, Decimal('0.00'))

    def __str__(self):
        return f"فاتورة رقم {self.id}"

    class Meta:
        verbose_name = "فاتورة"
        verbose_name_plural = "الفواتير"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items", verbose_name="الفاتورة")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="المنتج")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    class Meta:
        verbose_name = "عنصر فاتورة"
        verbose_name_plural = "عناصر الفواتير"

class Expense(models.Model):
    
    CATEGORY_CHOICES = [
        ('rent', 'إيجار'),
        ('salary', 'رواتب'),
        ('credit', 'سلفة'),
        ('purchases', 'مشتريات'),
        ('maintenance', 'صيانة'),
        ('electricity', 'كهرباء'),
        ('other', 'أخرى'),
    ]

    title = models.CharField(max_length=200, verbose_name="اسم المصروف")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="الفئة")
    monthly_session = models.ForeignKey(MonthlySession, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True, verbose_name="التاريخ")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.title} - {self.amount}"

