from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.services.stats_service import admin_global_stats
from apps.core.mock_data import (
    get_mock_emails, get_mock_aliases, get_mock_notifications,
    get_mock_quota_requests, get_mock_account_recovery_requests,
)


ADMIN_PAGE_SIZE = 6


def admin_dashboard_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    stats = admin_global_stats()
    now = timezone.now()

    threats = []
    for i in range(6):
        alias_user = type('User', (), {'email': 'user@example.com', 'pk': 1})()
        alias = type('Alias', (), {'address': f'alias{i}@prototype.local', 'user': alias_user})()
        t = type('Threat', (), {
            'id': i+1, 'from_email': f'phishing{i}@malware.com',
            'subject': f'Amenaza detectada #{i+1}',
            'risk_score': 80 + i,
            'received_at': now - timedelta(hours=i),
            'alias': alias,
        })()
        delta = now - t.received_at
        secs = int(delta.total_seconds())
        t.time_short = f'{secs // 3600}h' if secs < 86400 else f'{secs // 86400}d'
        threats.append(t)

    top_users = []
    for u in User.objects.all()[:5]:
        u.emails_count = 10
        top_users.append(u)

    activity_7d = [{'label': (now - timedelta(days=6-i)).strftime('%d/%m'), 'count': max(1, 4 - abs(3-i))} for i in range(7)]
    safe_pct = round(60 / (60 + 25 + 14) * 100)
    susp_pct = round(25 / (60 + 25 + 14) * 100)

    return render(request, 'core/admin_dashboard.html', {
        **stats,
        'top_users': top_users,
        'recent_threats': threats,
        'safe_count': 60,
        'susp_count': 25,
        'safe_pct': safe_pct,
        'susp_pct': susp_pct,
        'threats_pct': round(14 / (60 + 25 + 14) * 100),
        'users_active_regular': max(0, User.objects.filter(is_staff=False).count()),
        'users_inactive': max(0, User.objects.filter(is_active=False).count()),
        'emails_7d': 23,
        'aliases_active': 5,
        'aliases_active_pct': 80,
        'activity_7d': activity_7d,
    })


def admin_users_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    users = User.objects.all().order_by('-date_joined')
    counts = {
        'all': users.count(),
        'admin': users.filter(is_staff=True).count(),
        'user': users.filter(is_staff=False).count(),
        'threats': 0,
    }

    for u in users:
        u.aliases_count = 2
        u.emails_count = 10
        u.threats_count = 3

    return render(request, 'core/admin_users.html', {
        'users': users,
        'counts': counts,
        'q': '',
        'role': 'all',
        'qs_params': '',
    })


def admin_user_detail_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')

    target = User.objects.filter(pk=pk).first()
    if not target:
        return redirect('admin_users')

    aliases = get_mock_aliases(target)
    recent_emails = get_mock_emails(target, 15)

    return render(request, 'core/admin_user_detail.html', {
        'target': target,
        'aliases': aliases,
        'recent_emails': recent_emails,
        'emails_total': 15,
        'threats_total': 4,
        'target_quota_used': len(aliases),
        'target_quota_limit': 5,
        'target_quota_extra': 0,
        'target_is_unlimited': False,
        'target_alias_unlimited': False,
        'quota_base_limit': 5,
        'quota_min': 1,
        'quota_max': 999,
    })


