from django.db import models
from django.contrib.auth.models import User


class Alias(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aliases')
    label = models.CharField(max_length=100)
    address = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    destroyed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.address} ({self.label})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alias'
        verbose_name_plural = 'Alias'


class AliasQuotaRequest(models.Model):
    STATUS = [('pending', 'Pendiente'), ('approved', 'Aprobada'), ('rejected', 'Rechazada')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alias_quota_requests')
    requested_amount = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    admin_note = models.TextField(blank=True)
    granted_amount = models.PositiveIntegerField(default=0)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alias_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
