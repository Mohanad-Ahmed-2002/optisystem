from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test
from ..models import MonthlySession, Invoice, Expense
from ..utils import is_manager,block_superuser

@block_superuser
@user_passes_test(is_manager)
def manage_months(request):
    user_shop = request.user.shop  # ✅ المحل الخاص بالمستخدم
    months = MonthlySession.objects.filter(shop=user_shop).order_by('-month')
    return render(request, 'manage_months.html', {'months': months})

@block_superuser
@user_passes_test(is_manager)
def toggle_month_status(request, month_id):
    user_shop = request.user.shop
    session = get_object_or_404(MonthlySession, id=month_id, shop=user_shop)  # 🔐 الحماية من تعديل شهر لا يخص المستخدم

    if session.status == 'open':
        session.status = 'closed'

        # ✅ فلترة حسب المحل
        invoices = Invoice.objects.filter(monthly_session=session, shop=user_shop)
        expenses = Expense.objects.filter(monthly_session=session, shop=user_shop)
        total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        profit = total_sales - total_expenses

        next_session = MonthlySession.objects.filter(id__gt=session.id, status='open', shop=user_shop).order_by('id').first()

        if next_session:
            next_session.previous_profit += profit
            next_session.save()
            messages.success(request, f"✅ تم ترحيل ربح {profit} إلى شهر {next_session.month.strftime('%B %Y')}")
        else:
            messages.warning(request, "⚠️ تم إغلاق الشهر، لكن لم يتم العثور على شهر مفتوح لترحيل الربح إليه.")
    else:
        session.status = 'open'
        messages.info(request, "✅ تم فتح الشهر بنجاح.")

    session.save()
    return redirect('manage_months')


@block_superuser
@user_passes_test(is_manager)
def monthly_report(request, session_id):
    user_shop = request.user.shop
    session = get_object_or_404(MonthlySession, id=session_id, shop=user_shop)

    invoices = Invoice.objects.filter(monthly_session=session, shop=user_shop)
    expenses = Expense.objects.filter(monthly_session=session, shop=user_shop)

    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_sales - total_expenses
    total_with_previous = profit + session.previous_profit

    context = {
        'session': session,
        'invoices': invoices,
        'expenses': expenses,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'profit': profit,
        'total_with_previous': total_with_previous,
    }

    return render(request, 'monthly_report.html', context)
