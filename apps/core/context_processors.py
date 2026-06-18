from apps.accounts.services.profile_service import get_user_initials, get_user_color


def sidebar_counts(request):
    if not request.user.is_authenticated:
        return {
            'alias_count': 0, 'unread_count': 0, 'threats_count': 0,
            'notif_pending_count': 0, 'notif_unread_count': 0,
            'notif_unread_pending_count': 0, 'drafts_count': 0, 'trash_count': 0,
            'active_aliases': [],
            'alias_requests_pending_count': 0,
            'account_recovery_pending_count': 0,
            'avatar_initials': '', 'avatar_color': '#7c5cff',
        }

    from apps.core.mock_data import get_mock_aliases
    user = request.user
    active_aliases = [a for a in get_mock_aliases(user) if a.is_active]

    return {
        'alias_count': len(active_aliases),
        'active_aliases': active_aliases,
        'unread_count': 5,
        'threats_count': 7,
        'notif_pending_count': 0,
        'notif_unread_count': 4,
        'notif_unread_pending_count': 0,
        'drafts_count': 3,
        'trash_count': 3,
        'alias_requests_pending_count': 0,
        'account_recovery_pending_count': 0,
        'avatar_initials': get_user_initials(user),
        'avatar_color': get_user_color(user),
    }
