from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now
from decimal import Decimal
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
import time
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..models import Invoice, InvoiceItem,Lens, Product, Customer, MonthlySession, InvoicePayment
from ..forms import CustomerForm
from ..utils import  is_manager, is_employee, is_manager_or_employee,subscription_required,block_superuser


@block_superuser
@user_passes_test(is_manager_or_employee)
def invoice_list(request):
    search_query = request.GET.get('search', '')

    # 🔒 فلترة حسب المحل الحالي
    invoices_list = Invoice.objects.select_related('customer')\
        .filter(shop=request.user.shop)\
        .order_by('-date')

    if search_query:
        invoices_list = invoices_list.filter(customer__name__icontains=search_query)

    paginator = Paginator(invoices_list, 15)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'invoice_list.html', {
        'invoices': invoices,
        'search_query': search_query
    })


@block_superuser
@subscription_required
@user_passes_test(is_manager_or_employee)
def add_invoice(request):
    customers = Customer.objects.filter(shop=request.user.shop)
    products = Product.objects.filter(shop=request.user.shop)
    lenses = Lens.objects.filter(shop=request.user.shop)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                customer = None
                customer_id = request.POST.get('customer')

                if customer_id and customer_id != 'new':
                    customer = get_object_or_404(Customer, id=customer_id, shop=request.user.shop)
                else:
                    new_customer_form = CustomerForm(request.POST)
                    if new_customer_form.is_valid():
                        customer = new_customer_form.save(commit=False)
                        customer.shop = request.user.shop
                        customer.save()
                    else:
                        for field, errors in new_customer_form.errors.items():
                            for error in errors:
                                messages.error(request, f'خطأ في بيانات العميل الجديد - {field}: {error}')
                        raise ValueError("بيانات العميل الجديد غير صحيحة.")

                if not customer:
                    messages.error(request, 'يجب تحديد عميل أو إدخال بيانات عميل جديد صالحة.')
                    raise ValueError("Customer not selected or invalid new customer data.")

                payment_method = request.POST.get('payment_method')
                sale_type = request.POST.get('sale_type') or 'قطاعي'

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

                # ✅ حماية الجلسة الشهرية
                month_start = now().date().replace(day=1)
                session = None
                for attempt in range(3):
                    try:
                        session, _ = MonthlySession.objects.get_or_create(
                            month=month_start,
                            shop=request.user.shop,
                            defaults={'status': 'open'}
                        )
                        break
                    except IntegrityError:
                        time.sleep(0.1)
                        try:
                            session = MonthlySession.objects.get(month=month_start, shop=request.user.shop)
                            break
                        except ObjectDoesNotExist:
                            if attempt == 2:
                                messages.error(request, '⚠️ تعذر إنشاء جلسة الشهر الحالي. حاول مجددًا أو تواصل مع الدعم.')
                                raise

                if session.status == 'closed':
                    messages.error(request, 'هذا الشهر مغلق ولا يمكن إنشاء فواتير جديدة.')
                    raise ValueError("هذا الشهر مغلق.")

                invoice = Invoice.objects.create(
                    customer=customer,
                    payment_method=payment_method,
                    discount=discount,
                    total=Decimal('0.00'),
                    monthly_session=session,
                    shop=request.user.shop,
                    sale_type=sale_type
                )

                # ✅ دفعة أولى
                if amount_paid > 0:
                    InvoicePayment.objects.create(
                        invoice=invoice,
                        amount=amount_paid,
                        notes="دفعة أولى عند إنشاء الفاتورة"
                    )

                product_ids = request.POST.getlist('product_ids')
                quantities = request.POST.getlist('quantities')

                if not product_ids:
                    messages.error(request, 'يجب إضافة منتج واحد على الأقل للفاتورة.')
                    invoice.delete()
                    raise ValueError("No products added to the invoice.")

                total_invoice_items_price = Decimal('0.00')

                for pid, qty_str in zip(product_ids, quantities):
                    if not pid or not qty_str:
                        continue

                    product = get_object_or_404(Product, id=pid, shop=request.user.shop)
                    quantity = int(qty_str)

                    if quantity <= 0:
                        messages.warning(request, f'تم تجاهل المنتج \"{product.name}\" لأن الكمية المدخلة هي {quantity}.')
                        continue

                    if product.quantity < quantity:
                        messages.error(request, f'الكمية المطلوبة من \"{product.name}\" ({quantity}) أكبر من المتاح ({product.quantity}).')
                        raise ValueError("Insufficient stock.")

                    price = product.buy_price if sale_type == 'جملة' else product.sell_price
                    line_total = quantity * price
                    total_invoice_items_price += line_total

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    product.quantity -= quantity
                    product.save()

                lens_ids = request.POST.getlist('lens_ids')
                lens_quantities = request.POST.getlist('lens_quantities')

                for lid, qty_str in zip(lens_ids, lens_quantities):
                    if not lid or not qty_str:
                        continue

                    lens = get_object_or_404(Lens, id=lid, shop=request.user.shop)
                    quantity = int(qty_str)

                    if quantity <= 0:
                        messages.warning(request, f'تم تجاهل العدسة \"{lens.name}\" لأن الكمية المدخلة هي {quantity}.')
                        continue

                    price = lens.buy_price if sale_type == 'جملة' else lens.sell_price
                    line_total = quantity * price
                    total_invoice_items_price += line_total

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        lens=lens,
                        quantity=quantity,
                        price=price
                    )

                invoice.total = total_invoice_items_price - discount
                invoice.save()

                messages.success(request, 'تم إنشاء الفاتورة بنجاح.')
                return redirect('invoice_detail', invoice_id=invoice.id)

        except ValueError:
            pass
        except Exception as e:
            messages.error(request, f'حدث خطأ غير متوقع أثناء إنشاء الفاتورة: {e}')

    return render(request, 'add_invoice.html', {
        'customers': customers,
        'products': products,
        'lenses': lenses,
        'customer_form': CustomerForm()
    })

