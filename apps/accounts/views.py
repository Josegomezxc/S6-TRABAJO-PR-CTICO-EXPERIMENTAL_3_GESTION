from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from .services.auth_service import authenticate_flexible, login_single_session
from .services.profile_service import get_user_initials, get_user_color
from apps.core.services.stats_service import profile_stats

#estas son las funciones
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_values = {'email': ''}

    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        form_values['email'] = identifier

        if not identifier or not password:
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'accounts/login.html', {'form_values': form_values})

        user = authenticate_flexible(request, identifier, password)

        if user is None:
            messages.error(request, 'Correo/usuario o contraseña incorrectos.')
            return render(request, 'accounts/login.html', {'form_values': form_values})

        if not user.is_active:
            messages.error(request, 'Esta cuenta esta desactivada.')
            return render(request, 'accounts/login.html', {'form_values': form_values})

        login_single_session(request, user)

        remember = (request.POST.get('remember') or '').lower() in ('on', '1', 'true', 'yes')
        if remember:
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)

        return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form_values': form_values})


def logout_view(request):
    logout(request)
    return redirect('login')


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_values = {'name': '', 'email': ''}
    field_errors = {'name': '', 'email': '', 'password': [], 'password2': ''}

    if request.method == 'POST':
        username = (request.POST.get('name', '') or '').strip()
        email = (request.POST.get('email', '') or '').strip().lower()
        password = request.POST.get('password', '') or ''
        password2 = request.POST.get('password2', '') or ''

        form_values['name'] = username
        form_values['email'] = email

        if not username:
            field_errors['name'] = 'El nombre de usuario es obligatorio.'
        elif len(username) < 2 or len(username) > 30:
            field_errors['name'] = 'El nombre debe tener entre 2 y 30 caracteres.'

        if not email:
            field_errors['email'] = 'El correo electronico es obligatorio.'
        elif User.objects.filter(email__iexact=email).exists():
            field_errors['email'] = 'Ya existe una cuenta con ese correo.'

        if not password:
            field_errors['password'] = ['La contrasena es obligatoria.']
        elif len(password) < 4:
            field_errors['password'] = ['La contrasena debe tener al menos 4 caracteres.']

        if password and password2 and password != password2:
            field_errors['password2'] = 'Las contrasenas no coinciden.'

        has_errors = any((
            field_errors['name'], field_errors['email'],
            field_errors['password'], field_errors['password2'],
        ))

        if not has_errors:
            user = User.objects.create_user(
                username=email.split('@')[0][:30] or email[:30],
                email=email,
                password=password,
                first_name=username,
            )
            user.is_active = True
            user.save()

            login_single_session(request, user)
            messages.success(request, 'Cuenta creada exitosamente. Bienvenido!')
            return redirect('dashboard')

    return render(request, 'accounts/register.html', {
        'form_values': form_values,
        'field_errors': field_errors,
    })


def verificar_correo_view(request, token):
    messages.info(request, 'La verificacion de correo no esta disponible en el prototipo.')
    return redirect('dashboard')


def reenviar_codigo_view(request, token):
    messages.info(request, 'La verificacion de correo no esta disponible en el prototipo.')
    return redirect('login')


def recuperar_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_values = {'email': ''}

    if request.method == 'POST':
        email = (request.POST.get('email', '') or '').strip().lower()
        form_values['email'] = email
        return render(request, 'accounts/recuperar.html', {
            'form_values': {'email': ''},
            'submitted': True,
            'sent_to': email,
        })

    return render(request, 'accounts/recuperar.html', {'form_values': form_values})


def reset_password_view(request, token):
    if request.user.is_authenticated:
        return redirect('dashboard')
    messages.error(request, 'El enlace ha expirado o no es valido.')
    return redirect('recuperar')


@login_required(login_url='login')
def perfil_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        if form_type == 'info':
            new_name = (request.POST.get('name', '') or '').strip()
            if new_name:
                request.user.first_name = new_name[:150]
                request.user.save(update_fields=['first_name'])
                messages.success(request, 'Nombre actualizado correctamente.')
            return redirect('perfil')
        if form_type == 'password':
            pwd = request.POST.get('password', '')
            pwd2 = request.POST.get('password2', '')
            if not pwd:
                messages.error(request, 'Ingresa una contrasena nueva.')
            elif pwd != pwd2:
                messages.error(request, 'Las contrasenas no coinciden.')
            elif len(pwd) < 4:
                messages.error(request, 'La contrasena debe tener al menos 4 caracteres.')
            else:
                request.user.set_password(pwd)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contrasena actualizada correctamente.')
            return redirect('perfil')

    ctx = profile_stats(request.user)
    ctx['avatar_initials'] = get_user_initials(request.user)
    ctx['avatar_color'] = get_user_color(request.user)
    return render(request, 'accounts/perfil.html', ctx)


@login_required(login_url='login')
def cambiar_password(request):
    if request.method == 'POST':
        pwd = request.POST.get('password', '')
        pwd2 = request.POST.get('password2', '')
        if not pwd:
            messages.error(request, 'Ingresa una contrasena nueva.')
        elif pwd != pwd2:
            messages.error(request, 'Las contrasenas no coinciden.')
        elif len(pwd) < 4:
            messages.error(request, 'La contrasena debe tener al menos 4 caracteres.')
        else:
            request.user.set_password(pwd)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contrasena actualizada correctamente!')
        return redirect('cambiar_password')

    return render(request, 'accounts/cambiar_password.html')


def account_recovery_request_view(request, user_id):
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('login')


@login_required(login_url='login')
def eliminar_cuenta_request_view(request):
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('perfil')


@login_required(login_url='login')
def eliminar_cuenta_confirmar_view(request):
    messages.info(request, 'Funcionalidad no disponible en el prototipo.')
    return redirect('perfil')
