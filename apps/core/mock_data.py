from datetime import timedelta
from django.utils import timezone
from apps.aliases.models import Alias
from apps.mail.models import EmailMessage, SentEmail, Draft
from apps.sandbox.models import SandboxAnalysis
from apps.notifications.models import Notification
from apps.accounts.models import AccountRecoveryRequest
from apps.aliases.models import AliasQuotaRequest
from django.contrib.auth.models import User


def get_mock_alias(user):
    alias, _ = Alias.objects.get_or_create(
        address='demo@prototype.local',
        defaults={'user': user, 'label': 'Demo', 'is_active': True}
    )
    return alias


def get_mock_aliases(user):
    aliases = list(Alias.objects.filter(user=user))
    if not aliases:
        alias = get_mock_alias(user)
        aliases = [alias]
    return aliases


def get_mock_emails(user, limit=6):
    alias = get_mock_alias(user)
    now = timezone.now()
    emails = []
    subjects = [
        ('soporte@netflix.com', 'Tu factura de Netflix - Mayo 2026', 0, True),
        ('no-reply@paypal.com', 'Alerta de seguridad importante', 85, True),
        ('newsletter@github.com', 'GitHub Changelog #245', 0, False),
        ('phishing@malicioso.com', 'Verifica tu cuenta urgente', 92, True),
        ('amazon@amazon.com', 'Tu paquete fue enviado', 0, False),
        ('alerta@banco.com', 'Intento de acceso detectado', 75, True),
    ]
    for i, (from_e, subj, score, has_att) in enumerate(subjects):
        e = EmailMessage(
            id=i+1,
            alias=alias,
            from_email=from_e,
            subject=subj,
            body=f'Contenido del correo: {subj}',
            body_html=f'<p>Contenido: {subj}</p>',
            received_at=now - timedelta(hours=i),
            read=(i > 2),
            has_attachment=has_att,
            attachment_name='factura.pdf' if has_att else '',
            risk_score=score,
        )
        if has_att:
            analysis = SandboxAnalysis(pk=i+1)
            e.analysis_id = analysis.pk
            e.__dict__['analysis'] = analysis
        emails.append(e)
    return emails[:limit]


def get_mock_sent_emails(user, limit=6):
    alias = get_mock_alias(user)
    now = timezone.now()
    sent = []
    for i in range(limit):
        s = SentEmail(
            id=i+1,
            alias=alias,
            to_email='destinatario@example.com',
            subject=f'Correo enviado #{i+1}',
            body_html='<p>Mensaje de prueba</p>',
            sent_at=now - timedelta(hours=i),
            attachments_count=i % 3,
            attachments_meta=[{'filename': f'archivo_{i}.pdf', 'size': 1024, 'type': 'application/pdf'}] if i % 3 > 0 else [],
        )
        sent.append(s)
    return sent


def get_mock_drafts(user, limit=6):
    alias = get_mock_alias(user)
    now = timezone.now()
    drafts = []
    for i in range(limit):
        d = Draft(
            id=i+1,
            user=user,
            alias=alias,
            to_email='pendiente@example.com' if i > 0 else '',
            subject=f'Borrador #{i+1}',
            body_html='<p>Escribiendo...</p>',
            updated_at=now - timedelta(hours=i),
        )
        drafts.append(d)
    return drafts


def get_mock_trash(user):
    items = []
    now = timezone.now()
    alias = get_mock_alias(user)
    for i in range(3):
        em = EmailMessage(
            id=100+i,
            alias=alias,
            from_email='spam@example.com',
            subject=f'Correo eliminado #{i+1}',
            received_at=now - timedelta(days=i),
            deleted_at=now - timedelta(hours=i),
            read=True,
            risk_score=30,
        )
        em.kind = 'inbound'
        em.expires_at = now + timedelta(days=25)
        items.append(em)
    return items


