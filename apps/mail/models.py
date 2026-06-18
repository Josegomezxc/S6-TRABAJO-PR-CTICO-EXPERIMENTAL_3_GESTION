from django.db import models


class EmailMessage(models.Model):
    alias = models.ForeignKey('aliases.Alias', on_delete=models.CASCADE, related_name='emails')
    from_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    body_html_raw = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    has_attachment = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_path = models.CharField(max_length=500, blank=True)
    risk_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.subject} -> {self.alias.address}"

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Correo recibido'
        verbose_name_plural = 'Correos recibidos'


class SentEmail(models.Model):
    alias = models.ForeignKey('aliases.Alias', on_delete=models.CASCADE, related_name='sent_emails')
    to_email = models.CharField(max_length=2500)
    subject = models.CharField(max_length=255, blank=True)
    body_html = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    attachments_count = models.IntegerField(default=0)
    attachments_meta = models.JSONField(default=list, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.subject or '(sin asunto)'} -> {self.to_email}"

    class Meta:
        ordering = ['-sent_at']


class Draft(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='drafts')
    alias = models.ForeignKey('aliases.Alias', on_delete=models.SET_NULL, null=True, blank=True, related_name='drafts')
    to_email = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body_html = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']
