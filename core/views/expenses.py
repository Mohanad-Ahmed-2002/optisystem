from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.db import IntegrityError

from ..models import Expense, MonthlySession
from ..forms import ExpenseForm
from ..utils import is_manager_or_employee, is_manager,block_superuser

@block_superuser
@user_passes_test(is_manager_or_employee)
@login_required
def add_expense(request):
    month_start = now().date().replace(day=1)

    # ✅ حماية من IntegrityError
    try:
        session, _ = MonthlySession.objects.get_or_create(
            month=month_start,
            shop=request.user.shop,
            defaults={'status': 'open'}
        )
    except IntegrityError:
        session = MonthlySession.objects.get(month=month_start, shop=request.user.shop)

    # ✅ حماية من الشهر المغلق
    if session.status == 'closed':
        messages.error(request, "لا يمكن إضافة مصروفات لأن هذا الشهر مغلق.")
        return redirect('expenses_list')

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.monthly_session = session
            expense.shop = request.user.shop
            expense.save()
            messages.success(request, 'تم تسجيل المصروف بنجاح.')
            return redirect('expenses_list')
        else:
            messages.error(request, 'الرجاء تصحيح الأخطاء في النموذج.')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})

@block_superuser
@user_passes_test(is_manager)
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, shop=request.user.shop)  # 🔒 حماية
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "تم حذف المصروف بنجاح.")
    return redirect('expenses_list')

@block_superuser
@user_passes_test(is_manager_or_employee)
def expenses_list(request):
    search_query = request.GET.get('search', '')

    # 🧠 الأساس: استعلام واحد فقط
    expenses_qs = Expense.objects.filter(shop=request.user.shop).order_by('-date')

    if search_query:
        expenses_qs = expenses_qs.filter(title__icontains=search_query)

    # 🔢 الإجمالي
    total_expenses = expenses_qs.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # 📄 التقسيم
    paginator = Paginator(expenses_qs, 10)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)

    return render(request, 'expenses_list.html', {
        'expenses': expenses_page,
        'total_expenses': total_expenses,
        'search_query': search_query
    })
