from django.shortcuts import redirect
from django.http import HttpResponse

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_paths = [
            '/admin/', '/login/', '/signup/', '/choose-plan/', '/signup-with-plan/',
            '/waiting-approval/', '/activate-user/', '/deactivate-user/', '/platform-admin-dashboard/'
        ]
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        if request.user.is_authenticated:
            if request.user.role in ['manager', 'employee'] and not request.user.is_superuser:
                shop = request.user.shop
                if not shop:
                    print("🚫 المستخدم مش مربوط بأي محل.")
                    return redirect('choose_plan')

                owner = getattr(shop, 'owner', None)
                if not owner:
                    print("🚫 مفيش owner مربوط بالمحل.")
                    return redirect('choose_plan')

                subscription = getattr(owner, 'usersubscription', None)
                if not subscription:
                    print("🚫 مفيش اشتراك مربوط بصاحب المحل.")
                    return redirect('choose_plan')

                if not subscription.is_active():
                    print("⚠️ الاشتراك موجود لكنه غير فعّال.")
                    return redirect('choose_plan')

                print("✅ اشتراك صاحب المحل فعّال. السماح بالدخول.")
        
        return self.get_response(request)
