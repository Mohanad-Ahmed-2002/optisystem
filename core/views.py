from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import localdate,now
from decimal import Decimal

# استيراد الـ Models
from .models import Customer, Product, Invoice, InvoiceItem, Expense,MonthlySession
from accounts.models import CustomUser

# استيراد الـ Forms
from .forms import SalesReportForm, ExpenseForm, ProductForm, CustomerForm # تم إضافة ProductForm و CustomerForm

# استيراد الدوال المساعدة
from .utils import is_manager, is_employee, render_to_pdf

#----------------------------------------------------------------------
def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

def is_employee(user):
    return user.is_authenticated and user.role == 'employee'

def is_manager_or_employee(user):
    return user.is_authenticated and user.role in ['manager', 'employee']

# ---------------------------------------------------------------------
# Dashboard (لوحة التحكم)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def dashboard(request):
    """
    يعرض لوحة التحكم مع ملخص للمبيعات والمصاريف.
    """
    today = localdate()
    month_start = today.replace(day=1)

    # استخدام الحقل الصحيح لتاريخ الفاتورة
    daily_sales = Invoice.objects.filter(date__date=today)
    monthly_sales = Invoice.objects.filter(date__date__gte=month_start)
    monthly_expenses_qs = Expense.objects.filter(date__gte=month_start)

    daily_total = daily_sales.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    monthly_total = monthly_sales.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    monthly_expenses = monthly_expenses_qs.aggregate(amount=Sum('amount'))['amount'] or Decimal('0.00')

    monthly_profit = monthly_total - monthly_expenses

    context = {
        'daily_total': daily_total,
        'daily_count': daily_sales.count(),
        'monthly_total': monthly_total,
        'monthly_count': monthly_sales.count(),
        'latest_invoices': Invoice.objects.select_related('customer').order_by('-date')[:5],
        'monthly_expenses': monthly_expenses,
        'monthly_profit': monthly_profit,
    }
    return render(request, 'dashboard.html', context)

# ---------------------------------------------------------------------
# Products (لوحة منتجات)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def product_list(request):
    products = Product.objects.all().order_by('-id')

    paginator = Paginator(products, 5)  # عرض 10 منتجات في الصفحة
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'product_list.html', {'products': products_page})

@user_passes_test(is_manager_or_employee)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

@user_passes_test(is_manager)  # فقط المدير
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'تم حذف المنتج.')
        return redirect('product_list')
    return render(request, 'confirm_delete_product.html', {'product': product})

# ---------------------------------------------------------------------
# Invoice List (قائمة الفواتير)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def invoice_list(request):
    """
    يعرض قائمة بجميع الفواتير مع pagination.
    """
    invoices_list = Invoice.objects.select_related('customer').order_by('-date')

    paginator = Paginator(invoices_list, 15)  # عرض 15 فاتورة في الصفحة
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'invoice_list.html', {
        'invoices': invoices
    })

