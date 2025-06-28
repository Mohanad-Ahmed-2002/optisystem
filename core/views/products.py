from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from ..models import Product
from ..forms import ProductForm
from ..utils import is_manager_or_employee, is_manager,block_superuser

@block_superuser
@user_passes_test(is_manager_or_employee)
def product_list(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.filter(shop=request.user.shop)

    if search_query:
        products = products.filter(Q(name__icontains=search_query) |
        Q(barcode__icontains=search_query))


    products = products.order_by('-id')
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'product_list.html', {
        'products': products_page,
        'search_query': search_query
    })

@block_superuser
@user_passes_test(is_manager_or_employee)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = request.user.shop  # ✅ ربط المنتج بالمحل
            product.save()
            messages.success(request, 'تم إضافة المنتج بنجاح.')
            return redirect('product_list')
        else:
            messages.error(request, 'الرجاء تصحيح الأخطاء في النموذج.')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@block_superuser
@user_passes_test(is_manager_or_employee)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop=request.user.shop)  # ✅ حماية الوصول

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

@block_superuser
@user_passes_test(is_manager)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop=request.user.shop)  # ✅ حماية الوصول

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'تم حذف المنتج.')
        return redirect('product_list')
    return render(request, 'confirm_delete_product.html', {'product': product})
