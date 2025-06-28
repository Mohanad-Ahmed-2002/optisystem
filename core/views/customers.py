from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from ..utils import is_manager_or_employee, block_superuser
from django.shortcuts import render, get_object_or_404
from ..models import Customer, Invoice, InvoicePayment


@block_superuser
@user_passes_test(is_manager_or_employee)
def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.filter(shop=request.user.shop)

    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    return render(request, 'customer_list.html', {
        'customers': customers,
        'search_query': search_query
    })

@block_superuser
@user_passes_test(is_manager_or_employee)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, shop=request.user.shop)
    invoices = Invoice.objects.filter(customer=customer).order_by('-date')
    payments = InvoicePayment.objects.filter(invoice__customer=customer).order_by('-date')

    total_invoice = 0
    total_paid = 0
    total_remaining = 0

    for invoice in invoices:
        paid = sum(p.amount for p in InvoicePayment.objects.filter(invoice=invoice))
        remaining = invoice.total - paid

        invoice.paid = paid
        invoice.remaining = remaining

        total_invoice += invoice.total
        total_paid += paid
        total_remaining += remaining

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'payments': payments,
        'total_invoice': total_invoice,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
    })




