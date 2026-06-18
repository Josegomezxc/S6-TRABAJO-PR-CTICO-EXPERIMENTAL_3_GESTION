from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.core.mock_data import get_mock_notifications


NOTIF_BATCH = 6


@login_required(login_url='login')
def notification_list_view(request):
    notifs = get_mock_notifications(request.user, NOTIF_BATCH)
    counts = {
        'all': len(notifs),
        'unread': sum(1 for n in notifs if not n.read),
        'pending': sum(1 for n in notifs if n.status == 'pending'),
        'forwarded': sum(1 for n in notifs if n.type == 'forwarded'),
        'discarded': sum(1 for n in notifs if n.status == 'discarded'),
    }

    return render(request, 'notifications/notifications.html', {
        'notifications': notifs,
        'pending_count': counts['pending'],
        'counts': counts,
        'has_more': False,
        'next_offset': len(notifs),
        'batch_size': NOTIF_BATCH,
    })


@login_required(login_url='login')
def notification_more_api(request):
    return JsonResponse({'ok': True, 'html': '', 'count': 0, 'next_offset': 0, 'has_more': False})


@login_required(login_url='login')
def notification_detail_view(request, pk):
    notifs = get_mock_notifications(request.user)
    notif = next((n for n in notifs if n.id == pk), None)
    if not notif:
        notif = get_mock_notifications(request.user, 1)[0]
    return render(request, 'notifications/notification_detail.html', {
        'notif': notif,
        'email': None,
    })


@login_required(login_url='login')
def notification_unread_api(request):
    return JsonResponse({
        'unread_count': 0,
        'pending_count': 0,
        'unread_pending_count': 0,
        'unread_ids': [],
        'last_toast_id': 0,
        'total': 0,
        'recent': [],
    })


@login_required(login_url='login')
def notification_mark_read_api(request, pk):
    return JsonResponse({'ok': True, 'read': True})


@login_required(login_url='login')
def notification_mark_all_read_api(request):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def notification_mark_toast_shown_api(request):
    return JsonResponse({'ok': True, 'last_toast_id': 0})


@login_required(login_url='login')
def notification_forward_api(request, pk):
    return JsonResponse({'ok': False, 'error': 'no_actionable'}, status=400)


@login_required(login_url='login')
def notification_clear_api(request):
    return JsonResponse({'ok': True, 'deleted': 0})


@login_required(login_url='login')
def notification_discard_api(request, pk):
    return JsonResponse({'ok': False, 'error': 'no_actionable'}, status=400)
