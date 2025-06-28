from django.contrib import admin
from .models import Customer, Product, MonthlySession, Invoice, InvoiceItem, InvoicePayment, Expense

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(MonthlySession)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(InvoicePayment)
admin.site.register(Expense)
