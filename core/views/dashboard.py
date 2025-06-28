from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import localdate
from decimal import Decimal
from ..models import Invoice, Expense,InvoicePayment
from ..utils import is_manager_or_employee,subscription_required,block_superuser
from django.contrib.auth.decorators import user_passes_test
from ..models import MonthlySession

@block_superuser
@subscription_required
@user_passes_test(is_manager_or_employee)
def dashboard(request):
    """
    يعرض لوحة التحكم مع ملخص للمبيعات والمصاريف الخاصة بالمحل الحالي.
    """
    shop_name = request.user.shop.name
    today = localdate()
    month_start = today.replace(day=1)
    user_shop = request.user.shop  # ✅ جلب المحل الخاص بالمستخدم

    # تصفية البيانات حسب المحل
    daily_sales = Invoice.objects.filter(date__date=today, shop=user_shop)
    monthly_sales = Invoice.objects.filter(date__date__gte=month_start, shop=user_shop)
    monthly_expenses_qs = Expense.objects.filter(date__gte=month_start, shop=user_shop)

    daily_total = daily_sales.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    monthly_total = monthly_sales.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    monthly_paid = InvoicePayment.objects.filter(
        invoice__in=monthly_sales
    ).aggregate(paid=Sum('amount'))['paid'] or Decimal('0.00')
    monthly_expenses = monthly_expenses_qs.aggregate(amount=Sum('amount'))['amount'] or Decimal('0.00')

    # جلب الشهر المالي الحالي الخاص بالمحل
    session = MonthlySession.objects.filter(status='open', shop=user_shop).order_by('-month').first()
    previous_profit = session.previous_profit if session else Decimal('0.00')

    cash_flow_total = monthly_paid + previous_profit - monthly_expenses
    monthly_profit = monthly_total - monthly_expenses

    context = {
        'shop_name': shop_name,
        'daily_total': daily_total,
        'daily_count': daily_sales.count(),
        'monthly_total': monthly_total,
        'monthly_count': monthly_sales.count(),
        'latest_invoices': monthly_sales.select_related('customer').order_by('-date')[:5],  # ✅ أحدث فواتير المحل فقط
        'monthly_expenses': monthly_expenses,
        'monthly_paid': monthly_paid,
        'monthly_profit': monthly_profit,
        'previous_profit': previous_profit,
        'cash_flow_total': cash_flow_total,
    }
    return render(request, 'dashboard.html', context)
