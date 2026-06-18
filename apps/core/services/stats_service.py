def dashboard_stats(user):
    return {
        'total_emails': 42,
        'threats_blocked': 7,
        'safe_emails': 30,
        'pending_review': 5,
        'today_emails': 3,
        'today_threats': 1,
        'block_rate': 16.7,
        'total_trend': '+12%',
        'threats_trend': '+2',
        'safe_trend': '+8%',
        'pending_trend': '-1',
    }


def profile_stats(user):
    return {
        'total_emails': 42,
        'alias_count': 3,
        'threats_count': 7,
        'safe_count': 30,
    }


def admin_global_stats():
    from django.contrib.auth.models import User
    total = User.objects.count()
    staff = User.objects.filter(is_staff=True).count()
    active = User.objects.filter(is_active=True).count()
    return {
        'users_total': total,
        'users_staff': staff,
        'users_active': active,
        'users_inactive': total - active,
        'users_active_regular': active - staff,
        'total_aliases': 5,
        'aliases_total': 5,
        'aliases_active': 5,
        'aliases_active_pct': 100,
        'total_emails': 89,
        'emails_total': 89,
        'emails_24h': 5,
        'emails_7d': 23,
        'emails_trend': 12,
        'total_threats': 14,
        'threats_total': 14,
        'threats_24h': 2,
        'threats_trend': 5,
        'new_users_24h': 0,
        'new_emails_24h': 5,
        'new_emails_7d': 23,
    }
