from django.db import models


class SandboxAnalysis(models.Model):
    RISK_LEVELS = [
        ('safe', 'Seguro (0-30)'),
        ('warning', 'Sospechoso (31-60)'),
        ('danger', 'Alto riesgo (61-80)'),
        ('malware', 'Malware (81-100)'),
    ]
    CATEGORIES = [
        ('executable', 'Ejecutable'), ('office', 'Documento Office'),
        ('pdf', 'PDF'), ('archive', 'Archivo comprimido'),
        ('script', 'Script'), ('body', 'Cuerpo del correo'),
        ('url', 'URL'), ('aggregate', 'Agregado'), ('unknown', 'Desconocido'),
    ]

    email = models.OneToOneField('mail.EmailMessage', on_delete=models.CASCADE, related_name='analysis')
    filename = models.CharField(max_length=255)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='safe')
    threat_name = models.CharField(max_length=200, blank=True)
    blocked = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='unknown')
    real_mime_type = models.CharField(max_length=100, blank=True)
    sha256_hash = models.CharField(max_length=64, blank=True)
    md5_hash = models.CharField(max_length=32, blank=True)
    file_size = models.BigIntegerField(default=0)
    extension = models.CharField(max_length=20, blank=True)
    extension_spoof = models.BooleanField(default=False)
    yara_matches = models.JSONField(default=list, blank=True)
    evidence = models.JSONField(default=list, blank=True)
    iocs = models.JSONField(default=dict, blank=True)
    analyzers_run = models.JSONField(default=list, blank=True)
    body_score = models.IntegerField(default=0)
    body_evidence = models.JSONField(default=list, blank=True)
    body_threat = models.CharField(max_length=200, blank=True)
    attachments_reports = models.JSONField(default=list, blank=True)
    ai_verdict = models.CharField(max_length=20, blank=True)
    ai_threat_type = models.CharField(max_length=100, blank=True)
    ai_explanation = models.TextField(blank=True)
    ai_recommendation = models.TextField(blank=True)
    ai_generated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.filename} - {self.risk_score}/100"

    class Meta:
        ordering = ['-analyzed_at']
