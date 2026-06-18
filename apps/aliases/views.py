from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Alias
from apps.core.mock_data import get_mock_aliases


ALIAS_LIMIT_PER_USER = 5
ALIAS_BATCH = 6


@login_required(login_url='login')
def alias_list_view(request):
    aliases = get_mock_aliases(request.user)
    active_count = sum(1 for a in aliases if a.is_active)
    destroyed_count = len(aliases) - active_count
    total_emails = 15
    total_threats = 4

    return render(request, 'aliases/alias.html', {
        'aliases': aliases,
        'active_count': active_count,
        'destroyed_count': destroyed_count,
        'quota_used': len(aliases),
        'total_emails': total_emails,
        'total_threats': total_threats,
        'alias_limit': ALIAS_LIMIT_PER_USER,
        'alias_remaining': max(0, ALIAS_LIMIT_PER_USER - len(aliases)),
        'is_unlimited': False,
        'pending_request': None,
        'has_more': False,
        'next_offset': len(aliases),
        'batch_size': ALIAS_BATCH,
    })


@login_required(login_url='login')
def alias_more_api(request):
    return JsonResponse({'ok': True, 'html': '', 'count': 0, 'next_offset': 0, 'has_more': False})


@login_required(login_url='login')
def alias_create_view(request):
    if request.method == 'POST':
        import secrets
        label = 'demo-' + secrets.token_hex(3)
        address = f'{label}@prototype.local'
        Alias.objects.create(
            user=request.user,
            label=label,
            address=address,
        )
        messages.success(request, f'Alias creado: {address}')
    return redirect('alias_list')


@login_required(login_url='login')
def alias_destroy_view(request, pk):
    alias = get_object_or_404(Alias, pk=pk, user=request.user)
    if request.method == 'POST':
        alias.is_active = False
        alias.save()
        messages.success(request, f'Alias {alias.address} destruido.')
    return redirect('alias_list')


@login_required(login_url='login')
def alias_compose_view(request, pk):
    return JsonResponse({
        'ok': True,
        'message': 'Correo enviado (prototipo)',
    })


@login_required(login_url='login')
def alias_quota_request_create(request):
    return JsonResponse({
        'ok': False,
        'error': 'Funcionalidad no disponible en el prototipo.',
    }, status=400)
