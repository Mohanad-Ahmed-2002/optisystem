import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserSubscription

def render_to_pdf(template_src, context_dict):
    html = render_to_string(template_src, context_dict)
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(html, False, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    return response

def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

def is_employee(user):
    return user.is_authenticated and user.role == 'employee'

def is_manager_or_employee(user):
    return user.is_authenticated and user.role in ['manager', 'employee']

def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        # ✅ superuser يتجاوز التحقق
        if user.is_authenticated and user.is_superuser:
            return view_func(request, *args, **kwargs)

        # ✅ السماح بالدخول طالما صاحب المحل مشترك
        if user.is_authenticated and user.role in ['manager', 'employee']:
            shop = getattr(user, 'shop', None)
            if not shop:
                messages.error(request, "⚠️ لم يتم ربط حسابك بأي محل.")
                return redirect('choose_plan')

            owner = getattr(shop, 'owner', None)
            if not owner:
                messages.error(request, "⚠️ لا يوجد مدير لهذا المحل.")
                return redirect('choose_plan')

            subscription = getattr(owner, 'usersubscription', None)
            if not subscription or not subscription.is_active():
                messages.error(request, "⚠️ اشتراك المحل غير فعال أو منتهي. الرجاء التجديد.")
                return redirect('choose_plan')

        # ✅ التحقق من الموافقة
        # ✅ شرط التحقق فقط للمدير
        if user.is_authenticated and user.role == 'manager' and not user.is_approved:
            messages.warning(request, "حسابك قيد المراجعة، سيتم تفعيله بعد موافقة الإدارة.")
            return redirect('waiting_approval')


        return view_func(request, *args, **kwargs)
    return wrapper

from functools import wraps

def block_superuser(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect('platform_admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
