from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPES = [
        ('forward_request', 'Pendiente de aprobacion'),
        ('forwarded', 'Reenviado'),
        ('threat_alert', 'Amenaza bloqueada'),
        ('system', 'Sistema'),
    ]
    STATUSES = [
        ('pending', 'Pendiente'), ('approved', 'Aprobada'),
        ('discarded', 'Descartada'), ('expired', 'Expirada'), ('done', 'Completada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    related_email = models.ForeignKey('mail.EmailMessage', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUSES, default='done')
    created_at = models.DateTimeField(auto_now_add=True)
    actioned_at = models.DateTimeField(null=True, blank=True)
    target_url = models.CharField(max_length=300, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} -> {self.user.email} ({self.title[:40]})"

    @property
    def is_actionable(self):
        return self.type == 'forward_request' and self.status == 'pending'