@require_POST
def admin_toggle_staff(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad deshabilitada en el prototipo.')
    return redirect('admin_users')


def admin_aliases_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    aliases = []
    for user in User.objects.all():
        aliases.extend(get_mock_aliases(user))

    return render(request, 'core/admin_aliases.html', {
        'aliases': aliases,
        'total_count': len(aliases),
        'active_count': sum(1 for a in aliases if a.is_active),
        'destroyed_count': sum(1 for a in aliases if not a.is_active),
        'with_threats_count': 2,
        'shown_count': len(aliases),
        'current_state': 'all',
        'current_q': '',
    })


def admin_threats_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    now = timezone.now()
    threats = []
    for i in range(12):
        user = type('User', (), {'pk': 1, 'email': 'user@example.com'})()
        alias = type('Alias', (), {'address': f'alias{i}@prototype.local', 'user': user})()
        analysis = type('Analysis', (), {'pk': i+1})()
        t = type('Threat', (), {
            'id': i+1, 'from_email': f'phishing{i}@malware.com',
            'subject': f'Amenaza #{i+1}',
            'risk_score': 70 + (i % 30),
            'received_at': now - timedelta(hours=i),
            'alias': alias,
            'alias__user__email': 'user@example.com',
            'analysis': analysis if i < 6 else None,
        })()
        delta = now - t.received_at
        secs = int(delta.total_seconds())
        t.time_short = f'{secs // 3600}h' if secs < 86400 else f'{secs // 86400}d'
        threats.append(t)

    return render(request, 'core/admin_threats.html', {
        'threats': threats[:6],
        'total_threats': len(threats),
        'critical_count': 5,
        'high_count': 7,
        'today_count': 3,
        'current_level': 'all',
        'current_q': '',
        'qs_params': '',
    })


def admin_alias_requests_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    now = timezone.now()
    requests = []
    users = list(User.objects.all()) or [request.user]
    for i, status in enumerate(['pending', 'approved', 'rejected', 'pending']):
        u = users[i % len(users)]
        r = type('AliasQuotaRequest', (), {
            'id': i+1,
            'pk': i+1,
            'user': u,
            'requested_amount': [5, 10, 3, 8][i],
            'granted_amount': [0, 10, 0, 0][i],
            'status': status,
            'reason': ['Necesito mas alias', 'Proyecto nuevo', 'Ya no necesito', 'Campaña marketing'][i],
            'admin_note': 'Aprobado' if status == 'approved' else ('Demasiados alias inactivos' if status == 'rejected' else ''),
            'created_at': now - timedelta(days=i),
            'resolved_at': now - timedelta(days=i-1) if status != 'pending' else None,
        })()
        delta = now - r.created_at
        secs = int(delta.total_seconds())
        r.time_short = f'{max(1, secs // 60)} min' if secs < 3600 else (f'{secs // 3600} h' if secs < 86400 else f'{secs // 86400} d')
        requests.append(r)

    paginator = Paginator(requests, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    counts = {
        'all': len(requests),
        'pending': sum(1 for r in requests if r.status == 'pending'),
        'approved': sum(1 for r in requests if r.status == 'approved'),
        'rejected': sum(1 for r in requests if r.status == 'rejected'),
    }
    return render(request, 'core/admin_alias_requests.html', {
        'requests': requests,
        'page_obj': page_obj,
        'counts': counts,
        'status_filter': 'all',
        'q': '',
        'qs_params': '',
    })


def admin_account_recovery_requests_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    now = timezone.now()
    requests = []
    users = list(User.objects.all()) or [request.user]
    for i, status in enumerate(['pending', 'approved', 'rejected', 'pending']):
        u = users[i % len(users)]
        r = type('AccountRecoveryRequest', (), {
            'id': i+1,
            'pk': i+1,
            'user': u,
            'reason': ['Perdi el acceso a mi cuenta', 'Me robaron el telefono', 'Ya recupere el acceso', 'Cuenta bloqueada'][i],
            'status': status,
            'admin_note': 'Verificado' if status == 'approved' else ('Solicitud duplicada' if status == 'rejected' else ''),
            'created_at': now - timedelta(days=i),
            'resolved_at': now - timedelta(days=i-1) if status != 'pending' else None,
        })()
        delta = now - r.created_at
        secs = int(delta.total_seconds())
        r.time_short = f'{max(1, secs // 60)} min' if secs < 3600 else (f'{secs // 3600} h' if secs < 86400 else f'{secs // 86400} d')
        requests.append(r)

    paginator = Paginator(requests, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    counts = {
        'all': len(requests),
        'pending': sum(1 for r in requests if r.status == 'pending'),
        'approved': sum(1 for r in requests if r.status == 'approved'),
        'rejected': sum(1 for r in requests if r.status == 'rejected'),
    }
    return render(request, 'core/admin_account_recovery_requests.html', {
        'requests': requests,
        'page_obj': page_obj,
        'counts': counts,
        'status_filter': 'all',
        'q': '',
        'qs_params': '',
    })


def admin_alias_request_resolve_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('admin_alias_requests')


def admin_account_recovery_request_resolve_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('admin_account_recovery_requests')


@require_POST
def admin_set_alias_quota_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('admin_user_detail', pk=pk)


@require_POST
def admin_toggle_alias_unlimited_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('admin_user_detail', pk=pk)


@require_POST
def admin_toggle_alias_view(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('admin_users')


def page_not_found_view(request, _exception=None):
    return render(request, '404.html', status=404)


def server_error_view(request):
    return render(request, '500.html', status=500)
