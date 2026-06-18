from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email_verified = models.BooleanField(default=True)
    alias_quota_extra = models.IntegerField(default=0)
    alias_unlimited = models.BooleanField(default=False)
    current_session_key = models.CharField(max_length=40, blank=True, default='')
    session_last_activity = models.DateTimeField(null=True, blank=True)
    forward_safe_emails = models.BooleanField(default=False)
    last_toast_notif_id = models.PositiveBigIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.email or self.user.username}"

    @property
    def has_avatar(self):
        return bool(self.avatar and self.avatar.name)

    @property
    def avatar_url(self):
        try:
            if self.avatar and self.avatar.name:
                return self.avatar.url
        except ValueError:
            pass
        return ''


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return not self.used_at and not self.is_expired

    def mark_used(self):
        from django.utils import timezone
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])


class EmailVerificationCode(models.Model):
    PURPOSE_CHOICES = [
        ('register', 'Verificación de registro'),
        ('delete_account', 'Confirmar eliminación de cuenta'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_codes')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='register')
    code = models.CharField(max_length=6, db_index=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.used_at and timezone.now() < self.expires_at and self.attempts < 5


class PendingRegistration(models.Model):
    email = models.EmailField(db_index=True)
    first_name = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=128)
    code = models.CharField(max_length=6, db_index=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.used_at and timezone.now() < self.expires_at and self.attempts < 5


class AccountRecoveryRequest(models.Model):
    STATUS = [('pending', 'Pendiente'), ('approved', 'Aprobada'), ('rejected', 'Rechazada')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_recovery_requests')
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    admin_note = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_account_recovery_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
