import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone


from apps.core.mock_data import get_mock_sandbox_analyses


PAGE_SIZE = 6


@login_required(login_url='login')
def sandbox_list_view(request):
    analyses = get_mock_sandbox_analyses(request.user, 12)
    counts = {
        'all': len(analyses),
        'malware': sum(1 for a in analyses if a.risk_score >= 81),
        'danger': sum(1 for a in analyses if 61 <= a.risk_score < 81),
        'warning': sum(1 for a in analyses if 30 < a.risk_score < 61),
        'safe': sum(1 for a in analyses if a.risk_score <= 30),
    }

    now = timezone.now()
    for a in analyses:
        delta = now - a.analyzed_at
        secs = int(delta.total_seconds())
        if secs < 45: a.time_short = 'ahora'
        elif secs < 3600: a.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: a.time_short = f'{secs // 3600} h'
        elif secs < 86400 * 7: a.time_short = f'{secs // 86400} d'
        else: a.time_short = f'{secs // (86400*7)} sem'

    paginator = Paginator(analyses, PAGE_SIZE)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'sandbox/sandbox_list.html', {
        'page_obj': page_obj,
        'counts': counts,
        'q': '',
        'filter': 'all',
        'qs_params': '',
        'total_count': counts['all'],
        'blocked_count': counts['danger'] + counts['malware'],
        'safe_count': counts['safe'],
        'warning_count': counts['warning'],
    })


@login_required(login_url='login')
def sandbox_analyze_view(request, email_id):
    return render(request, 'sandbox/sandbox_list.html', {'analyses': [], 'counts': {}, 'q': '', 'filter': 'all'})


@login_required(login_url='login')
def sandbox_report_view(request, pk):
    analyses = get_mock_sandbox_analyses(request.user)
    analysis = next((a for a in analyses if a.id == pk), None)
    if not analysis:
        analysis = get_mock_sandbox_analyses(request.user, 1)[0]

    yara_context = []
    for match in (analysis.yara_matches or [])[:10]:
        if isinstance(match, dict):
            yara_context.append({
                'rule': match.get('rule', ''),
                'desc': '',
                'category': '',
                'severity': match.get('severity', ''),
                'strings': [],
            })

    return render(request, 'sandbox/sandbox_report.html', {
        'analysis': analysis,
        'yara_context_json': json.dumps(yara_context, ensure_ascii=False),
    })


@login_required(login_url='login')
def ai_analysis_view(request):
    return JsonResponse({
        'result': 'VEREDICTO: SEGURO\n\nTIPO DE AMENAZA: No aplica\n\nEXPLICACION: Este es un prototipo. No se realizo analisis IA real.\n\nRECOMENDACION: Prototipo - sin analisis real.',
        'cached': False,
    })
