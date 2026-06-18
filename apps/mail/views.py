import json
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from apps.aliases.models import Alias
from apps.core.mock_data import (
    get_mock_emails, get_mock_sent_emails, get_mock_drafts,
    get_mock_trash, get_mock_sandbox_analyses, get_mock_alias,
)
from apps.core.services.stats_service import dashboard_stats
from apps.mail.models import EmailMessage, SentEmail, Draft


PAGE_SIZE = 6


@login_required(login_url='login')
def dashboard_view(request):
    stats = dashboard_stats(request.user)
    alias = get_mock_alias(request.user)
    aliases = [alias]
    now = timezone.now()

    recent_emails = get_mock_emails(request.user, 20)
    for em in recent_emails:
        delta = now - em.received_at
        secs = int(delta.total_seconds())
        if secs < 45: em.time_short = 'ahora'
        elif secs < 3600: em.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: em.time_short = f'{secs // 3600} h'
        elif secs < 86400 * 7: em.time_short = f'{secs // 86400} d'
        else: em.time_short = f'{secs // (86400*7)} sem'

    recent_analyses = get_mock_sandbox_analyses(request.user, 3)
    for an in recent_analyses:
        delta = now - an.analyzed_at
        secs = int(delta.total_seconds())
        if secs < 45: an.time_short = 'ahora'
        elif secs < 3600: an.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: an.time_short = f'{secs // 3600} h'
        elif secs < 86400 * 7: an.time_short = f'{secs // 86400} d'
        else: an.time_short = f'{secs // (86400*7)} sem'

    recent_threats = [e for e in recent_emails if e.risk_score >= 61][:3]

    risk_distribution = {'safe': 30, 'susp': 5, 'threats': 7}
    activity_14d = [{'label': f'{(now - timedelta(days=13-i)).strftime("%d/%m")}', 'count': max(0, 3 - (13-i) % 5 + (i % 3))} for i in range(14)]

    return render(request, 'mail/dashboard.html', {
        'aliases': aliases,
        'recent_emails': recent_emails[:20],
        'recent_analyses': recent_analyses[:3],
        'recent_threats': recent_threats,
        'risk_distribution': risk_distribution,
        'activity_14d': activity_14d,
        **stats,
    })


@login_required(login_url='login')
def inbox_view(request):
    emails = get_mock_emails(request.user, 25)
    counts = {
        'all': len(emails),
        'unread': sum(1 for e in emails if not e.read),
        'attachment': sum(1 for e in emails if e.has_attachment),
        'danger': sum(1 for e in emails if e.risk_score >= 61),
        'safe': sum(1 for e in emails if 0 < e.risk_score <= 30),
    }

    now = timezone.now()
    for em in emails:
        delta = now - em.received_at
        secs = int(delta.total_seconds())
        if secs < 45: em.time_short = 'ahora'
        elif secs < 3600: em.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: em.time_short = f'{secs // 3600} h'
        elif secs < 86400 * 7: em.time_short = f'{secs // 86400} d'
        else: em.time_short = f'{secs // (86400*7)} sem'

    paginator = Paginator(emails, PAGE_SIZE)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'mail/inbox.html', {
        'page_obj': page_obj,
        'counts': counts,
        'q': '',
        'filter': 'all',
        'qs_params': '',
    })


@login_required(login_url='login')
def mark_email_read_api(request, pk):
    return JsonResponse({"ok": True, "unread_count": 0, "notif_unread_count": 0})


@login_required(login_url='login')
def email_html_api(request, pk):
    return HttpResponseNotFound("not_found")


@login_required(login_url='login')
def inbox_clear_api(request):
    return JsonResponse({'ok': True, 'deleted': 0, 'trashed': True})


SENT_BATCH = 6


