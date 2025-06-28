from datetime import date
from .models import UserSubscription

def subscription_alert(request):
    context = {}
    user = request.user

    if user.is_authenticated and user.role in ['manager', 'employee'] and not user.is_superuser:
        shop = user.shop
        if shop:
            owner = shop.owner
            subscription = getattr(owner, 'usersubscription', None)
            if subscription and subscription.end_date:
                days_left = (subscription.end_date.date() - date.today()).days
                if days_left <= 1:
                    context['subscription_days_left'] = days_left
    return context
