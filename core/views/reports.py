from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now
from decimal import Decimal

from ..models import Invoice
from ..forms import SalesReportForm
from ..utils import is_manager, is_manager_or_employee, render_to_pdf,block_superuser

@block_superuser
@user_passes_test(is_manager)
def sales_report(request):
    user_shop = request.user.shop
    form = SalesReportForm(request.GET or None)
    
    invoices = Invoice.objects.select_related('customer').filter(shop=user_shop).order_by('-created_at')

    if form.is_valid():
        customer = form.cleaned_data.get('customer')
        product = form.cleaned_data.get('product')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if customer:
            invoices = invoices.filter(customer=customer)
        if product:
            invoices = invoices.filter(items__product=product).distinct()
        if date_from:
            invoices = invoices.filter(created_at__date__gte=date_from)
        if date_to:
            invoices = invoices.filter(created_at__date__lte=date_to)

    total = invoices.aggregate(total_sum=Sum('total'))['total_sum'] or Decimal('0.00')

    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'sales_report.html', {
        'form': form,
        'invoices': invoices,
        'total': total,
    })

@block_superuser
@user_passes_test(is_manager_or_employee)
def sales_report_print(request):
    user_shop = request.user.shop
    form = SalesReportForm(request.GET or None)
    
    invoices = Invoice.objects.select_related('customer').filter(shop=user_shop).order_by('-created_at')

    if form.is_valid():
        customer = form.cleaned_data.get('customer')
        product = form.cleaned_data.get('product')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if customer:
            invoices = invoices.filter(customer=customer)
        if product:
            invoices = invoices.filter(items__product=product).distinct()
        if date_from:
            invoices = invoices.filter(created_at__date__gte=date_from)
        if date_to:
            invoices = invoices.filter(created_at__date__lte=date_to)

    total = invoices.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')

    return render(request, 'sales_report_print.html', {
        'invoices': invoices,
        'total': total,
        'now': now(),
    })

@block_superuser
@user_passes_test(is_manager_or_employee)
def invoice_pdf(request, invoice_id):
    user_shop = request.user.shop
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer'),
        id=invoice_id,
        shop=user_shop  # 🔒 حماية الوصول
    )
    items = invoice.items.select_related('product', 'lens')  # ✅ دعم العدسات لو احتجتها في الطباعة

    context = {
        'invoice': invoice,
        'items': items
    }
    return render_to_pdf('invoice_pdf_template.html', context)