def get_mock_sandbox_analyses(user, limit=6):
    alias = get_mock_alias(user)
    now = timezone.now()
    data = [
        dict(filename='documento.pdf', risk_score=0, risk_level='safe', threat_name='', category='pdf', real_mime='application/pdf', ext='.pdf', spoof=False, yara=[], evidence=[], iocs={}, analyzers=['static'], blocked=False),
        dict(filename='malware.exe', risk_score=85, risk_level='malware', threat_name='Trojan.Generic', category='executable', real_mime='application/x-msdownload', ext='.exe', spoof=False, yara=[{'rule':'PowerShell_Loader','severity':'critical'}], evidence=[{'type':'yara','detail':'YARA PowerShell_Loader: Detected IEX+DownloadString','severity':'critical'}], iocs={'urls':['http://malware.example.com'],'ips':['185.234.56.78']}, analyzers=['static','dynamic','yara','body'], blocked=True),
        dict(filename='phishing.doc', risk_score=65, risk_level='danger', threat_name='Phishing.Bank', category='office', real_mime='application/msword', ext='.doc', spoof=True, yara=[{'rule':'PowerShell_Loader','severity':'critical'}], evidence=[{'type':'url','detail':'URL sospechosa: http://bit.ly/phishing-bank','severity':'high'}], iocs={'urls':['http://bit.ly/phishing-bank'],'ips':[]}, analyzers=['static','dynamic','yara','body'], blocked=True),
        dict(filename='virus.bat', risk_score=92, risk_level='malware', threat_name='Ransomware.Locky', category='script', real_mime='text/x-bat', ext='.bat', spoof=False, yara=[{'rule':'PowerShell_Loader','severity':'critical'}], evidence=[{'type':'dynamic','detail':'Intento de conexion a IP 185.234.56.78:4444','severity':'critical'}], iocs={'urls':[],'ips':['185.234.56.78']}, analyzers=['static','dynamic','yara','body'], blocked=True),
        dict(filename='informe.xlsx', risk_score=45, risk_level='warning', threat_name='', category='office', real_mime='application/vnd.ms-excel', ext='.xlsx', spoof=False, yara=[], evidence=[{'type':'info','detail':'Documento Office con macros detectadas','severity':'medium'}], iocs={}, analyzers=['static','yara'], blocked=False),
        dict(filename='foto.png', risk_score=15, risk_level='safe', threat_name='', category='unknown', real_mime='image/png', ext='.png', spoof=False, yara=[], evidence=[], iocs={}, analyzers=['static','yara'], blocked=False),
    ]
    analyses = []
    for i in range(limit):
        d = data[i % len(data)]
        a = SandboxAnalysis(
            id=i+1,
            email=EmailMessage(id=i+1, alias=alias, from_email=f'remitente{i}@example.com', subject=f'Analisis #{i+1}', body='test', risk_score=d['risk_score']),
            filename=d['filename'], risk_score=d['risk_score'], risk_level=d['risk_level'],
            threat_name=d['threat_name'], category=d['category'], real_mime_type=d['real_mime'],
            sha256_hash=f'abc{i}'*16, md5_hash=f'def{i}'*8,
            file_size=[2048,65536,32768,1024,16384,512000][i%6],
            extension=d['ext'], extension_spoof=d['spoof'],
            yara_matches=d['yara'], evidence=d['evidence'], iocs=d['iocs'],
            analyzers_run=d['analyzers'], body_score=0, body_evidence=[], body_threat='',
            analyzed_at=now - timedelta(hours=i), blocked=d['blocked'],
        )
        analyses.append(a)
    return analyses


def get_mock_notifications(user, limit=6):
    now = timezone.now()
    notifs = []
    for i in range(limit):
        n = Notification(
            id=i+1,
            user=user,
            type=['system', 'threat_alert', 'forwarded', 'system', 'threat_alert', 'system'][i],
            title=[
                'Bienvenido a DockerShield',
                'Amenaza bloqueada: Phishing detectado',
                'Correo reenviado a tu bandeja',
                'Alias creado correctamente',
                'Malware detectado en adjunto',
                'Cupo de alias actualizado'
            ][i],
            message=[
                'Tu cuenta fue creada exitosamente.',
                'Se bloqueo un intento de phishing desde PayPal.',
                'El correo seguro fue reenviado a tu correo real.',
                'Tu alias "Demo" esta listo para usarse.',
                'Se detecto malware en un archivo adjunto.',
                'El administrador ajusto tu cupo de alias.'
            ][i],
            read=(i > 1),
            status='done',
            created_at=now - timedelta(hours=i),
        )
        notifs.append(n)
    return notifs


def get_mock_quota_requests(user):
    now = timezone.now()
    requests = []
    for i, status in enumerate(['pending', 'approved', 'rejected', 'pending']):
        req_user = user
        r = AliasQuotaRequest(
            id=i+1,
            user=req_user,
            requested_amount=[5, 10, 3, 8][i],
            reason=['Necesito mas alias para mi equipo', 'Proyecto nuevo en desarrollo', 'Ya no necesito tantos', 'Campaña de email marketing'][i],
            status=status,
            admin_note='Aprobado' if status == 'approved' else ('Demasiados alias inactivos' if status == 'rejected' else ''),
            granted_amount=[0, 10, 0, 0][i],
            created_at=now - timedelta(days=i),
            resolved_at=now - timedelta(days=i-1) if status != 'pending' else None,
        )
        delta = now - r.created_at
        secs = int(delta.total_seconds())
        if secs < 3600: r.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: r.time_short = f'{secs // 3600} h'
        else: r.time_short = f'{secs // 86400} d'
        requests.append(r)
    return requests


def get_mock_account_recovery_requests():
    from django.contrib.auth.models import User
    now = timezone.now()
    requests = []
    users = list(User.objects.all()) or [type('User', (), {'pk': 1, 'email': 'demo@example.com', 'username': 'demo', 'get_full_name': lambda self: 'Demo User'})()]
    for i, status in enumerate(['pending', 'approved', 'rejected', 'pending']):
        u = users[i % len(users)]
        r = AccountRecoveryRequest(
            id=i+1,
            user=u,
            reason=['Perdi el acceso a mi cuenta', 'Me robaron el telefono', 'Ya recupere el acceso', 'Cuenta bloqueada por error'][i],
            status=status,
            admin_note='Verificado' if status == 'approved' else ('Solicitud duplicada' if status == 'rejected' else ''),
            created_at=now - timedelta(days=i),
            resolved_at=now - timedelta(days=i-1) if status != 'pending' else None,
        )
        delta = now - r.created_at
        secs = int(delta.total_seconds())
        if secs < 3600: r.time_short = f'{max(1, secs // 60)} min'
        elif secs < 86400: r.time_short = f'{secs // 3600} h'
        else: r.time_short = f'{secs // 86400} d'
        requests.append(r)
    return requests


def get_mock_all_users():
    users = list(User.objects.all())
    return users


def get_mock_active_aliases(user):
    return get_mock_aliases(user)