# ---------------------------------------------------------------------
# Add Invoice (إضافة فاتورة)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def add_invoice(request):
    """
    يضيف فاتورة جديدة، مع إمكانية إنشاء عميل جديد، ويتحقق من المخزون.
    """
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == 'POST':
        try:
            with transaction.atomic(): # ضمان Atomic Transaction
                # 1. تحديد العميل أو إنشاء عميل جديد
                customer = None
                customer_id = request.POST.get('customer')

                if customer_id and customer_id != 'new':
                    customer = get_object_or_404(Customer, id=customer_id)
                else: # إنشاء عميل جديد
                    new_customer_form = CustomerForm(request.POST)
                    if new_customer_form.is_valid():
                        customer = new_customer_form.save()
                    else:
                        # إذا كان هناك أخطاء في نموذج العميل الجديد
                        for field, errors in new_customer_form.errors.items():
                            for error in errors:
                                messages.error(request, f'خطأ في بيانات العميل الجديد - {field}: {error}')
                        raise ValueError("بيانات العميل الجديد غير صحيحة.")

                if not customer: # للتأكد من وجود عميل بعد محاولة الإنشاء أو التحديد
                    messages.error(request, 'يجب تحديد عميل أو إدخال بيانات عميل جديد صالحة.')
                    raise ValueError("Customer not selected or invalid new customer data.")

                # 2. معلومات الفاتورة
                payment_method = request.POST.get('payment_method')
                try:
                    discount = Decimal(request.POST.get('discount') or '0.00')
                    if discount < 0:
                        messages.error(request, 'الخصم لا يمكن أن يكون قيمة سالبة.')
                        raise ValueError("Discount cannot be negative.")
                except Exception:
                    messages.error(request, 'قيمة الخصم غير صحيحة.')
                    raise ValueError("Invalid discount value.")
                
                try:
                    amount_paid = Decimal(request.POST.get('amount_paid') or '0.00')
                    if amount_paid < 0:
                        messages.error(request, 'المبلغ المدفوع لا يمكن أن يكون أقل من 0.')
                        raise ValueError("Invalid amount_paid.")
                except Exception:
                    messages.error(request, 'قيمة المبلغ المدفوع غير صحيحة.')
                    raise ValueError("Invalid amount_paid.")


                # تحديد بداية الشهر
                month_start = now().date().replace(day=1)
                session, _ = MonthlySession.objects.get_or_create(month=month_start)

                # لو السيشن الشهري مغلق، امنع الإضافة
                if session.status == 'closed':
                    messages.error(request, 'هذا الشهر مغلق ولا يمكن إنشاء فواتير جديدة.')
                    raise ValueError("هذا الشهر مغلق.")


                # 3. إنشاء الفاتورة (مبدئيًا)
                invoice = Invoice.objects.create(
                    customer=customer,
                    payment_method=payment_method,
                    discount=discount,
                    total=Decimal('0.00'),  # يُحسب لاحقًا
                    amount_paid=amount_paid,
                    monthly_session=session,
                )

                # 4. قراءة المنتجات والكميات وإنشاء عناصر الفاتورة
                product_ids = request.POST.getlist('product_ids')
                quantities = request.POST.getlist('quantities')

                if not product_ids:
                    messages.error(request, 'يجب إضافة منتج واحد على الأقل للفاتورة.')
                    invoice.delete() # حذف الفاتورة التي تم إنشاؤها إذا لم يكن هناك عناصر
                    raise ValueError("No products added to the invoice.")

                total_invoice_items_price = Decimal('0.00')

                for pid, qty_str in zip(product_ids, quantities):
                    if not pid or not qty_str:
                        continue # تخطي الصفوف الفارغة في النموذج

                    try:
                        product = get_object_or_404(Product, id=pid)
                        quantity = int(qty_str)
                    except (ValueError, Product.DoesNotExist):
                        messages.error(request, f'حدث خطأ في المنتج أو الكمية المدخلة.')
                        raise ValueError("Invalid product ID or quantity.") # إفشال العملية كلها

                    if quantity <= 0:
                        messages.warning(request, f'تم تجاهل المنتج "{product.name}" لأن الكمية المدخلة هي {quantity}.')
                        continue # تجاهل الكميات غير الصالحة بدلاً من إفشال العملية كلها

                    if product.quantity < quantity:
                        messages.error(request, f'الكمية المطلوبة من "{product.name}" ({quantity}) أكبر من المتاح في المخزون ({product.quantity}).')
                        raise ValueError("Insufficient stock.")

                    line_total = quantity * product.sell_price
                    total_invoice_items_price += line_total

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        price=product.sell_price # تسجيل سعر البيع وقت الفاتورة
                    )

                    # تحديث المخزون
                    product.quantity -= quantity
                    product.save()

                # 5. تحديث الإجمالي النهائي في الفاتورة
                invoice.total = total_invoice_items_price - discount
                invoice.save()

                messages.success(request, 'تم إنشاء الفاتورة بنجاح.')
                return redirect('invoice_detail', invoice_id=invoice.id)

        except ValueError as e:
            # رسائل الخطأ التي تم إطلاقها بواسطة raise ValueError
            # يتم التعامل معها في الـ messages.error بالفعل
            pass
        except Exception as e:
            messages.error(request, f'حدث خطأ غير متوقع أثناء إنشاء الفاتورة: {e}')
            # لا داعي لإعادة التوجيه هنا، سيتم عرض الصفحة مع رسالة الخطأ
            
    return render(request, 'add_invoice.html', {
        'customers': customers,
        'products': products,
        'customer_form': CustomerForm() # لإظهار نموذج العميل الجديد في الـ GET request
    })

