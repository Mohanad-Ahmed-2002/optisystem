from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.forms import LensForm
from core.models import Lens
from accounts.views import is_manager_or_employee
from django.contrib.auth.decorators import login_required, user_passes_test
from ..utils import is_manager_or_employee,block_superuser

@block_superuser
@login_required
@user_passes_test(is_manager_or_employee)
def add_lens(request):
    if request.method == 'POST':
        form = LensForm(request.POST)
        if form.is_valid():
            lens = form.save(commit=False)
            lens.shop = request.user.shop  # ✅ ربط العدسة بالمحل
            lens.save()
            messages.success(request, 'تمت إضافة العدسة بنجاح.')
            return redirect('lens_list')
        else:
            messages.error(request, 'الرجاء تصحيح الأخطاء في النموذج.')
    else:
        form = LensForm()
    return render(request, 'add_lens.html', {'form': form})

@block_superuser
@login_required
@user_passes_test(is_manager_or_employee)
def lens_list(request):
    lenses = Lens.objects.filter(shop=request.user.shop).order_by('-id')  # ✅ عدسات المحل فقط

    search_query = request.GET.get('search', '')
    if search_query:
        lenses = lenses.filter(name__icontains=search_query)

    paginator = Paginator(lenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lens_list.html', {'lenses': page_obj, 'search_query': search_query})

@block_superuser
@login_required
@user_passes_test(is_manager_or_employee)
def edit_lens(request, lens_id):
    lens = get_object_or_404(Lens, id=lens_id, shop=request.user.shop)  # 🔒 منع التلاعب

    if request.method == 'POST':
        form = LensForm(request.POST, instance=lens)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات العدسة بنجاح.')
            return redirect('lens_list')
    else:
        form = LensForm(instance=lens)
    return render(request, 'add_lens.html', {'form': form, 'edit_mode': True})

@block_superuser
@login_required
@user_passes_test(is_manager_or_employee)
def delete_lens(request, lens_id):
    lens = get_object_or_404(Lens, id=lens_id, shop=request.user.shop)  # 🔒 حماية الوصول

    if request.method == 'POST':
        lens.delete()
        messages.success(request, 'تم حذف العدسة بنجاح.')
        return redirect('lens_list')
    return render(request, 'confirm_delete_lens.html', {'lens': lens})
