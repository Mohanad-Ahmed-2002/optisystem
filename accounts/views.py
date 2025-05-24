# accounts/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages # لاستخدام الرسائل
from .forms import CreateEmployeeForm, LoginForm # تأكد من استيراد LoginForm
# تأكد أن is_manager و is_employee موجودة في utils.py في مجلد المشروع الرئيسي
# إذا كانت في تطبيق accounts، أضفها هنا
# from .utils import is_manager, is_employee # لو كانت utils.py في مجلد المشروع الرئيسي

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
    users = User.objects.exclude(id=request.user.id).order_by('-date_joined')
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