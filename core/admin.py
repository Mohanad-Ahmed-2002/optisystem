from django.contrib import admin
from .models import Customer,Product,Invoice,InvoiceItem

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sell_price', 'quantity')
    list_filter = ('category',)
    search_fields = ('name', 'brand', 'barcode')


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'payment_method', 'total')
    list_filter = ('payment_method', 'date')
    search_fields = ('customer__name',)
    inlines = [InvoiceItemInline]

