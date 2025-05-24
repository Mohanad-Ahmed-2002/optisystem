from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # تم نقلها للأعلى لتكون الـ home page الافتراضية

    # الفواتير
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('add-invoice/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:invoice_id>/update_payment/', views.update_invoice_payment, name='update_invoice_payment'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),

    # المنتجات
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),


    # المصاريف
    path('add-expenses/', views.add_expense, name='add_expense'),
    path('expenses-list/', views.expenses_list, name='expenses_list'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),


    # التقارير
    path('sales-report/', views.sales_report, name='sales_report'),
    path('months/', views.manage_months, name='manage_months'),
    path('months/toggle/<int:month_id>/', views.toggle_month_status, name='toggle_month_status'),
    path('months/<int:session_id>/report/', views.monthly_report, name='monthly_report'),


]