@block_superuser
@user_passes_test(is_manager_or_employee)
def update_invoice_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, shop=request.user.shop)

    messages.error(request, "هذا الإجراء لم يعد متاحًا. استخدم زر 'إضافة دفعة جديدة'.")
    return redirect('invoice_detail', invoice_id=invoice.id)

@block_superuser
@user_passes_test(is_manager_or_employee)
def add_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, shop=request.user.shop)
    
    if invoice.monthly_session and invoice.monthly_session.status == "closed":
        messages.error(request, "❌ لا يمكن تسجيل دفعة لأن الشهر مغلق.")
        return redirect('invoice_detail', invoice_id=invoice.id)


    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount') or '0')
            notes = request.POST.get('notes', '')
            if amount <= 0:
                messages.error(request, '❌ يجب إدخال مبلغ صحيح.')
            elif amount + invoice.amount_paid > invoice.total:
                messages.error(request, '❌ مجموع الدفعات يتجاوز إجمالي الفاتورة.')
            else:
                InvoicePayment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    notes=notes
                )
                messages.success(request, '✅ تم تسجيل الدفعة بنجاح.')
                return redirect('invoice_detail', invoice_id=invoice.id)
        except:
            messages.error(request, 'حدث خطأ أثناء حفظ الدفعة.')

    return render(request, 'add_payment.html', {'invoice': invoice})

@block_superuser
@user_passes_test(is_manager_or_employee)
def delete_payment(request, payment_id):
    payment = get_object_or_404(InvoicePayment, id=payment_id)

    if payment.invoice.monthly_session and payment.invoice.monthly_session.status == "closed":
        messages.error(request, "❌ لا يمكن حذف دفعة لأن الشهر مغلق.")
        return redirect('invoice_detail', invoice_id=payment.invoice.id)


    # 🔒 التأكد إن الفاتورة التابعة للدفعة تخص نفس المحل
    if payment.invoice.shop != request.user.shop:
        raise PermissionDenied("غير مسموح لك بحذف هذه الدفعة.")

    invoice_id = payment.invoice.id
    payment.delete()
    messages.success(request, '✅ تم حذف الدفعة بنجاح.')
    return redirect('invoice_detail', invoice_id=invoice_id)

@block_superuser
@user_passes_test(is_manager_or_employee)
def invoice_detail(request, invoice_id):
    # 🔒 نجيب الفاتورة بس لو تبع نفس الـ shop
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer'),
        id=invoice_id,
        shop=request.user.shop
    )

    items = invoice.items.select_related('product')
    for item in items:
        item.line_total = item.price * item.quantity

    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })

@user_passes_test(is_manager_or_employee)
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer', 'shop'),
        id=invoice_id,
        shop=request.user.shop
    )
    items = invoice.items.select_related('product', 'lens')
    for item in items:
        item.line_total = item.price * item.quantity

    total_before_discount = invoice.total + (invoice.discount or 0)
    remaining = invoice.total - invoice.amount_paid

    context = {
        'invoice': invoice,
        'items': items,
        'shop': invoice.shop,
        'total_before_discount': total_before_discount,
        'remaining': remaining,

    }
    return render(request, 'print_invoice.html', context)


@user_passes_test(is_manager)
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, shop=request.user.shop)  # 🔒 حماية بالـ Shop

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for item in invoice.items.all():
                    if item.product:
                        item.product.quantity += item.quantity
                        item.product.save()

                invoice.delete()
                messages.success(request, 'تم حذف الفاتورة بنجاح واستعادة المنتجات إلى المخزون.')
                return redirect('invoice_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف الفاتورة: {e}')
            return redirect('invoice_detail', invoice_id=invoice_id)

    return render(request, 'confirm_delete_invoice.html', {'invoice': invoice})

def get_product_by_barcode(request):
    barcode = request.GET.get('barcode', '')
    if not barcode:
        return JsonResponse({'success': False, 'error': 'لا يوجد باركود'})

    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            'success': True,
            'id': product.id,
            'name': product.name,
            'sell_price': float(product.sell_price),
            'quantity': product.quantity
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المنتج غير موجود'})

def search_customers(request):
    q = request.GET.get('q', '')
    shop = request.user.shop
    results = Customer.objects.filter(shop=shop, name__icontains=q)[:10]
    data = [{'id': c.id, 'name': c.name, 'phone': c.phone} for c in results]
    return JsonResponse(data, safe=False)