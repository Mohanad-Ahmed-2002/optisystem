# accounts/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages # لاستخدام الرسائل
from .forms import CreateEmployeeForm, LoginForm # تأكد من استيراد LoginForm
from core.models import Shop
from django.shortcuts import render, redirect
from .models import SubscriptionPlan,UserSubscription
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.utils import timezone
from datetime import timedelta
from datetime import date

# تأكد أن is_manager و is_employee موجودة في utils.py في مجلد المشروع الرئيسي
# إذا كانت في تطبيق accounts، أضفها هنا
from core.utils import is_manager_or_employee

User = get_user_model()

# دوال التحقق من الدور (يمكنك استيرادها من utils.py في مجلد المشروع الرئيسي)
# بما أنك أرسلت utils.py وفيه هذه الدوال، سنفترض أنها هناك.
# لكن لضمان عملها بشكل مباشر في هذا الملف، أعد تعريفها هنا إذا لم يتم استيرادها.
def is_manager(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'manager'

def is_employee(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'employee'

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'manager')

@login_required
@user_passes_test(is_admin, login_url='dashboard') # فقط المشرفون يمكنهم إضافة موظفين
def add_employee(request):
    if request.method == 'POST':
        form = CreateEmployeeForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True  # تعيينه كموظف في Django admin
            # الدور يتم تعيينه تلقائياً من الفورم (field 'role')
            user.shop = request.user.shop
            user.save()
            messages.success(request, f'تم إضافة الموظف {user.username} بنجاح.')
            return redirect('add_employee')  # أو 'manage_users'
        else:
            messages.error(request, 'حدث خطأ أثناء إضافة الموظف. يرجى التحقق من البيانات.')
    else:
        form = CreateEmployeeForm()
    return render(request, 'accounts/add_employee.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # لو مسجل دخول، حوله مباشرة للوحة التحكم

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # استخدام LOGIN_REDIRECT_URL من settings.py
                if user.role == 'manager' and not user.shop:
                    shop = Shop.objects.create(name=f"محل {user.username}", owner=user)
                    user.shop = shop
                    user.save()

                return redirect('dashboard') # أو settings.LOGIN_REDIRECT_URL
            else:
                messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
        # إذا الفورم غير صالح أو authenticate فشل
        return render(request, 'accounts/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "تم تسجيل الخروج بنجاح.")
    return redirect('login') # بعد تسجيل الخروج، ارجع لصفحة تسجيل الدخول

@login_required
@user_passes_test(is_admin, login_url='dashboard') # تقييد الوصول للمشرفين فقط
def manage_users(request):
    # استبعاد المستخدم الحالي (المشرف) من القائمة
    users = User.objects.filter(shop=request.user.shop, is_superuser=False).exclude(id=request.user.id)
    return render(request, 'accounts/manage_users.html', {'users': users})

@login_required
@user_passes_test(is_admin, login_url='dashboard') # تقييد الوصول للمشرفين فقط
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # لا تسمح للمشرف بحذف نفسه أو حذف superuser آخر
    if user.is_superuser:
        messages.error(request, "لا يمكنك حذف المستخدم المشرف (superuser).")
        return redirect('manage_users')

    if request.method == 'POST':
        user.delete()
        messages.success(request, f'تم حذف المستخدم "{user.username}" بنجاح.')
        return redirect('manage_users')
    return render(request, 'accounts/delete_user_confirmation.html', {'user': user})

# ---------------------------------------------------------------------------------------------
# Subscription
# -----------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from .models import SubscriptionPlan
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def choose_plan(request):
    plans = SubscriptionPlan.objects.all()
    if request.method == 'POST':
        plan_key = request.POST.get('plan')
        if plan_key in ['monthly', '3months']:
            try:
                selected_plan = SubscriptionPlan.objects.get(name=plan_key)
                request.session['selected_plan'] = plan_key
                return redirect('signup_with_plan', plan_id=selected_plan.id)  # ✅ بعد ما جبنا الخطة فعلاً
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, 'الخطة غير موجودة.')
        else:
            messages.error(request, 'يرجى اختيار خطة صحيحة.')

    return render(request, 'accounts/choose_plan.html')


@login_required
def some_page(request):
    if not hasattr(request.user, 'usersubscription') or not request.user.usersubscription.is_active():
        messages.error(request, "اشتراكك غير فعال، برجاء التجديد.")
        return redirect('choose_plan')
    return render(request, 'your_template.html')

from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription
from .forms import CustomUserCreationForm
from django.contrib.auth import login

def signup_with_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            shop_name = form.cleaned_data.get('shop_name')
            user.role = 'manager'
            user.is_active = False  # 🛑 نوقف حسابه مؤقتًا
            user.save()

            # إنشاء المحل وربطه بالمستخدم
            shop = Shop.objects.create(name=shop_name, owner=user)
            user.shop = shop
            user.save()


            # إنشاء الاشتراك
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=plan.duration_days)
            UserSubscription.objects.create(
                user=user,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
            )

            login(request, user)  # تسجيل الدخول تلقائي بعد التسجيل
            messages.info(request, "✅ تم التسجيل بنجاح، في انتظار موافقة الإدارة لتفعيل حسابك.")
            return redirect('waiting_approval') 

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup_with_plan.html', {
        'form': form,
        'plan': plan
    })

def waiting_approval(request):
    return render(request, 'accounts/waiting_approval.html')

@login_required
@user_passes_test(is_admin)
def pending_approvals(request):
    users = User.objects.filter(is_active=True, is_approved=False, role='manager')
    return render(request, 'accounts/pending_approvals.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"✅ تم تفعيل حساب {user.username}.")
    return redirect('pending_approvals')

from django.contrib.admin.views.decorators import staff_member_required

from datetime import date

@staff_member_required(login_url='login')
def platform_admin_dashboard(request):
    users = User.objects.filter(is_superuser=False, role='manager').select_related('shop', 'usersubscription__plan')

    for user in users:
        if hasattr(user, 'usersubscription') and user.usersubscription.end_date:
            user.days_left = (user.usersubscription.end_date.date() - date.today()).days
        else:
            user.days_left = None

    return render(request, 'accounts/platform_admin_dashboard.html', {'users': users})



from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect

User = get_user_model()

@user_passes_test(lambda u: u.is_superuser)
def activate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.is_approved = True  # ✅ التفعيل الكامل
    user.save()
    messages.success(request, f"تم تفعيل {user.username} بنجاح ✅")
    return redirect('platform_admin_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def deactivate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    messages.warning(request, f"تم إيقاف {user.username} ❌")
    return redirect('platform_admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def superuser_delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.info(request, f"تم حذف {user.username} نهائيًا 🗑️")
    return redirect('platform_admin_dashboard')


@login_required
def custom_redirect_view(request):
    if request.user.is_superuser:
        return redirect('platform_admin_dashboard')  # لوحة المدير
    else:
        return redirect('dashboard')  # الصفحة العادية للعميل
