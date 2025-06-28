from django.urls import path
from . import views
from .views import lens,customers

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
    path('invoices/<int:invoice_id>/add-payment/', views.add_payment, name='add_payment'),
    path('payments/<int:payment_id>/delete/', views.delete_payment, name='delete_payment'),
    


    # العملاء
    path('customers/', customers.customer_list, name='customer_list'),
    path('customers/<int:pk>/', customers.customer_detail, name='customer_detail'),


    # المنتجات
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('lenses/', lens.lens_list, name='lens_list'),
    path('lenses/add/', lens.add_lens, name='add_lens'),
    path('lenses/edit/<int:lens_id>/', lens.edit_lens, name='edit_lens'),
    path('lenses/delete/<int:lens_id>/', lens.delete_lens, name='delete_lens'),


    # المصاريف
    path('add-expenses/', views.add_expense, name='add_expense'),
    path('expenses-list/', views.expenses_list, name='expenses_list'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),


    # التقارير
    path('sales-report/', views.sales_report, name='sales_report'),
    path('months/', views.manage_months, name='manage_months'),
    path('months/toggle/<int:month_id>/', views.toggle_month_status, name='toggle_month_status'),
    path('months/<int:session_id>/report/', views.monthly_report, name='monthly_report'),
    path('reports/sales/print/', views.sales_report_print, name='sales_report_print'),




]