@login_required(login_url='login')
def sent_view(request):
    sent_emails = get_mock_sent_emails(request.user, SENT_BATCH)
    groups = _group_sent_by_date(sent_emails)
    active_aliases = get_mock_emails(request.user)

    return render(request, 'mail/sent.html', {
        'sent_emails': sent_emails,
        'sent_groups': groups,
        'total_sent': len(sent_emails),
        'has_more': False,
        'next_offset': len(sent_emails),
        'batch_size': SENT_BATCH,
        'active_aliases': active_aliases,
        'attach_count': 3,
        'scheduled_count': 1,
    })


def _group_sent_by_date(emails):
    today = timezone.now().date()
    yday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    groups = [
        {"label": "Hoy", "emails": []},
        {"label": "Ayer", "emails": []},
        {"label": "Esta semana", "emails": []},
        {"label": "Anteriores", "emails": []},
    ]
    for em in emails:
        d = em.sent_at.date()
        if d == today: groups[0]["emails"].append(em)
        elif d == yday: groups[1]["emails"].append(em)
        elif d > week_ago: groups[2]["emails"].append(em)
        else: groups[3]["emails"].append(em)
    return [g for g in groups if g["emails"]]


@login_required(login_url='login')
def sent_more_api(request):
    return JsonResponse({'ok': True, 'html': '', 'count': 0, 'next_offset': 0, 'has_more': False})


@login_required(login_url='login')
def sent_empty_api(request):
    return JsonResponse({'ok': True, 'moved': 0})


@login_required(login_url='login')
def compose_contacts_api(request):
    return JsonResponse({'ok': True, 'results': []})


TRASH_RETENTION_DAYS = 30
TRASH_BATCH = 6


@login_required(login_url='login')
def email_trash_api(request, pk):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def sent_trash_api(request, pk):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def trash_restore_api(request):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def trash_delete_api(request):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def trash_empty_api(request):
    return JsonResponse({'ok': True, 'deleted': 0, 'inbound': 0, 'outbound': 0, 'drafts': 0})


@login_required(login_url='login')
def trash_view(request):
    all_trash = get_mock_trash(request.user)
    return render(request, 'mail/trash.html', {
        'all_trash': all_trash,
        'inbound_trash': all_trash,
        'outbound_trash': [],
        'drafts_trash': [],
        'total_trash': len(all_trash),
        'retention_days': TRASH_RETENTION_DAYS,
        'has_more': False,
        'next_offset': len(all_trash),
        'batch_size': TRASH_BATCH,
    })


@login_required(login_url='login')
def trash_more_api(request):
    return JsonResponse({'ok': True, 'html': '', 'count': 0, 'next_offset': 0, 'has_more': False})


@login_required(login_url='login')
def draft_save_api(request):
    return JsonResponse({'ok': True, 'draft_id': None})


@login_required(login_url='login')
def draft_get_api(request, pk):
    from apps.core.mock_data import get_mock_drafts
    drafts = get_mock_drafts(request.user, 12)
    draft = next((d for d in drafts if d.id == pk), None)
    if not draft:
        return JsonResponse({'ok': False, 'error': 'not_found'}, status=404)
    alias = draft.alias
    return JsonResponse({
        'ok': True,
        'draft': {
            'id': draft.id,
            'to': draft.to_email,
            'subject': draft.subject,
            'body_html': draft.body_html,
            'alias_id': alias.id,
            'alias_address': alias.address,
            'alias_label': alias.label,
            'alias_active': alias.is_active,
        },
    })


@login_required(login_url='login')
def draft_delete_api(request, pk):
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def drafts_empty_api(request):
    return JsonResponse({'ok': True, 'moved': 0})


DRAFTS_BATCH = 6


@login_required(login_url='login')
def drafts_view(request):
    drafts = get_mock_drafts(request.user, DRAFTS_BATCH)
    return render(request, 'mail/drafts.html', {
        'drafts': drafts,
        'total_drafts': len(drafts),
        'no_recipient_count': 1,
        'scheduled_count': 0,
        'has_more': False,
        'next_offset': len(drafts),
        'batch_size': DRAFTS_BATCH,
    })


@login_required(login_url='login')
def drafts_more_api(request):
    return JsonResponse({'ok': True, 'html': '', 'count': 0, 'next_offset': 0, 'has_more': False})