@user_passes_test(is_manager_or_employee)
def update_invoice_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        try:
            new_amount = Decimal(request.POST.get('amount_paid') or '0.00')
            if new_amount < 0:
                messages.error(request, "المبلغ غير صالح.")
            elif new_amount > invoice.total:
                messages.error(request, "لا يمكن أن يكون المبلغ المدفوع أكبر من الإجمالي.")
            else:
                invoice.amount_paid = new_amount
                invoice.save()
                messages.success(request, "تم تحديث المبلغ المدفوع.")
                return redirect('invoice_detail', invoice_id=invoice.id)
        except:
            messages.error(request, "حدث خطأ أثناء تحديث المبلغ.")

    return render(request, 'update_invoice_payment.html', {'invoice': invoice})


# ---------------------------------------------------------------------
# Invoice Detail (تفاصيل الفاتورة)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def invoice_detail(request, invoice_id):
    """
    يعرض تفاصيل فاتورة محددة.
    """
    invoice = get_object_or_404(Invoice.objects.select_related('customer'), id=invoice_id)
    items = invoice.items.select_related('product') # استخدام related_name
    for item in items:
        item.line_total = item.price * item.quantity
        
    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'items': items,
    })

# ---------------------------------------------------------------------
# Print Invoice (طباعة الفاتورة)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def print_invoice(request, invoice_id):
    """
    يعرض قالب الفاتورة المخصص للطباعة.
    """
    invoice = get_object_or_404(Invoice.objects.select_related('customer'), id=invoice_id)
    items = invoice.items.select_related('product')
    return render(request, 'print_invoice.html', {
        'invoice': invoice,
        'items': items,
    })

# ---------------------------------------------------------------------
# Delete Invoice (حذف فاتورة)
# ---------------------------------------------------------------------
@user_passes_test(is_manager)  # فقط المدير
def delete_invoice(request, invoice_id):
    """
    يحذف فاتورة محددة ويعيد المنتجات إلى المخزون (يتطلب POST للحماية).
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # استعادة المخزون لكل عنصر في الفاتورة
                for item in invoice.items.all():
                    product = item.product
                    product.quantity += item.quantity # إضافة الكمية المسترجعة
                    product.save()
                
                invoice.delete()
                messages.success(request, 'تم حذف الفاتورة بنجاح واستعادة المنتجات إلى المخزون.')
                return redirect('invoice_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف الفاتورة: {e}')
            return redirect('invoice_detail', invoice_id=invoice_id)
    
    # في حالة طلب GET، نعرض صفحة تأكيد الحذف
    return render(request, 'confirm_delete_invoice.html', {'invoice': invoice})

# ---------------------------------------------------------------------
# Sales Report (تقرير المبيعات)
# ---------------------------------------------------------------------
@user_passes_test(is_manager)  # فقط المدير
def sales_report(request):
    """
    يعرض تقرير المبيعات بناءً على فلاتر مختلفة.
    """
    form = SalesReportForm(request.GET or None)
    invoices = Invoice.objects.select_related('customer').order_by('-created_at') # Order by for consistency

    if form.is_valid():
        customer = form.cleaned_data.get('customer')
        product = form.cleaned_data.get('product')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if customer:
            invoices = invoices.filter(customer=customer)
        if date_from:
            invoices = invoices.filter(created_at__date__gte=date_from)
        if date_to:
            invoices = invoices.filter(created_at__date__lte=date_to)

        if product:
            invoices = invoices.filter(items__product=product).distinct()

    total = invoices.aggregate(total_sum=Sum('total'))['total_sum'] or Decimal('0.00')

    # إضافة Pagination للتقرير أيضاً
    paginator = Paginator(invoices, 20) # 20 فاتورة في الصفحة
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'sales_report.html', {
        'form': form,
        'invoices': invoices,
        'total': total,
    })

# ---------------------------------------------------------------------
# Invoice PDF (طباعة الفاتورة كـ PDF)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def invoice_pdf(request, invoice_id):
    """
    ينشئ فاتورة بصيغة PDF.
    """
    invoice = get_object_or_404(Invoice.objects.select_related('customer'), id=invoice_id)
    items = invoice.items.select_related('product')
    context = {
        'invoice': invoice,
        'items': items
    }
    return render_to_pdf('invoice_pdf_template.html', context) # تأكد أن هذا القالب موجود

# ---------------------------------------------------------------------
# Add Product (إضافة منتج)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def add_product(request):
    """
    يضيف منتج جديد باستخدام Django Form.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المنتج بنجاح.')
            return redirect('dashboard') # افترض وجود URL لصفحة المنتجات
        else:
            messages.error(request, 'الرجاء تصحيح الأخطاء في النموذج.')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

# ---------------------------------------------------------------------
# Add Expense (إضافة مصاريف)
# ---------------------------------------------------------------------
@user_passes_test(is_manager_or_employee)
def add_expense(request):
    """
    يضيف مصروف جديد باستخدام ExpenseForm ويربطه بجلسة شهرية.
    """
    # تحديد أول يوم في الشهر الحالي
    month_start = now().date().replace(day=1)

    # الحصول أو إنشاء MonthlySession لهذا الشهر
    session, _ = MonthlySession.objects.get_or_create(month=month_start)

    # منع الإضافة لو الشهر مغلق
    if session.status == 'closed':
        messages.error(request, "لا يمكن إضافة مصروفات لأن هذا الشهر مغلق.")
        return redirect('expenses_list')

    # عند إرسال POST
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.monthly_session = session  # ربط المصروف بالشهر
            expense.save()
            messages.success(request, 'تم تسجيل المصروف بنجاح.')
            return redirect('expenses_list')
        else:
            messages.error(request, 'الرجاء تصحيح الأخطاء في النموذج.')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})

@user_passes_test(is_manager_or_employee)
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, "تم حذف المصروف بنجاح.")
        return redirect('expenses_list')
    
    # ✅ لا ترجع صفحة تأكيد
    return redirect('expenses_list')


# ---------------------------------------------------------------------
# Expenses List (قائمة المصاريف)
# ---------------------------------------------------------------------
@user_passes_test(is_manager)  # فقط المدير
def expenses_list(request):
    """
    يعرض قائمة بالمصاريف مع إجمالي المصاريف.
    """
    expenses_list_qs = Expense.objects.order_by('-date')
    total_expenses = expenses_list_qs.aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')

    # إضافة Pagination للمصاريف
    paginator = Paginator(expenses_list_qs, 10)  # 10 مصاريف في الصفحة
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)

    return render(request, 'expenses_list.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
    })
#---------------------------------------------------------------------------
# MANAGE MONTH  (إدارة الشهور )
#------------------------------------
@user_passes_test(is_manager)
def manage_months(request):
    months = MonthlySession.objects.order_by('-month')
    return render(request, 'manage_months.html', {'months': months})

@user_passes_test(is_manager)
def toggle_month_status(request, month_id):
    session = get_object_or_404(MonthlySession, id=month_id)
    session.status = 'closed' if session.status == 'open' else 'open'
    session.save()
    messages.success(request, f"تم تغيير حالة الشهر إلى: {'مغلق' if session.status == 'closed' else 'مفتوح'}")
    return redirect('manage_months')

@user_passes_test(is_manager)
def monthly_report(request, session_id):
    session = get_object_or_404(MonthlySession, id=session_id)

    invoices = Invoice.objects.filter(monthly_session=session)
    expenses = Expense.objects.filter(monthly_session=session)

    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_sales - total_expenses

    context = {
        'session': session,
        'invoices': invoices,
        'expenses': expenses,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'profit': profit,
    }

    return render(request, 'monthly_report.html', context)
